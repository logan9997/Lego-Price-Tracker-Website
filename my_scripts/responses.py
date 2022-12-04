from requests_oauthlib import OAuth1Session

from my_scripts.KEYS_DONT_PUSH import *

import json

class Respose():

    def __init__(self) -> None:
        self.base_url = "https://api.bricklink.com/api/store/v1/"
        self.auth = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, TOKEN_VALUE, TOKEN_SECRET)


    def get_response_data(self, sub_url:str, **display:bool) -> None:
        display = display.get("display", False)
        response = self.auth.get(self.base_url + sub_url)   
        #format response into dict
        self.response = json.loads(response._content.decode("utf-8"))
        if "data" in self.response:
            if display:
                print(self.response["data"])
            return self.response["data"]
        else:
            if display:
                print(f'ERROR AT {sub_url}\n{self.response["meta"]}\n')
            return None



        
        