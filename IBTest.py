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

import os
import string
import random
import sys
import logging
import json
import datetime

from locust import HttpLocust, task, between
from threading import Timer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info('INIT')

#test data
global test_id
test_id = '3d616fd585'

problem_ids = [1, 50]
problem_language_id_map = {
    1: [4, 11, 27, 35, 39, 42, 43, 44, 55, 114, 116, 510, 511, 512],
    50: [4, 11, 27, 35, 39, 42, 43, 44, 55, 114, 116, 510, 511, 512]
}

random_matrix = [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]

problem_codes = {
    1: [
        'syntax error',
        'public class Solution {public int canCompleteCircuit(final List<Integer> gas, final List<Integer> cost) {return 1;}}',
        'public class Solution {public int canCompleteCircuit(final List<Integer> gas, final List<Integer> cost) {int currentFuel = 0;int remaining = 0;int total = 0;int start = 0;for(int i = 0; i < gas.size(); i++){remaining = gas.get(i) - cost.get(i);if(currentFuel >= 0)currentFuel += remaining;else{currentFuel = remaining;start = i;}total += remaining;}return total >= 0 ? start : -1;}}'
        ],
    50: [
        'syntax error',
        'public class Solution {public ArrayList<Integer> slidingMaximum(final List<Integer> a, int b) {ArrayList<Integer> result = new ArrayList<>(); return result;}}',
        'public class Solution {public ArrayList<Integer> slidingMaximum(final List<Integer> a, int b) {ArrayList<Integer> result = new ArrayList<>();Deque<Integer> dq = new LinkedList<>();        for(int i=0; i<b; i++){while(!dq.isEmpty()&& a.get(dq.peekLast())<a.get(i))dq.pollLast();dq.offerLast(i);                }for(int i = b ; i<a.size() ; i++){result.add(a.get(dq.peekFirst()));int currWindowStartIndex = i-b+1;while(!dq.isEmpty() && dq.peek()<currWindowStartIndex)dq.pollFirst();while(!dq.isEmpty()&& a.get(dq.peekLast())<a.get(i))dq.pollLast();dq.offerLast(i);  }result.add(a.get(dq.peekFirst()));return result;}}'
        ]
}

def signup(l):
    random_user = random.randint(1,sys.maxsize)
    response = l.client.post("/test/a/load_test/", {
        "candidate_email": "loadtestinterviewbit+" + str(random_user) +  "@gmail.com",
        "password": '12ABXYZ12',
         "candidate_name": str(random_user),
         "candidate_city": "Random",
         "candidate_branch": "candidate_branch",
         "candidate_degree": "candidate_degree",
         "candidate_university": "candidate_university",
         "candidate_contact_number": "9923704608"
         })

    l.client.post( "/test/" + test_id + '/' + "save-candidate-details",{
        "candidate_email": "loadtestinterviewbit+" + str(random_user) +  "@gmail.com",
        "password": '12ABXYZ12',
         "candidate_name": str(random_user),
         "candidate_city": "Random",
         "candidate_branch": "candidate_branch",
         "candidate_degree": "candidate_degree",
         "candidate_university": "candidate_university",
         "candidate_contact_number": "9923704608",
         "disclaimer": "on",
         "slug": "dkjhfkdfjhg"
     })

def login(l):
    l.client.post("/users/sign_in/", {"user[email]":"abhimanyu@interviewbit.com", "user[password]":"12!@abAB<>"})

def logout(l):
    l.client.post("/users/sign_out/", {"_method":"delete"})

def check_status(l, test_id, problem_id, submission_id):
    response = l.client.get("/test/" + str(test_id) + "/status/?problem_id=" + str(problem_id) + "&submission_id=" + str(submission_id))

# class MyTaskSet(task):
    
#     def on_start(self):
#         signup(self)

#     def on_stop(self):
#         logout(self)

#     #open the test programming_language_id
#     @task(6)
#     def index(self):    
#         response = self.client.get("/test/" + test_id + '/')

#     #record event
#     @task(33)
#     def record_event(self):
#         response = self.client.post("/test/" + test_id + '/record-event/',{
#             "event_type": "jhsdfgjdsf",
#             "event_value": "kjdkjdhfgkjdfhgifderiuy eiruty idufgy difuyg",
#             "timestamp": datetime.datetime.now()
#         })

#     #mark problem opened
#     @task(13)
#     def mark_problem_opened(self):
#         problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
#         response = self.client.post("/test/" + str(test_id) + "/mark-problem-opened/",{
#             "problem_id": problem_id
#         })

#     #get live problems
#     @task(6)
#     def get_live_problems(self):
#         response = self.client.get("/test/" + str(test_id) + "/live-problems/")

#     #fetch code
#     @task(22)
#     def fetch_code(self):    
#         problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
#         supported_languages = problem_language_id_map[problem_id]
#         programming_language_id = supported_languages[random.randint(0,(len(supported_languages) - 1))]
#         response = self.client.get("/test/" + str(test_id) + "/get-code/?programming_language_id=" + str(programming_language_id) + "&problem_id=" + str(problem_id))

#     # #save code
#     @task(52)
#     def save_code(self):
#         problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
#         supported_languages = problem_language_id_map[problem_id]
#         programming_language_id = 511#supported_languages[random.randint(0,(len(supported_languages) - 1))]
#         response = self.client.post("/test/" + str(test_id) + "/save-code/", {
#             "problem_id": problem_id, 
#             "programming_language_id": 511,
#             "is_objective": 'false',
#             "problem_code": problem_codes[problem_id][random.choice(random_matrix)]
#         })

