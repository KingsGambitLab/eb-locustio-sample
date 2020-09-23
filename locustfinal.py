import os
import string
import random
import sys
import logging
import json
import datetime
import gevent
import websocket
from locust import HttpLocust, TaskSet, task, events, Locust
from threading import Timer
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info('INIT')

global test_id
test_id = '5fe3b04e26'
problem_ids = [382, 228] #[228, 382, 900, 1195, 1262]
problem_language_id_map = {
  228: [4, 11, 27, 35, 39, 42, 43, 44, 55, 114, 116, 510, 511, 512],
  382: [4, 11, 27, 35, 39, 42, 43, 44, 55, 114, 116, 510, 511, 512],
  900: [4, 11, 27, 35, 39, 42, 43, 44, 55, 114, 116, 510, 511, 512],
  1195: [4, 11, 27, 35, 39, 42, 43, 44, 55, 114, 116, 510, 511, 512],
  1262: [4, 11, 27, 35, 39, 42, 43, 44, 55, 114, 116, 510, 511, 512],
}
random_matrix = [0,1,1,2,2,2,3,3,4,4]
problem_codes = {
  228: [
    'syntax error',
    'int Solution::isSymmetric(TreeNode* A) { return 0; }',
    'vector<int>ans; void inOrder(TreeNode* A) {if(A==NULL)return; inOrder(A->left); ans.push_back(A->val); inOrder(A->right);} int Solution::isSymmetric(TreeNode* A) {ans.clear();inOrder(A);int l=0;int r=ans.size()-1;while(l<r){if(ans[l]!=ans[r])return 0;l++;r--;}return 1;}',
    'int Solution::isSymmetric(TreeNode* A) { int i=1; while(true) {i+=1;} return 0; }',
    'int Solution::isSymmetric(TreeNode* A) { isSymmetric(A); }',
  ],
  382: [
    'syntax error',
    'vector<string> Solution::fizzBuzz(int A) {return 0;}',
    'vector<string> Solution::fizzBuzz(int A) {vector<string> ans;for (int num = 1; num <= A; num++) {if ((num % 3 == 0) && (num % 5 == 0)) {ans.push_back("FizzBuzz");} else if(num % 3 == 0) {ans.push_back("Fizz");} else if(num % 5 == 0) {ans.push_back("Buzz");} else {string numStr;for(int i = num; i > 0; i /= 10) {numStr = char((i % 10) + \'0\') + numStr;}ans.push_back(numStr);}}return ans;}',
    'vector<string> Solution::fizzBuzz(int A) { int i=1; while(true) {i+=1;} return 0; }',
    'vector<string> Solution::fizzBuzz(int A) {vector<string> s = fizzBuzz(A);}',
  ],
  900: [
    'syntax error',
    'string Solution::solve(string A) {return 0;}',
    'string Solution::solve(string A) {string s;s=A;int j=s.length();int len=j;j=j-1;int count=0;int i=0;string ans;if (s == string(s.rbegin(), s.rend())){if(len%2==1)ans="YES";elseans="NO";}else{while(i<=j){if(s[i]!=s[j])count++;i++;j--;}if(count>1)ans="NO";elseans="YES";}return ans;}',
    'string Solution::solve(string A) { int i=1; while(true) {i+=1;} return 0; }',
    'string Solution::solve(string A) {string s = solve(A);}',
  ],
  1195: [
    'syntax error',
    'int Solution::solve(vector<int> &A) {return 0;}',
    'int Solution::solve(vector<int> &A) {int ans = 0;int mini = 1e9, maxi = -1e9;for(auto &i : A) {mini = min(mini, i);maxi = max(maxi, i);}for(auto &i : A) {if(mini < i and i < maxi)ans += 1;}return ans;}',
    'int Solution::solve(vector<int> &A) { int i=1; while(true) {i+=1;} return 0; }',
    'int Solution::solve(vector<int> &A) {int s = solve(A);}',
  ],
  1262: [
    'syntax error',
    'int Solution::solve(int A) {return 0;}',
    'int Solution::solve(int A) {return A == 2 ? 1 : 2;}',
    'int Solution::solve(int A) { int i=1; while(true) {i+=1;} return 0; }',
    'int Solution::solve(int A) {int s = solve(A);}',
  ]
}

max_users = 3
user = None

batched_events = '[{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:54:25 UTC"},{"event_type":"browser_focus","event_value":null,"timestamp":"2020-09-23 04:54:31 UTC"},{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:54:37 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:54:37 UTC"},{"event_type":"browser_focus","event_value":null,"timestamp":"2020-09-23 04:54:38 UTC"},{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:54:39 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:54:39 UTC"},{"event_type":"browser_focus","event_value":null,"timestamp":"2020-09-23 04:54:40 UTC"},{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:54:41 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:54:41 UTC"},{"event_type":"browser_focus","event_value":null,"timestamp":"2020-09-23 04:54:42 UTC"},{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:54:44 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:54:49 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:54:52 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:54:54 UTC"},{"event_type":"browser_focus","event_value":null,"timestamp":"2020-09-23 04:54:58 UTC"},{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:55:09 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:55:09 UTC"},{"event_type":"browser_focus","event_value":null,"timestamp":"2020-09-23 04:55:10 UTC"},{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:55:30 UTC"}]'

