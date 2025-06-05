import os
import string
import random
import sys
import logging
import json
import datetime
import gevent
import websocket
from locust import HttpUser, TaskSet, task, events, Locust
from threading import Timer
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info('INIT')

global test_id

# staging data
test_id = '039fe767d1'
test_id_number = 915642

# local data
test_id = '332c23102d'
test_id_number = 14515

problem_ids = [228, 382, 900, 1195, 1262]
program_languages_random_map = [44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 116, 116, 511]
problem_language_id_map = {
  228: program_languages_random_map,
  382: program_languages_random_map,
  900: program_languages_random_map,
  1195: program_languages_random_map,
  1262: program_languages_random_map,
}
random_matrix = [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,3,3,3,4,4]

python_tle = """
class Solution: 
    # @param A : string 
    # @return a strings 
    def solve(self, A): 
        while True:
            continue
"""
python_mle = """
class Solution: 
  # @param A : string 
  # @return a strings 
  def solve(self, A): 
    Solution.solve(self, A)
"""
problem_codes = {
  228: {
      44: [
        'syntax error',
        'int Solution::isSymmetric(TreeNode* A) { return 0; }',
        'vector<int>ans; void inOrder(TreeNode* A) {if(A==NULL)return; inOrder(A->left); ans.push_back(A->val); inOrder(A->right);} int Solution::isSymmetric(TreeNode* A) {ans.clear();inOrder(A);int l=0;int r=ans.size()-1;while(l<r){if(ans[l]!=ans[r])return 0;l++;r--;}return 1;}',
        'int Solution::isSymmetric(TreeNode* A) { int i=1; while(true) {i+=1;} return 0; }',
        'int Solution::isSymmetric(TreeNode* A) { isSymmetric(A); }',
      ],
      116: [
        'syntax error',
"""
class Solution: 
  def isMirror(self,root1,root2): 
    if(root1==None and root2==None): 
      return True 
    if(root1 and root2 and root1.val==root2.val): 
      return self.isMirror(root1.left,root2.right) and self.isMirror(root1.right,root2.left) 
    return False 
  
  def isSymmetric(self, A): 
    if self.isMirror(A,A): 
      return 0
    return 0
""",
"""
class Solution: 
  def isMirror(self,root1,root2): 
    if(root1==None and root2==None): 
      return True 
    if(root1 and root2 and root1.val==root2.val): 
      return self.isMirror(root1.left,root2.right) and self.isMirror(root1.right,root2.left) 
    return False 
  
  def isSymmetric(self, A): 
    if self.isMirror(A,A): 
      return 1 
    return 0
""",
python_tle,
python_mle
      ],
      511: [
          'syntax error',
          'public class Solution {public int isSymmetric(TreeNode A) {return 0;}}',
          'public class Solution { boolean isMirror(TreeNode A,TreeNode B){ if(A==null && B==null) return true; if(A==null || B==null) return false; return (A.val==B.val && isMirror(A.left,B.right) && isMirror(A.right,B.left)); } public int isSymmetric(TreeNode A) { if(A==null) return 1; if(A.left==null && A.right==null) return 1; if(A.left==null || A.right==null) return 0; return (isMirror(A.left,A.right)?1:0); } }',
          'public class Solution {public int isSymmetric(TreeNode A) {int i=0;while (true) {i++;}}}',
          'public class Solution {public int isSymmetric(TreeNode A) {int s = isSymmetric(A);return 1;}}'
      ]
  },
  382: {
      44: [
        'syntax error',
        'vector<string> Solution::fizzBuzz(int A) {return 0;}',
        'vector<string> Solution::fizzBuzz(int A) {vector<string> ans;for (int num = 1; num <= A; num++) {if ((num % 3 == 0) && (num % 5 == 0)) {ans.push_back("FizzBuzz");} else if(num % 3 == 0) {ans.push_back("Fizz");} else if(num % 5 == 0) {ans.push_back("Buzz");} else {string numStr;for(int i = num; i > 0; i /= 10) {numStr = char((i % 10) + \'0\') + numStr;}ans.push_back(numStr);}}return ans;}',
        'vector<string> Solution::fizzBuzz(int A) { int i=1; while(true) {i+=1;} return 0; }',
        'vector<string> Solution::fizzBuzz(int A) {vector<string> s = fizzBuzz(A);}',
      ],
      116: [
        'syntax error',
"""
class Solution: 
  def fizzBuzz(self, A): 
    lst = [] 
    i=0 
    while i < A: 
      if(((i+1)%3 == 0) & ((i+1)%5 == 0)): 
        lst.append("FizzBuzz") 
      elif((i+1)%5 == 0): 
        lst.append("Buzz") 
      elif((i+1)%3 == 0): 
        lst.append("Fizz") 
      else: 
        lst.append(i+1) 
      i += 1 
    return []
""",
"""
class Solution: 
  def fizzBuzz(self, A): 
    lst = [] 
    i=0 
    while i < A: 
      if(((i+1)%3 == 0) & ((i+1)%5 == 0)): 
        lst.append("FizzBuzz") 
      elif((i+1)%5 == 0): 
        lst.append("Buzz") 
      elif((i+1)%3 == 0): 
        lst.append("Fizz") 
      else: 
        lst.append(i+1) 
      i += 1 
    return lst
""",
python_tle,
python_mle
      ],
      511: [
          'syntax error',
          'public class Solution {public ArrayList<String> fizzBuzz(int A) {ArrayList<String> al = new ArrayList();return al;} }',
          'public class Solution { public ArrayList<String> fizzBuzz(int A) { ArrayList<String> al = new ArrayList(); for (int i = 1 ; i <= A ; i++){ if ( i%3 == 0 && i%5 == 0 ){ al.add("FizzBuzz"); }else if ( i%3 == 0 ){ al.add("Fizz"); }else if ( i%5 == 0 ){ al.add("Buzz"); }else{ al.add(i+""); } } return al; } }',
          'public class Solution {public ArrayList<String> fizzBuzz(int A) {ArrayList<String> al = new ArrayList();int i = 0;while (true) {i+=1;}} }',
          'public class Solution {public ArrayList<String> fizzBuzz(int A) {ArrayList<String> al = new ArrayList();al = fizzBuzz(A);return al;} }'
      ]
  },
  900: {
      44: [
        'syntax error',
        'string Solution::solve(string A) {return 0;}',
        'string Solution::solve(string A) {string s;s=A;int j=s.length();int len=j;j=j-1;int count=0;int i=0;string ans;if (s == string(s.rbegin(), s.rend())){if(len%2==1)ans="YES";elseans="NO";}else{while(i<=j){if(s[i]!=s[j])count++;i++;j--;}if(count>1)ans="NO";elseans="YES";}return ans;}',
        'string Solution::solve(string A) { int i=1; while(true) {i+=1;} return 0; }',
        'string Solution::solve(string A) {string s = solve(A);}',
      ],
      116: [
        'syntax error',
"""
class Solution: 
# @param A : string 
# @return a strings 
  def solve(self, A): 
    a=A[::-1] 
    c=0 
    if len(A)==1: 
      return 'YES' 
    for i in range(len(A)//2): 
      if a[i]!=A[i]: 
        c+=1 
    return 'WA'
""",
"""
class Solution: 
  # @param A : string 
  # @return a strings 
  def solve(self, A): 
    a=A[::-1] 
    c=0 
    if len(A)==1: 
      return 'YES' 
    for i in range(len(A)//2): 
      if a[i]!=A[i]: 
        c+=1 
    if len(A)%2==0 and c==1: 
      return 'YES'
    if len(A)%2!=0 and c<=1: 
      return 'YES' 
    else: 
      return 'NO'
""",
python_tle,
python_mle
      ],
      511: [
          'syntax error',
          'public class Solution { public String solve(String A) {return "";} }',
          'public class Solution { public String solve(String A) { int count = 0; for(int i = 0;i<A.length()/2;i++){ if(A.charAt(i)!=A.charAt(A.length()-1-i))count++; } if(count==0 && A.length()%2==0)return "NO"; if(count<2)return "YES"; return "NO"; } }',
          'public class Solution { public String solve(String A) {int i=0;while (true) {i+=1;}} }',
          'public class Solution { public String solve(String A) {String s = solve(A);return "";} }'
      ]
  },
  1195: {
      44: [
        'syntax error',
        'int Solution::solve(vector<int> &A) {return 0;}',
        'int Solution::solve(vector<int> &A) {int ans = 0;int mini = 1e9, maxi = -1e9;for(auto &i : A) {mini = min(mini, i);maxi = max(maxi, i);}for(auto &i : A) {if(mini < i and i < maxi)ans += 1;}return ans;}',
        'int Solution::solve(vector<int> &A) { int i=1; while(true) {i+=1;} return 0; }',
        'int Solution::solve(vector<int> &A) {int s = solve(A);}',
      ],
      116: [
        'syntax error',
"""
class Solution:
  def solve(self, A):
    ans = 0
    mini = 1e9
    maxi = -1e9

    for i in A:
      mini = min(mini, i);
      maxi = max(maxi, i);

    for i in A:
      if mini < i and i < maxi:
        ans += 1;

    return 0
""",
"""
class Solution:
  def solve(self, A):
    ans = 0
    mini = 1e9
    maxi = -1e9

    for i in A:
      mini = min(mini, i);
      maxi = max(maxi, i);

    for i in A:
      if mini < i and i < maxi:
        ans += 1;

    return ans
""",
python_tle,
python_mle
      ],
      511: [
          'syntax error',
          'public class Solution { public int solve(ArrayList<Integer> A) {return 0;} }',
          'public class Solution { public int solve(ArrayList<Integer> A) { Collections.sort(A); int duplicate = 0;for(int i=1;i<A.size()-1;i++){ int n = A.get(i);if(n<A.get(A.size()-1) && A.get(0)<n) { duplicate++;} } return duplicate; } }',
          'public class Solution { public int solve(ArrayList<Integer> A) {int i=0;while (true) {i+=1;}} }',
          'public class Solution { public int solve(ArrayList<Integer> A) {int i=solve(A);return i;} }'
      ]
  },
  1262: {
      44: [
        'syntax error',
        'int Solution::solve(int A) {return 0;}',
        'int Solution::solve(int A) {return A == 2 ? 1 : 2;}',
        'int Solution::solve(int A) { int i=1; while(true) {i+=1;} return 0; }',
        'int Solution::solve(int A) {int s = solve(A);}',
      ],
      116: [
        'syntax error',
"""
class Solution: 
  def solve(self, A): 
    if A == 2: 
      return 1 
    else: 
      return 1
""",
"""
class Solution: 
  def solve(self, A): 
    if A == 2: 
      return 1 
    else: 
      return 2
""",
python_tle,
python_mle
      ],
      511: [
          'syntax error',
          'public class Solution {public int solve(int A) {return 0;}}',
          'public class Solution { public static boolean isPrime(int n){ for(int i=2;i<n;i++){ if(n%i==0){ return false; } } return true; } public int solve(int n) { int half=n/2; if(n<=2){ return 1; } while(!isPrime(half)){ half--; if(isPrime(half)){ break; } } int otherHalf=n-half; return 2; } }',
          'public class Solution {public int solve(int A) {int i=0;while (true) {i+=1;}}',
          'public class Solution {public int solve(int A) {int i=solve(A);return i;}}'
      ]
  }
}


