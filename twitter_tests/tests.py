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
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    status_code=200,
                                                    json=json))

    def test_0_1_1_in_reply_to_status_id(self):
        """
        Tries to post a reply to an unexisting status (invalid id)
        """
        params = {'in_reply_to_status_id':'invalid'}
        json = {'in_reply_to_status_id':None,
                'in_reply_to_status_id_str':None}
        self.assertTrue(self.endpoint.check_request(params=params,
                                                    status_code=200,
                                                    json=json))