# Assumes 40% users change programming language
language_random_matrix = [1, 1, 1, 2, 2]

def between(min, max):
  return random.randint(min, max)

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
    "/test/" + str(test_id) + "/status/?problem_id=" + str(problem_id) + "&submission_id=" + str(submission_id)
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

class CompleteTaskSet(TaskSet):
  ws_host = os.getenv('WS_TARGET_HOST', "ws://localhost:3000")
  ws_connected = False
  ws_client = None
  
  def on_start(self):
    global user
    user = set_user()
    self.ws_client = SocketClient(self.ws_host)
    login(self, user)

  def on_stop(self):
    logout(self)
    if self.ws_connected:
      self.ws_client.on_close()
  
  # Each function represents a single task i.e, exactly one network request of
  # any form
  def connect_to_socket(self):
    ws_url = '/cable/?token=' + user['slug']
    self.ws_client.connect(ws_url)
    self.ws_connected = True

  def load_live_test_page(self):
    time_to_wait = between(5, 10)
    start = time.time()
    response = self.client.get("/test/" + test_id + '/')
    end = time.time()
    if end - start > time_to_wait:
      self._sleep(start + time_to_wait - end)
  
  def get_live_test_problems(self):
    time_to_wait = between(5, 10)
    start = time.time()
    response = self.client.get("/test/" + str(test_id) + "/live-problems/")
    end = time.time()
    if end - start > time_to_wait:
      self._sleep(start + time_to_wait - end)

  def mark_problem_opened(self, problem_id):
    response = self.client.post("/test/" + str(test_id) + "/mark-problem-opened/",{
        "problem_id": problem_id
    })

  def fetch_code(self, problem_id):    
    supported_languages = problem_language_id_map[problem_id]
    programming_language_id = supported_languages[random.randint(0,(len(supported_languages) - 1))]
    response = self.client.get("/test/" + str(test_id) + "/get-code/?programming_language_id=" + str(programming_language_id) + "&problem_id=" + str(problem_id))

  def save_code(self, problem_id):
    supported_languages = problem_language_id_map[problem_id]
    programming_language_id = 511#supported_languages[random.randint(0,(len(supported_languages) - 1))]
    response = self.client.post("/test/" + str(test_id) + "/save-code/", {
        "problem_id": problem_id, 
        "programming_language_id": 44,
        "is_objective": 'false',
        "problem_code": problem_codes[problem_id][random.choice(random_matrix)]
    })

  def submit_code(self, problem_id):
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
    resp_json = json.loads(response.content)
    r = Timer(10, check_status, (self, test_id, problem_id, resp_json['submission_id']))
    r.start()
    for i in range(1, 3):
      check_status(self, test_id, problem_id, resp_json['submission_id'])
      r = Timer(i, check_status, (self, test_id, problem_id, resp_json['submission_id']))
      r.start()

  def session_poll(self):
    response = self.client.get("/test/" + str(test_id) + "/poll/?current_duration=30" + "&current_extra_time=0")

  def record_batch_events(self):
    response = self.client.post("/test/" + str(test_id) + "/record-batch-events/", {
      "events": batched_events
    })


  @task(100)
  def main_task(self):
    problems_tested = 0
    for case in range(3):
      self.load_live_test_page()
      self.connect_to_socket()
      self.get_live_test_problems()
      if test == 0:
        self._sleep(between(60, 180))
      else:
        self._sleep(between(30, 60))

      max_problems_per_session = 2
      problems_this_session = 0
      while problems_tested < len(problem_ids) and problems_this_session < max_problems_per_session:
        problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
        self.mark_problem_opened(problem_id)

        # Considering programming language change
        num_languages = random.choice(language_random_matrix)
        for c in range(num_languages):
          self.fetch_code(problem_id)

        self._sleep(between(10, 30))
        for i in range(5):
          self.save_code(problem_id)
          self._sleep(1)
          self.submit_code(problem_id)
          self._sleep(between(5, 10))

        problems_this_session += 1
        problems_tested += 1
    logger.info('======COMPLETED MAIN TASK========')
  
  @task(10)
  def poll_task(self):
    self.load_live_test_page()
    self.connect_to_socket()
    for i in range(15):
      self.session_poll()
      self._sleep(10)
    logger.info('======COMPLETED POLL TASK========')
  
  @task(5)
  def record_events(self):
    self.load_live_test_page()
    self.connect_to_socket()
    for i in range(50):
      self.record_batch_events()
      self._sleep(between(5, 10))
    logger.info('======COMPLETED RECORD EVENTS TASK========')



class HTTPLocust(HttpLocust):
  host = os.getenv('TARGET_DOMAIN', "http://localhost:3000")
  task_set = CompleteTaskSet
  min_wait = 0
  max_wait = 0