# Alex Branciog

import unittest

import twitter_endpoints 

# User
USER = 'Smth_Banal'
USER_ID = '3575504721'
A_STATUS_ID = '738366915941421056'

#TODO
# improve json check by adding a base json containing regexps
# modify check json to do a regex match on each key

class TestUpdateEndpoint(unittest.TestCase):

    def setUp(self):
        self.endpoint = twitter_endpoints.TwitterUpdateEndpoint()
        # will need this to check that the tweet was actually posted
        self.search_endpoint = twitter_endpoints.TwitterSearchEndpoint()

    def test_0_0_0_status(self):
        """
        Tries to post a valid uniq status
        """
        self.assertTrue(self.endpoint.check_request())

    def test_0_0_1_duplicate_status(self):
        """
        Tries to post a duplicate status.
        Should receive an error response.
        """
        params = {'status':'Duplicate'}
        json = {u'errors': [{u'message': u'Status is a duplicate.',
                             u'code': 187}]}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    status_code=403,
                                                    json=json))

    def test_0_1_0_in_reply_to_status_id(self):
        """
        Tries to post a reply to a status given by a valid id.
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
#        selassertTrue(self.search_endpoint.check_request(params=search_params,
#                                                           json=search_json))

    def test_0_1_1_in_reply_to_status_id(self):
        """
        Tries to post a reply to an unexisting status (invalid id)
        """
        params = {'in_reply_to_status_id':'invalid'}
        json = {'in_reply_to_status_id':None,
                'in_reply_to_status_id_str':None}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))

    def test_0_2_0_lat_long(self):
        """
        Tries to post a status specifing the place by lat and long
        """
        params = {'lat':45, 'long':45}
        json = {'place':params.copy()}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))


class TestSearchEndpoint(unittest.TestCase):

    def setUp(self):
        self.endpoint = twitter_endpoints.TwitterSearchEndpoint()

    def test_1_0_0_search(self):
        """
        Tries to post a valid uniq status
        """
        params = {'q':'#tweet'}
        json = {'status':{'text':'#tweet'}}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))

    def test_1_1_0_search_lang(self):
        """
        Tries to post a valid uniq status
        """
        params = {'q':'#tweet', 'lang':'sv'}
        json = {'status':{'text':'#tweet', 'lang':'sv'}}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))

    def test_1_2_0_search_count(self):
        """
        Tries to post a valid uniq status
        """
        params = {'q':'#tweet', 'count':2}
        json = {'status':{'text':'#tweet'}, 'search_metadata':{'count':2},
                'expected_statuses_number':2}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))

    def test_1_3_1_search_until(self):
        """
        Tries to search for tweets older than a week.
        Should get no status.
        """
        params = {'q':'#tweet', 'until':'2015-01-01'}
        json = {'search_metadata':{'count':2},
                'expected_statuses_number':0}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    json=json))