#     # #Submit Code
#     @task(22)
#     def submit_code(self):
#         problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
#         supported_languages = problem_language_id_map[problem_id]
#         programming_language_id = supported_languages[random.randint(0,(len(supported_languages) - 1))]

#         response = self.client.post("/test/" + test_id + "/evaluate-code/", {
#             "problem_id": problem_id, 
#             "programming_language_id": 511,
#             "submission_content": problem_codes[problem_id][random.choice(random_matrix)],
#             "submission_type": 'submit'
#         }, {
#             'X-Requested-With': 'XMLHttpRequest'
#         })        
#         logger.info(response.content)
#         resp_json = json.loads(response.content)

#         r = Timer(10, check_status, (self, test_id, problem_id, resp_json['submission_id']))
#         r.start()
#         #for i in range(1,30):
#             #check_status(self, test_id, problem_id, resp_json['submission_id'])
#             #r = Timer(i, check_status, (self, test_id, problem_id, resp_json['submission_id']))
#             #r.start()

#     #get submission status
#     #@task(2400)
#     #def submission_status(self):                    
#         #response = self.client.get("/test/" + str(test_id) + "/status/?problem_id=" + str(problem_id) + "&submission_id=" + str(response.submission_id))        

#     #session poll
#     @task(90)
#     def session_poll(self):
#         response = self.client.get("/test/" + str(test_id) + "/poll/?current_duration=30" + "&current_extra_time=0")

#class NewUserTasks(TaskSet):
    #Open landing page
    #@task(100)
    #def index(self):
    #    response = self.client.get("/")
    #@task(90)
    #def open_dashboard(self):
    #    response = self.client.get("/dashboard/")
    #@task(81)
    #def open_programming(self):
    #    response = self.client.get("/courses/programming/")
    #@task(73)
    #def open_topic(self):
    #    response = self.client.get("/courses/programming/topics/arrays/")
    #@task(66)
    #def open_problem(self):
    #    response = self.client.get("/problems/max-sum-contiguous-subarray/")



class MyLocust(HttpLocust):
    host = os.getenv('TARGET_URL', "https://staging.scaler.com")
    min_wait = 90
    max_wait = 100


    def on_start(self):
        signup(self)

    def on_stop(self):
        logout(self)

    #open the test programming_language_id
    @task(6)
    def index(self):    
        response = self.client.get("/test/" + test_id + '/')

    #record event
    # @task(33)
    # def record_event(self):
    #     response = self.client.post("/test/" + test_id + '/record-event/',{
    #         "event_type": "jhsdfgjdsf",
    #         "event_value": "kjdkjdhfgkjdfhgifderiuy eiruty idufgy difuyg",
    #         "timestamp": datetime.datetime.now()
    #     })

    #mark problem opened
    # @task(13)
    # def mark_problem_opened(self):
    #     problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
    #     response = self.client.post("/test/" + str(test_id) + "/mark-problem-opened/",{
    #         "problem_id": problem_id
    #     })

    #get live problems
    @task(6)
    def get_live_problems(self):
        response = self.client.get("/test/" + str(test_id) + "/live-problems/")

    #fetch code
    # @task(22)
    # def fetch_code(self):    
    #     problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
    #     supported_languages = problem_language_id_map[problem_id]
    #     programming_language_id = supported_languages[random.randint(0,(len(supported_languages) - 1))]
    #     response = self.client.get("/test/" + str(test_id) + "/get-code/?programming_language_id=" + str(programming_language_id) + "&problem_id=" + str(problem_id))

    # #save code
    # @task(52)
    # def save_code(self):
    #     problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
    #     supported_languages = problem_language_id_map[problem_id]
    #     programming_language_id = 511#supported_languages[random.randint(0,(len(supported_languages) - 1))]
    #     response = self.client.post("/test/" + str(test_id) + "/save-code/", {
    #         "problem_id": problem_id, 
    #         "programming_language_id": 511,
    #         "is_objective": 'false',
    #         "problem_code": problem_codes[problem_id][random.choice(random_matrix)]
    #     })

    # #Submit Code
    # @task(22)
    # def submit_code(self):
    #     problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
    #     supported_languages = problem_language_id_map[problem_id]
    #     programming_language_id = supported_languages[random.randint(0,(len(supported_languages) - 1))]

    #     response = self.client.post("/test/" + test_id + "/evaluate-code/", {
    #         "problem_id": problem_id, 
    #         "programming_language_id": 511,
    #         "submission_content": problem_codes[problem_id][random.choice(random_matrix)],
    #         "submission_type": 'submit'
    #     }, {
    #         'X-Requested-With': 'XMLHttpRequest'
    #     })        
    #     logger.info(response.content)
    #     resp_json = json.loads(response.content)

    #     r = Timer(10, check_status, (self, test_id, problem_id, resp_json['submission_id']))
    #     r.start()
        #for i in range(1,30):
            #check_status(self, test_id, problem_id, resp_json['submission_id'])
            #r = Timer(i, check_status, (self, test_id, problem_id, resp_json['submission_id']))
            #r.start()

    #get submission status
    #@task(2400)
    #def submission_status(self):                    
        #response = self.client.get("/test/" + str(test_id) + "/status/?problem_id=" + str(problem_id) + "&submission_id=" + str(response.submission_id))        

    #session poll
    # @task(90)
    # def session_poll(self):
    #     response = self.client.get("/test/" + str(test_id) + "/poll/?current_duration=30" + "&current_extra_time=0")