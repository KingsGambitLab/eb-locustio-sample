import logging
import random
import time

from locust import HttpUser, task, between

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info('INIT')


WEBSITE_HOST = 'https://staging7.scaler.com'
BYPASS_FORGERY_SECRET = 'terces_yregrof'
BYPASS_THROTTLING_SECRET = 'terces_gnilttorht'
MEETING_SLUG = 'load-test-session'
MEETING_AUDIENCE_PASSWORD = 'ImR7wsw66G5C5O8vG8XY1LYqqBcVoNpb'
MAX_USERS = 3000

def login(user):
  user_num = str(random.randint(1, MAX_USERS))
  payload = {
    'user[email]': 'dronaloadtester+' + user_num + '@gmail.com',
    'user[password]': '12ABXYZ12'
  }
  response = user.client.post('/users/sign_in/?bypass_forgery_secret=' + BYPASS_FORGERY_SECRET + '&bypass_throttling_secret=' + BYPASS_THROTTLING_SECRET, payload)

class MeetingApi:
  def __init__(self, locust_user, slug):
    self.locust_user = locust_user
    self.slug = slug

  def create_url(self, endpoint):
    return '/meetings/' + self.slug + endpoint + '?bypass_forgery_secret=' + BYPASS_FORGERY_SECRET + '&bypass_throttling_secret=' + BYPASS_THROTTLING_SECRET
  
  def get(self, endpoint):
    url = self.create_url(endpoint)
    return self.locust_user.client.get(url)
  
  def post(self, endpoint, payload={}):
    url = self.create_url(endpoint)
    return self.locust_user.client.post(url, payload)

  def page(self):
    self.locust_user.client.get('/meetings/i/' + self.slug + '/live')

  def basic_details(self):
    response = self.get('/item')
    return response.json()['meeting']

  def join_as_audience(self):
    payload = {
      'password': MEETING_AUDIENCE_PASSWORD,
      'role': 'audience'
    }
    response = self.post('/participants', payload)
    return response.json()

  def plugins(self):
    response = self.get('/plugins')
    return response.json()

  def session_details(self):
    response = self.get('/live-session')
    return response.json()

  def messages(self):
    response = self.get('/messages')
    return response.json()


class DronaUser(HttpUser):
  wait_time = between(2, 6)
  host = WEBSITE_HOST
  
  # def __init__(self):
  #   self.meeting_api = MeetingApi(self, MEETING_SLUG)

  def on_start(self):
    self.client.headers = {
      'Authorization': 'Basic aW1wYWN0OmdldHNoaXRkb25l'
    }
    self.meeting_api = MeetingApi(self, MEETING_SLUG)
    login(self)

  @task
  def join_meeting(self):
    details = self.meeting_api.basic_details()
    if not 'role' in details['participant']:
      self.meeting_api.join_as_audience()
    self.meeting_api.plugins()
    self.meeting_api.session_details()
    self.meeting_api.messages()











