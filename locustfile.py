import os
import string
import random
import sys
import logging
import json
import datetime
import gevent
import websocket
from locust import HttpLocust, SequentialTaskSet, task, events, Locust
from threading import Timer
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info('INIT')

#test data
global test_id
test_id = '5645c712df' #8a2c3d05c2 local, 5645c712df staging
problem_ids = [382, 900] #[228, 382, 900, 1195, 1262]
problem_language_id_map = {
  228: [4, 11, 27, 35, 39, 42, 43, 44, 55, 114, 116, 510, 511, 512],
  382: [4, 11, 27, 35, 39, 42, 43, 44, 55, 114, 116, 510, 511, 512],
  900: [4, 11, 27, 35, 39, 42, 43, 44, 55, 114, 116, 510, 511, 512],
  1195: [4, 11, 27, 35, 39, 42, 43, 44, 55, 114, 116, 510, 511, 512],
  1262: [4, 11, 27, 35, 39, 42, 43, 44, 55, 114, 116, 510, 511, 512],
}
random_matrix = [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
problem_codes = {
  228: [
    'syntax error',
    'int Solution::isSymmetric(TreeNode* A) { return 0; }',
    'vector<int>ans; void inOrder(TreeNode* A) {if(A==NULL)return; inOrder(A->left); ans.push_back(A->val); inOrder(A->right);} int Solution::isSymmetric(TreeNode* A) {ans.clear();inOrder(A);int l=0;int r=ans.size()-1;while(l<r){if(ans[l]!=ans[r])return 0;l++;r--;}return 1;}'
  ],
  382: [
    'syntax error',
    'vector<string> Solution::fizzBuzz(int A) {return 0;}',
    'vector<string> Solution::fizzBuzz(int A) {vector<string> ans;for (int num = 1; num <= A; num++) {if ((num % 3 == 0) && (num % 5 == 0)) {ans.push_back("FizzBuzz");} else if(num % 3 == 0) {ans.push_back("Fizz");} else if(num % 5 == 0) {ans.push_back("Buzz");} else {string numStr;for(int i = num; i > 0; i /= 10) {numStr = char((i % 10) + \'0\') + numStr;}ans.push_back(numStr);}}return ans;}'
  ],
  900: [
    'syntax error',
    'string Solution::solve(string A) {return 0;}',
    'string Solution::solve(string A) {string s;s=A;int j=s.length();int len=j;j=j-1;int count=0;int i=0;string ans;if (s == string(s.rbegin(), s.rend())){if(len%2==1)ans="YES";elseans="NO";}else{while(i<=j){if(s[i]!=s[j])count++;i++;j--;}if(count>1)ans="NO";elseans="YES";}return ans;}'
  ],
  1195: [
    'syntax error',
    'int Solution::solve(vector<int> &A) {return 0;}',
    'int Solution::solve(vector<int> &A) {int ans = 0;int mini = 1e9, maxi = -1e9;for(auto &i : A) {mini = min(mini, i);maxi = max(maxi, i);}for(auto &i : A) {if(mini < i and i < maxi)ans += 1;}return ans;}'
  ],
  1262: [
    'syntax error',
    'int Solution::solve(int A) {return 0;}',
    'int Solution::solve(int A) {return A == 2 ? 1 : 2;}'
  ]
}
# def signup(l):
#   global user_num
#   response = l.client.post("/test/a/load_test/", {
#       "candidate_email": "loadtestinterviewbit+" + user_num +  "@gmail.com",
#       "password": '12ABXYZ12',
#         "candidate_name": user_num,
#         "candidate_city": "Random",
#         "candidate_branch": "candidate_branch",
#         "candidate_degree": "candidate_degree",
#         "candidate_university": "candidate_university",
#         "candidate_contact_number": "9923704608"
#         })
#   l.client.post( "/test/" + test_id + '/' + "save-candidate-details",{
#       "candidate_email": "loadtestinterviewbit+" + user_num +  "@gmail.com",
#       "password": '12ABXYZ12',
#         "candidate_name": user_num,
#         "candidate_city": "Random",
#         "candidate_branch": "candidate_branch",
#         "candidate_degree": "candidate_degree",
#         "candidate_university": "candidate_university",
#         "candidate_contact_number": "9923704608",
#         "disclaimer": "on",
#         "slug": "dkjhfkdfjhg"
#     })
# class MyTaskSet(TaskSet):
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
    #get submission status
    #@task(2400)
    #def submission_status(self):                    
        #response = self.client.get("/test/" + str(test_id) + "/status/?problem_id=" + str(problem_id) + "&submission_id=" + str(response.submission_id))        
    #session poll
    # @task(90)
    # def session_poll(self):
    #     response = self.client.get("/test/" + str(test_id) + "/poll/?current_duration=30" + "&current_extra_time=0")

max_users = 3
user = None

def set_user():
  global user, max_users
  user_num = str(random.randint(0, max_users))

  return {
    'email': "loadtestinterviewbit+" + user_num + "@gmail.com",
    'password': "12ABXYZ12",
    'slug': "loadtest-user-" + user_num
  }

def login(self, user):
  self.client.post(
    "/users/sign_in/", 
    {
      "user[email]": user['email'],
      "user[password]": user['password']
    }
  )

def logout(self):
  self.client.post(
    "/users/sign_out/", 
    {"_method":"delete"}
  )

def check_status(self, test_id, problem_id, submission_id):
  self.client.get(
    "/test/" + test_id + "/status/?problem_id=" + problem_id + "&submission_id=" + submission_id
  )

class SocketClient(object):
  def __init__(self, url):
    self.url = url

  def connect(self, ws_url):
    self.ws = websocket.WebSocket()
    self.ws.settimeout(10)
    self.ws_url = ws_url
    self.ws.connect(self.url + self.ws_url)
    events.quitting += self.on_close
    self.attach_session()

  def attach_session(self):
    payload = {
      "command": "subscribe",
      "identifier": "{\"channel\":\"AppearanceChannel\"}"
    }
    self.send('subscribe', payload)

  def send_with_response(self, payload):
    json_data = json.dumps(payload)
    g = gevent.spawn(self.ws.send, json_data)
    g.get(block=True, timeout=2)
    g = gevent.spawn(self.ws.recv)
    result = g.get(block=True, timeout=10)
    return json.loads(result)

  def on_close(self):
    self.ws.close()

  def send(self, end_point, payload):
    if end_point == 'dummy':
      return
    start_time = time.time()
    e = None
    try:
      self.send_with_response(payload)
    except Exception as exp:
      e = exp
      self.ws.close()
      self.connect(self.ws_url)
    elapsed = int((time.time() - start_time) * 1000)
    if e:
      events.request_failure.fire(
        request_type='sockjs', name=end_point,
        response_time=elapsed, exception=e
      )
    else:
      events.request_success.fire(
        request_type='sockjs', name=end_point,
        response_time=elapsed, response_length=0
      )

class WSTaskSet(TaskSet):
  def on_start(self):
    user = set_user()
    ws_url = '/cable/?token=' + user['slug']
    self.client.connect(ws_url)

  def on_stop(self):
    self.client.on_close()

  @task(1)
  def dummy_action(self):
    self.client.send('dummy', {})

class WSLocust(Locust):
  host = os.getenv('WS_TARGET_HOST', "ws://localhost:3000")
  task_set = WSTaskSet
  min_wait = 0
  max_wait = 0

  # Initialise WS Client
  client = SocketClient(host)

class HTTPTaskSet(SequentialTaskSet):
  def on_start(self):
    user = set_user()
    login(self, user)
  def on_stop(self):
    logout(self)

  # Live Test Index
  @task(5)
  def index(self):
    time_to_wait = 10
    start = time.time()
    response = self.client.get("/test/" + test_id + '/')
    end = time.time()
    if end - start > time_to_wait:
      self._sleep(start + time_to_wait - end)

  # Get Live Problems
  @task(5)
  def get_live_problems(self):
    time_to_wait = 10
    start = time.time()
    response = self.client.get("/test/" + str(test_id) + "/live-problems/")
    end = time.time()
    if end - start > time_to_wait:
      self._sleep(start + time_to_wait - end)

  @task(1)
  def mark_problem_opened(self):
      problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
      response = self.client.post("/test/" + str(test_id) + "/mark-problem-opened/",{
          "problem_id": problem_id
      })

  @task(5)
  def fetch_code(self):    
      problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
      supported_languages = problem_language_id_map[problem_id]
      programming_language_id = supported_languages[random.randint(0,(len(supported_languages) - 1))]
      response = self.client.get("/test/" + str(test_id) + "/get-code/?programming_language_id=" + str(programming_language_id) + "&problem_id=" + str(problem_id))

  @task(8)
  def save_code(self):
      problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
      supported_languages = problem_language_id_map[problem_id]
      programming_language_id = 511#supported_languages[random.randint(0,(len(supported_languages) - 1))]
      response = self.client.post("/test/" + str(test_id) + "/save-code/", {
          "problem_id": problem_id, 
          "programming_language_id": 44,
          "is_objective": 'false',
          "problem_code": problem_codes[problem_id][random.choice(random_matrix)]
      })

  # Submit Code
  @task(10)
  def submit_code(self):
    problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
    supported_languages = problem_language_id_map[problem_id]
    programming_language_id = supported_languages[random.randint(0,(len(supported_languages) - 1))]
    response = self.client.post("/test/" + test_id + "/evaluate-code/", {
      "problem_id": problem_id, 
      "programming_language_id": programming_language_id,
      "submission_content": problem_codes[problem_id][random.choice(random_matrix)],
      "submission_type": 'submit'
    }, {
      'X-Requested-With': 'XMLHttpRequest'
    })        
    logger.info(response.content)
    resp_json = json.loads(response.content)
    r = Timer(10, check_status, (self, test_id, problem_id, resp_json['submission_id']))
    r.start()
    for i in range(1,30):
      check_status(self, test_id, problem_id, resp_json['submission_id'])
      r = Timer(i, check_status, (self, test_id, problem_id, resp_json['submission_id']))
      r.start()

class HTTPLocust(HttpLocust):
  host = os.getenv('TARGET_DOMAIN', "http://localhost:3000")
  task_set = HTTPTaskSet
  min_wait = 0
  max_wait = 0