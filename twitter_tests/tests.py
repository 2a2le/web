# Alex Branciog
# encoding: utf-8

import datetime
import unittest

import twitter_endpoints

# User
USER = 'Smth_Banal'
USER_ID = '3575504721'
A_STATUS_ID = '738366915941421056'

class TestUpdateEndpoint(unittest.TestCase):

    def setUp(self):
        self.endpoint = twitter_endpoints.TwitterUpdateEndpoint()
        # will need this to check that the tweet was actually posted
        self.search_endpoint = twitter_endpoints.TwitterSearchEndpoint()

    def test_1_0_0_status(self):
        """
        1.0.0 Post a new status
        """
        self.assertTrue(self.endpoint.check_request())

    def test_1_0_2_duplicate_status(self):
        """
        1.0.2 Post a duplicate status
        """
        params = {'status':'Duplicate'}
        json = {u'errors': [{u'message': u'Status is a duplicate.',
                             u'code': 187}]}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    status_code=403,
                                                    json=json))

    def test_1_1_0_in_reply_to_status_id(self):
        """
        1.1.0 Post a reply
        """
        status = '@{} {}'.format(USER,
                                 twitter_endpoints.generate_uuid())
        params = {'status':status,
                  'in_reply_to_status_id':A_STATUS_ID}
        json = {'text':status, 'in_reply_to_status_id':eval(A_STATUS_ID),
                'in_reply_to_status_id_str':A_STATUS_ID,
                'in_reply_to_user_id':eval(USER_ID),
                'in_reply_to_user_id_str':USER_ID}
        search_params = {'q':status}
        search_json = {'status':json}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))
        self.assertTrue(self.search_endpoint.check_request(params=search_params,
                                                           json=search_json))

    def test_1_1_1_in_reply_to_status_id_no_user(self):
        """
        1.1.1 Post a reply no @user
        """
        params = {'in_reply_to_status_id':A_STATUS_ID}
        json = {'in_reply_to_status_id':None,
                'in_reply_to_status_id_str':None,
                'in_reply_to_user_id':None,
                'in_reply_to_user_id_str':None}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))

    def test_1_1_2_in_reply_to_status_id_invalid(self):
        """
        1.1.2 Post a reply to an invalid status id
        """
        params = {'in_reply_to_status_id':'invalid'}
        json = {'in_reply_to_status_id':None,
                'in_reply_to_status_id_str':None}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))

    def test_1_2_0_lat_long(self):
        """
        1.2.0 Post a new status. Specify the place
        by lat and long parameters.
        """
        params = {'lat':45, 'long':45}
        json = {'place':params.copy()}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))

    # TODO
    # Move the test below in a separate file/folder to
    # be able to run it separately with nosetests
    def notest_0_0_0_status_rate_limit(self):
        """
        1.10.0 Post a new status. Check rate limit.

        The test is not picked up by nose because it will cause
        same failures if the suite is rerun in the same day.
        Remove the no from the test (method) name to run it.
        """
        json = {u'errors': [{u'message': u'User is over daily status update'
                              ' limit.', u'code': 185}]}
        while True:
            try:
                self.endpoint.check_request()
            except twitter_endpoints.TestFailedError:
                self.assertTrue(self.endpoint.check_request(status_code=403,
                                                            json=json))


class TestSearchEndpoint(unittest.TestCase):

    def setUp(self):
        self.endpoint = twitter_endpoints.TwitterSearchEndpoint()

    def test_2_0_0_search(self):
        """
        2.0.0 Search for tweets containing #tweet
        """
        params = {'q':'#tweet'}
        json = {'status':{'text':'#tweet'}}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))

    def test_2_1_0_search_lang(self):
        """
        2.1.0 Search for tweets lang
        """
        params = {'q':'#tweet', 'lang':'sv'}
        json = {'status':{'text':'#tweet', 'lang':'sv'}}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))

    def test_2_2_0_search_locale(self):
        """
        2.2.0 Search for tweets locale
        """
        params = {'q':'ツイート'}
        json = {'status':{'text':'ツイート', 'lang':'ja'}}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))

    def test_2_3_0_search_count(self):
        """
        2.3.0 Search for tweets count
        """
        params = {'q':'#tweet', 'count':2}
        json = {'status':{'text':'#tweet'}, 'search_metadata':{'count':2},
                'expected_statuses_number':2}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))

    def test_2_4_0_search_until(self):
        """
        2.4.0 Search for tweets until
        """
        two_days_ago = datetime.date.today() - datetime.timedelta(days=2)
        params = {'q':'#tweet', 'until':two_days_ago.strftime("%Y-%m-%d"),
                  'count':1}
        json = {'status':{'created_before':two_days_ago}}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))

    def test_2_4_1_search_until(self):
        """
        2.4.1 Search for tweets until more than a week ago
        """
        params = {'q':'#tweet', 'until':'2015-01-01'}
        json = {'expected_statuses_number':0}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))

    # TODO
    # Move the test below in a separate file/folder to
    # be able to run it separately with nosetests
    def notest_2_10_0_search_rate_limit(self):
        """
        2.10.0 Search for tweets. Check the rate limit.

        The test is not picked up by nose because it will cause
        same failures for the rest of the suite.
        Remove the no from the test (method) name to run it.
        """
        params = {'q':'#tweet'}
        json = {'status':{'text':'#tweet'}}
        while True:
            try:
                self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))
            except twitter_endpoints.TestFailedError:
                json = {u'errors': [{u'message': u'Rate limit exceeded',
                                     u'code': 88}]}
                self.assertTrue(self.endpoint.check_request(params=params,
                                                            status_code=429,
                                                            json=json))
