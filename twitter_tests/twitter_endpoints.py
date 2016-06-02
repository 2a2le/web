# Alex Branciog

import uuid

import requests
import requests_oauthlib
import requests.packages.urllib3 as urllib3

# URLs
SEARCH = 'https://api.twitter.com/1.1/search/tweets.json'
UPDATE = 'https://api.twitter.com/1.1/statuses/update.json'

# OAuth
CLIENT_KEY = u'eVP3L5l1vX6Q20qEWWJBelIfV'
CLIENT_SECRET = u'27VEuF4qErAGCishfleG5zLvBJ1AAmJ3IoVdYJ75xQQxxga9UG'
RESOURCE_OWNER_KEY = u'3575504721-dIpxGbqa4crzDWhwKo16dV56L4lyYHHgi0qczhx'
RESOURCE_OWNER_SECRET = u'IzalISFtV5JLLz7XszaFz8ajUPPZhaGMIoG86aTAuIjEC'


class TestFailedError(AssertionError):
    pass


def generate_uuid():
    """generate uuid for uniq tweets"""
    return str(uuid.uuid4())


class TwitterEndpoint():
    """
    Handles twitter requests.
    """
    def __init__(self):
        """
        Creates a twitter endpoint that can
        send authenticated requests.
        """
        self.auth = requests_oauthlib.OAuth1(CLIENT_KEY,
                        client_secret=CLIENT_SECRET,
                        resource_owner_key=RESOURCE_OWNER_KEY,
                        resource_owner_secret=RESOURCE_OWNER_SECRET)
        self.response = None
        self.json = None
        # suppress urllib3 InsecurePlatformWarning
        urllib3.disable_warnings()

    def _send_request(self, params):
        """
        Sends a request and stores the answer.
        """
        raise NotImplementedError('Each twitter endpoint needs to implement '
                                  '_send_request.')

    def _validate_status_code(self, status_code):
        if self.response.status_code != status_code:
            raise TestFailedError('STATUS_CODE: Expected: {}, Actual: {}'.format(
                                  status_code, self.response.status_code))
        return True

    def _validate_json(self, json):
        """
        Checks the response json.
        """
        raise NotImplementedError('Each twitter endpoint needs to implement '
                                  '_validate_json.')

    def check_request(self, params={}, status_code=200, json={}):
        """
        Sends a request and validates the response.
        """
        self._send_request(params)
        print self.response.json()
        return (self._validate_status_code(status_code) and 
                self._validate_json(json))
        
    

class TwitterUpdateEndpoint(TwitterEndpoint):
    """
    Handles twitter POST statuses/update requests.
    """
    def __init__(self):
        TwitterEndpoint.__init__(self)
        self.url = UPDATE

    def _send_request(self, params = {}):
        self.response = requests.post(url=self.url, params=params,
                                      auth=self.auth)
        self.json = self.response.json()

    def _validate_json(self, json = {}):
        if json.has_key('errors'):
            for error in json['errors']:
                if error not in self.json['errors']:
                    raise TestFailedError(
                            'ERRORS: Expected: {}, Actual: {}'.format(
                                json['errors'], self.json['errors']))
        else:
            for key in json.keys():
                expected = json[key]
                actual = self.json[key] if self.json.has_key(key)\
                            else 'Not present'
                if actual != expected:
                    raise TestFailedError(
                            'FIELD {}: Expected: {}, Actual: {}'.format(
                                key, expected, actual))
        return True

    def check_request(self, params={}, status_code=200, json={}):
        if not params.has_key('status'):
            text = generate_uuid()
            # do not modify mutable default function argument
            params = params.copy() 
            params['status'] = text
            json['text'] = params['status']
        return TwitterEndpoint.check_request(self, params, status_code, json)


class TwitterSearchEndpoint(TwitterEndpoint):
    """
    Handles twitter GET search/tweets requests.
    """
    def __init__(self):
        TwitterEndpoint.__init__(self)
        self.url = SEARCH

    def _send_request(self, params = {}):
        self.response = requests.get(url=self.url, params=params,
                                      auth=self.auth)
        self.json = self.response.json()

"""        
        
    url
    auth
    params

    send_req
    parse_response
for each test json some keys are 
    common
    speciffic
"""