is_prod = False
max_ib_users = 100000

submission_dispersion = int(os.getenv('SUBMISSION_DISPERSION', "250"))

batched_events = '[{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:54:25 UTC"},{"event_type":"browser_focus","event_value":null,"timestamp":"2020-09-23 04:54:31 UTC"},{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:54:37 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:54:37 UTC"},{"event_type":"browser_focus","event_value":null,"timestamp":"2020-09-23 04:54:38 UTC"},{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:54:39 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:54:39 UTC"},{"event_type":"browser_focus","event_value":null,"timestamp":"2020-09-23 04:54:40 UTC"},{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:54:41 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:54:41 UTC"},{"event_type":"browser_focus","event_value":null,"timestamp":"2020-09-23 04:54:42 UTC"},{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:54:44 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:54:49 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:54:52 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:54:54 UTC"},{"event_type":"browser_focus","event_value":null,"timestamp":"2020-09-23 04:54:58 UTC"},{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:55:09 UTC"},{"event_type":"tab_switch","event_value":null,"timestamp":"2020-09-23 04:55:09 UTC"},{"event_type":"browser_focus","event_value":null,"timestamp":"2020-09-23 04:55:10 UTC"},{"event_type":"browser_blur","event_value":null,"timestamp":"2020-09-23 04:55:30 UTC"}]'

