#!/opt/elasticbeanstalk/lib/ruby/bin/ruby
#encoding: utf-8

# Copyright 2015-2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under the License.

require 'json'
require 'open3'
require 'aws-sdk'
require 'open-uri'
require 'fileutils'
require 'net/http'

# get the region that the instance is running in
# $region = JSON.parse(URI.open('http://169.254.169.254/latest/dynamic/instance-identity/document').read)["region"]
$region = "ap-south-1"

# create a new DynamoDB client
$ddb = Aws::DynamoDB::Client.new({ region: $region })

def main
  # Nginx configuration source path, for logging purposes if needed by run_build.sh, but not modified here.
  nginx_config_source_path = ".platform/nginx/nginx.conf"

  # read environment variables using the get-config utility
  env_vars = JSON.parse(%x(/opt/elasticbeanstalk/bin/get-config environment))

  # read the Elastic Beanstalk deployment manifest
  dep_manifest = JSON.parse(File.read('/tmp/manifest'))

  # read the private IP of the instance from the metadata service
  # Step 1: Get the session token
  token_uri = URI("http://169.254.169.254/latest/api/token")
  token_req = Net::HTTP::Put.new(token_uri)
  token_req['X-aws-ec2-metadata-token-ttl-seconds'] = "21600"

  token_res = Net::HTTP.start(token_uri.host) do |http|
    http.request(token_req)
  end

  token = token_res.body

  # Step 2: Use token to get local IPv4 address
  ip_uri = URI("http://169.254.169.254/latest/meta-data/local-ipv4")
  ip_req = Net::HTTP::Get.new(ip_uri)
  ip_req['X-aws-ec2-metadata-token'] = token

  ip_res = Net::HTTP.start(ip_uri.host) do |http|
    http.request(ip_req)
  end

  private_ip = ip_res.body
  
  eb_env_name = env_vars["EB_ENV_NAME"]
  master_ip_table = env_vars["MASTER_IP_TABLE"]
  deployment_id = dep_manifest["DeploymentId"]

  is_master = write_master_ip(master_ip_table, eb_env_name, private_ip, deployment_id, token)

  puts "We are " + (is_master ? "master" : "follower")

  if is_master
    File.open('.master', "w") { |f| f.print "true" }
    File.open('.masterIP', "w") { |f| f.print "127.0.0.1" } # Master uses localhost for its own services
    puts "Master setup complete. .master and .masterIP files created."
    puts "Nginx source config at #{nginx_config_source_path} will be used by the platform for master."
  else # Follower instance
    File.delete('.master') if File.exist?('.master')
    master_ip = get_master_ip(master_ip_table, eb_env_name)

    if master_ip
      File.open('.masterIP', "w") { |f| f.print "#{master_ip}" }
      puts "Follower setup: .masterIP file created with Master IP: #{master_ip}."
      puts "Nginx modification for follower will be handled by platform hook using .masterIP."
    else
      puts "ERROR: Could not get master IP from DynamoDB table. Follower setup incomplete for .masterIP. EXITING."
      exit 1 # Exit if master IP can't be found, as .masterIP is critical for the hook
    end
  end
end

def run_command(command)
  output, status = Open3.capture2e(command)
  puts "#{command}"
  if output.length > 0
    puts "Output:\n#{output}"
  end
  return status.success?
end

def get_num_instances_in_environment(env_name)
  begin
    eb = Aws::ElasticBeanstalk::Client.new({ region: $region })
    resp = eb.describe_environment_resources(:environment_name => env_name)
    if resp && resp.environment_resources && resp.environment_resources.instances
      return resp.environment_resources.instances.count
    else 
      puts "No instances found or unexpected response for #{env_name}"
      return 0
    end
  rescue Exception => e
    puts "Error retrieving number of instances in #{env_name}: #{e.message}"
    return 0 
  end
end

def write_master_ip(table_name, key, ip, deployment_id, token)
  begin
    update_time = Time.now()
    id_uri = URI("http://169.254.169.254/latest/meta-data/instance-id")
    id_req = Net::HTTP::Get.new(id_uri)
    id_req['X-aws-ec2-metadata-token'] = token
    id_res = Net::HTTP.start(id_uri.host) { |http| http.request(id_req) }
    instance_id = id_res.body

    num_instances = get_num_instances_in_environment(key)
    # Consider adding a check here: if num_instances is 0 or unexpectedly low, handle error.

    $ddb.update_item(
      :table_name => table_name,
      :key => { :HashKey => key },
      :update_expression => "SET IP = :val, ChangedAt = :time, ReadCount = :rc, " \
                           "DeploymentID = :dep_id, InstanceID = :inst_id",
      :condition_expression => "attribute_not_exists(DeploymentID) OR DeploymentID < :dep_id",
      :expression_attribute_values => {
        ":rc" => 0,
        ":val" => ip,
        ":time" => update_time.to_s,
        ":inst_id" => instance_id,
        ":dep_id" => deployment_id
      }
    )
    return true
  rescue Aws::DynamoDB::Errors::ConditionalCheckFailedException
    puts "Conditional check failed when writing master IP."
    return false
  rescue Exception => e
    puts "Error writing master IP to #{table_name}: #{e.class} - #{e.message}\nBacktrace: #{e.backtrace.join("\n")}"
    return false 
  end
end

def get_master_ip(table_name, key)
  5.downto(1) do |retries|
    begin
      sleep(3 * (5 - retries))
      puts "Read Attempt #{6 - retries} for master IP from #{table_name}"
      item_output = $ddb.get_item(
        :table_name => table_name,
        :key => { :HashKey => key }
      )
      item = item_output.item
      if item && item["IP"]
        puts "Master IP found: #{item["IP"]}"
        begin
          $ddb.update_item(
            :table_name => table_name,
            :key => { :HashKey => key },
            :update_expression => "ADD ReadCount :val",
            :expression_attribute_values => {":val" => 1}
          )
        rescue Exception => e_update
          puts "Error updating ReadCount for master IP: #{e_update.message}"
        end
        return item["IP"]
      else
        puts "Master IP not found or item malformed in attempt #{6-retries}. Item: #{item.inspect if item}"
      end
    rescue Exception => e
      puts "Error reading master IP from #{table_name} in attempt #{6-retries}: #{e.class} - #{e.message}"
    end
  end
  puts "Failed to get master IP after all retries."
  return nil
end

main if __FILE__==$0
