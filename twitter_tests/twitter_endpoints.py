# Alex Branciog

import uuid
import re
import time

import requests
import requests_oauthlib
import requests.packages.urllib3 as urllib3
from dateutil import parser as dateutil_parser

# URLs
SEARCH = 'https://api.twitter.com/1.1/search/tweets.json'
UPDATE = 'https://api.twitter.com/1.1/statuses/update.json'

# OAuth
CLIENT_KEY = u'eVP3L5l1vX6Q20qEWWJBelIfV'
CLIENT_SECRET = u'27VEuF4qErAGCishfleG5zLvBJ1AAmJ3IoVdYJ75xQQxxga9UG'
RESOURCE_OWNER_KEY = u'3575504721-dIpxGbqa4crzDWhwKo16dV56L4lyYHHgi0qczhx'
RESOURCE_OWNER_SECRET = u'IzalISFtV5JLLz7XszaFz8ajUPPZhaGMIoG86aTAuIjEC'

# Max wait between tweet is posted and tweet is searchable
SEARCH_TIMEOUT = 30

#TODO
# improve json check by adding fields to below base json
# containing regexps
base_json = {}


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


    def _validate_json(self, json={}):
        """
        Checks the response json.
        """
        json = json.copy()
        json.update(base_json)
        def _check_errors(errors):
            if not self.json.has_key('errors'):
                raise TestFailedError(
                        'ERRORS: Expected: present, Actual: not present')
            for error in errors:
                if error not in self.json['errors']:
                    raise TestFailedError(
                            'ERRORS: Expected: {}, Actual: {}'.format(
                                errors, self.json['errors']))
        if json.has_key('errors'):
            _check_errors(json.pop('errors'))
        else:
            for key in json.keys():
                expected = json[key]
                actual = self.json[key] if self.json.has_key(key)\
                            else 'Not present'
                if not self._check_value(expected, actual):
                    raise TestFailedError(
                            'FIELD {}: Expected: {}, Actual: {}'.format(
                                key, expected, actual))
        return True

    def check_request(self, params={}, status_code=200, json={}):
        """
        Sends a request and validates the response.
        """
        self._send_request(params)
        print self.response.json()
        return (self._validate_status_code(status_code) and
                self._validate_json(json))

    def _check_value(self, expected, actual):
        """
        Search regex if the expected value is a string.
        Compare otherwise.
        """
        if (type(expected) is str and
                (type(actual) is str or type(actual) is unicode)):
            return re.search(expected, actual) is not None
        return expected == actual


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

    def _check_place(self, expected_place):
        """
        Check that place (lat,long) is contained by place bounding_box
        """
        place = self.json['place']
        if place is None:
            raise TestFailedError('FIELD place: Expected: expected_place,'
                                  ' Actual: Not present')
        min_long, min_lat = place['bounding_box']['coordinates'][0][0]
        max_long, max_lat = place['bounding_box']['coordinates'][0][2]
        exp_lat = expected_place['lat']
        exp_long = expected_place['long']
        if exp_lat < min_lat or exp_lat > max_lat:
            raise TestFailedError('FIELD lat: Expected: Within ({}, {}),'
                    ' Actual: {}'.format(min_lat, max_lat, exp_lat))
        if exp_long < min_long or exp_long > max_long:
            raise TestFailedError('FIELD long: Expected: Within ({}, {}),'
                    ' Actual: {}'.format(min_long, max_long, exp_long))

    def _validate_json(self, json = {}):
        if json.has_key('place'):
            self._check_place(json.pop('place'))
        return TwitterEndpoint._validate_json(self, json)

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

    def _check_statuses(self, expected_status):
        """
        Verifies that each status has the required fields
        given by expected_status.
        Values match the regex/string.
        """
        statuses = self.json['statuses']
        if len(self.json['statuses']) == 0:
            raise TestFailedError(
                   'FIELD STATUSES: Expected: At least one status,'
                   ' Actual: No status')
        for status in self.json['statuses']:
            for status_key in expected_status.keys():
                if status_key == 'created_before':
                    created_before = expected_status['created_before']
                    created_at = status['created_at']
                    created_at = dateutil_parser.parse(created_at).date()
                    if created_at > created_before:
                        raise TestFailedError(
                               'STATUSES FIELD {}: Expected: Before {},'
                               ' Actual: {}'.format(created_at, created_before,
                                                    created_at))
                else:
                    expected = expected_status[status_key]
                    actual = status[status_key] if\
                                status.has_key(status_key)\
                                else 'Not present'
                    if not self._check_value(expected, actual):
                        raise TestFailedError(
                               'STATUSES FIELD {}: Expected: {},'
                               ' Actual: {}'.format(status_key, expected,
                                                    actual.encode('utf-8')))

    def _check_metadata(self, expected_metadata):
        """
        Verifies search response json metadata.
        """
        metadata = self.json['search_metadata']
        for key in expected_metadata.keys():
            expected = expected_metadata[key]
            actual = metadata[key] if metadata.has_key(key)\
                        else 'Not present'
            if not self._check_value(expected, actual):
                raise TestFailedError(
                        'FIELD {}: Expected: {}, Actual: {}'.format(
                                key, expected, actual))
            self._check_value

    def _validate_json(self, json = {}):
        if json.has_key('search_metadata'):
            self._check_metadata(json.pop('search_metadata'))
        if json.has_key('expected_statuses_number'):
            # check if we got the expected number of statuses
            exp_no_statuses = json.pop('expected_statuses_number')
            no_statuses = len(self.json['statuses'])
            if no_statuses != exp_no_statuses:
                raise TestFailedError(
                    'STATUSES: Count: Expected: {}, Actual: {}'.format(
                            exp_no_statuses, no_statuses))
        if json.has_key('status'):
            self._check_statuses(json.pop('status'))
        return TwitterEndpoint._validate_json(self, json)

    def check_request(self, params={}, status_code=200, json={}):
        timeout = SEARCH_TIMEOUT
        while timeout > 0:
            try:
                return TwitterEndpoint.check_request(self, params, status_code, json)
            except TestFailedError:
                # Need to wait a while before the tweet is searchable
                time.sleep(5)
                timeout-=5
        return TwitterEndpoint.check_request(self, params, status_code, json)