# Assumes 40% users change programming language
language_random_matrix = [1, 1, 1, 2, 2]

dispersion_random_matrices = [
  [0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
  [0, 0, 0, 0, 0, 0, 1, 1, 1, 2],
  [0, 0, 0, 0, 1, 1, 1, 2, 2, 3],
]
dispersion_delays = [1, .5, .25, 0]

warm_up_urls = [
  'facebook-interview-questions',
  'google-interview-questions',
  'amazon-interview-questions',
  'microsoft-interview-questions',
  'sql-interview-questions',
  'python-interview-questions',
  'javascript-interview-questions',
  'mvc-interview-questions',
  'react-interview-questions',
  'angular-interview-questions',
  'directi-interview-questions',
  'yahoo-interview-questions',
  'linkedin-interview-questions',
  'vmware-interview-questions',
  'ebay-interview-questions',
  'flipkart-interview-questions'
]

def between(min, max):
  return random.randint(min, max)

def create_url(url, query_params = {}):
  forgery_secret = os.getenv('BYPASS_FORGERY_SECRET', 'terces_yregrof')
  throttle_secret = os.getenv('BYPASS_THROTTLING_SECRET', 'terces_gnilttorht')
  bypass_url = url + "?bypass_forgery_secret=" + forgery_secret + "&bypass_throttling_secret=" + throttle_secret
  for name in query_params:
    bypass_url += "&" + name + "=" + str(query_params[name])
  return bypass_url

def set_ib_user():
  global max_ib_users
  user_num = str(random.randint(1, max_ib_users))

  if is_prod:
    return {
      'email': "ibloadtester+" + user_num + "@gmail.com",
      'password': "12ABXYZ12",
      'slug': "ib-loadtest-" + user_num
    }
  else:
    return {
      'email': "loadtestinterviewbit+" + user_num + "@gmail.com",
      'password': "12ABXYZ12",
      'slug': "loadtest-user-" + user_num
    }


def login(self, user):
  self.client.post(
    create_url("/users/sign_in/"),
    {
      "user[email]": user['email'],
      "user[password]": user['password']
    }
  )

def logout(self):
  self.client.post(
    create_url("/users/sign_out/"), 
    {"_method":"delete"}
  )


def check_status(self, test_id, problem_id, submission_id):
  params = { "problem_id": problem_id, "submission_id": submission_id }
  self.client.get(
    create_url("/test/" + str(test_id) + "/status/", params)
  )

class SocketClient(object):
  def __init__(self, url):
    self.url = url

  def connect(self, ws_url):
    self.ws = websocket.WebSocket()
    self.ws.settimeout(10)
    self.ws_url = ws_url
    self.ws.connect(self.url + self.ws_url)
    events.test_stop.add_listener(self.on_close)
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
    logger.info('======SOCKET RESPONSE========')
    logger.info(result)
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
      events.request.fire(
        request_type='sockjs', name=end_point,
        response_time=elapsed, exception=e, success=0
      )
    else:
      events.request.fire(
        request_type='sockjs', name=end_point,
        response_time=elapsed, response_length=0, success=1
      )

class CompleteTaskSet(TaskSet):
  # ws_host = os.getenv('WS_TARGET_HOST', "wss://impact:getshitdone@6.staging.sclr.ac")
  ws_host = os.getenv('WS_TARGET_HOST', "ws://127.0.0.1:3000")
  warm_up = False
  
  def on_start(self):
    if self.warm_up:
      return

    self._ib_user = set_ib_user()
    self.opened_problems = []
    self.ws_connected = False
    self.ws_client = SocketClient(self.ws_host)
    login(self, self._ib_user)

  def on_stop(self):
    if self.warm_up:
      return

    logout(self)
    if self.ws_connected:
      self.ws_client.on_close()
  
  # Each function represents a single task i.e, exactly one network request of
  # any form
  def connect_to_socket(self):
    ws_url = '/cable/?token=' + self._ib_user['slug']
    self.ws_client.connect(ws_url)
    self.ws_connected = True

  def load_live_test_page(self):
    response = self.client.get(create_url("/test/" + test_id + '/'))
  
  def save_candidate_details(self):
    form_data = {
      "authenticity_token": "DFYue7fmpZCAxjdY0Exr5KVuufcZQFpckQ/Am+N7OQ8RgPAPKAdgOLnefhoxtCO2qsw0i8lTV3cdNuf+lPYotA==",
      "candidate_email": self._ib_user['email'],
      "candidate_name": self._ib_user['email'],
      "candidate_grad_year": "2024",
      "disclaimer": "on",
      "restricted_disclaimer": "on"
    }
    response = self.client.post(create_url("/test/" + test_id + "/save-candidate-details/"), data=form_data)

  def dual_camera_init(self):
    params = {
      "api_context": {
        "id": test_id_number,
        "type": "interviewbit_test"
      }
    }
    response = self.client.get(create_url("/api/v3/proctoring/dual_camera/init"), params=params)
    
  def start_test(self):
    response = self.client.put(create_url("/api/v3/assessments/" + str(test_id_number) + "/session/start/"))
  
  def get_live_test_problems(self):
    gevent.sleep(between(1, 5))
    response = self.client.get(create_url("/test/" + str(test_id) + "/live-problems/"))

  def mark_problem_opened(self, problem_id):
    if problem_id in self.opened_problems:
      return

    response = self.client.post(create_url("/test/" + str(test_id) + "/mark-problem-opened/"), json={
        "problem_id": problem_id
    })
    self.opened_problems.append(problem_id)

  def fetch_code(self, problem_id):    
    supported_languages = problem_language_id_map[problem_id]
    programming_language_id = supported_languages[random.randint(0,(len(supported_languages) - 1))]
    params = {
      "programming_language_id": programming_language_id,
      "problem_id": problem_id
    }
    response = self.client.get(create_url("/test/" + str(test_id) + "/get-code/", params))

  def save_code(self, problem_id):
    supported_languages = problem_language_id_map[problem_id]
    programming_language_id = supported_languages[random.randint(0,(len(supported_languages) - 1))]
    response = self.client.post(create_url("/test/" + str(test_id) + "/save-code/"), json={
        "problem_id": problem_id, 
        "programming_language_id": programming_language_id,
        "is_objective": 'false',
        "problem_code": problem_codes[problem_id][programming_language_id][random.choice(random_matrix)]
    })

  def submit_code(self, problem_id):
    supported_languages = problem_language_id_map[problem_id]
    programming_language_id = supported_languages[random.randint(0,(len(supported_languages) - 1))]

    response = self.client.post(create_url("/test/" + test_id + "/evaluate-code/"), json={
      "problem_id": problem_id, 
      "programming_language_id": programming_language_id,
      "submission_content": problem_codes[problem_id][programming_language_id][random.choice(random_matrix)],
      "submission_type": 'submit'
    }, headers={
      'X-Requested-With': 'XMLHttpRequest'
    })

    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>SOCKET')
    print(self.ws_client.__str__())
    resp_json = json.loads(response.content)
    for i in range(0, 3):
      r = Timer(i, check_status, (self, test_id, problem_id, resp_json['submission_id']))
      r.start()

  def session_poll(self):
    params = {
      "current_duration": 30,
      "current_extra_time": 0
    }
    response = self.client.get(create_url("/test/" + str(test_id) + "/poll/", params))

  def record_batch_events(self):
    response = self.client.post(create_url("/test/" + str(test_id) + "/record-batch-events/"), json={
      "events": batched_events
    })

  # Call this to indicate the end of test
  def perform_health_check(self):
    response = self.client.get(create_url("/health_check_v3/"))

  def load_interview_questions_page(self, url):
    response = self.client.get(create_url("/" + url + "/"))

  @task(10)
  def submission_task(self):
    for i in range(5):
      problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
      self.submit_code(problem_id)

  @task(100)
  def main_task(self):
    gevent.sleep(20)
    if self.warm_up:
      for url in warm_up_urls:
        self.load_interview_questions_page(url)
      return

    # Load Test twice
    self.load_live_test_page()
    self.load_live_test_page()
    
    gevent.sleep(10)
    self.save_candidate_details()
    # self.dual_camera_init()
    
    # start the test
    # self.start_test()
    
    problems_tested = 0
    for case in range(3):
      dispersion_random_matrix = dispersion_random_matrices[case]
      self.connect_to_socket()
      self.connect_to_socket()
      self.connect_to_socket()
      self.connect_to_socket()
      self.connect_to_socket()
      self.connect_to_socket()
      self.get_live_test_problems()
      self.get_live_test_problems()

      max_problems_per_session = 2
      problems_this_session = 0
      while problems_tested < len(problem_ids) and problems_this_session < max_problems_per_session:
        problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
        self.mark_problem_opened(problem_id)

        gevent.sleep(between(10, 30))
        for i in range(5):
          buffer = between(0, submission_dispersion)
          gevent.sleep(buffer)

          self.fetch_code(problem_id)
          gevent.sleep(1)
          
          # Considering programming language change
          num_languages = random.choice(language_random_matrix)
          if num_languages > 1:
            self.fetch_code(problem_id)
            gevent.sleep(1)

          self.save_code(problem_id)
          self.submit_code(problem_id)

          # Asumming 30% users switch problem after a submission
          # 25% because they answered correct
          # 5% because they want to spend time on other problems
          if random.randint(1, 100) <= 30:
            problem_id = problem_ids[random.randint(0,(len(problem_ids) - 1))]
            self.mark_problem_opened(problem_id)

          delay_fraction = dispersion_delays[random.choice(dispersion_random_matrix)]
          gevent.sleep(delay_fraction * (submission_dispersion - buffer))

        problems_this_session += 1
        problems_tested += 1
      self.record_batch_events()
    self.perform_health_check()
    logger.info('======COMPLETED MAIN TASK========')
  
  @task(10)
  def poll_task(self):
    for i in range(10):
      self.session_poll()
      gevent.sleep(10)
    self.perform_health_check()
    logger.info('======COMPLETED POLL TASK========')
  
  @task(5)
  def record_events(self):
    for i in range(10):
      self.record_batch_events()
      gevent.sleep(between(5, 10))
    self.perform_health_check()
    logger.info('======COMPLETED RECORD EVENTS TASK========')

class MitUser(HttpUser):
  # host = os.getenv('TARGET_DOMAIN', "https://impact:getshitdone@6.staging.sclr.ac")
  host = os.getenv('TARGET_DOMAIN', "http://localhost:3000")
  min_wait = 0
  max_wait = 0

  tasks = {CompleteTaskSet:2}
