from requests_oauthlib import OAuth1Session

from KEYS_DONT_PUSH import *

import json
import sqlite3


class Respose():

    def __init__(self) -> None:
        self.base_url = "https://api.bricklink.com/api/store/v1/"
        self.auth = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, TOKEN_VALUE, TOKEN_SECRET)


    def get_response(self, sub_url:str) -> None:
        response = self.auth.get(self.base_url + sub_url)   
        #format response into dict
        self.response = json.loads(response._content.decode("utf-8"))
        return self.response["data"]

        
        