from requests_oauthlib import OAuth1Session

from my_scripts.keys import *

import json

class Response():

    def __init__(self) -> None:
        self.base_url = "https://api.bricklink.com/api/store/v1/"
        self.auth = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, TOKEN_VALUE, TOKEN_SECRET)


    def get_response_data(self, sub_url:str, **display:bool) -> dict[str]:
        display = display.get("display", False)
        response = self.auth.get(self.base_url + sub_url)   
        #format response into dict
        self.response = json.loads(response._content.decode("utf-8"))

        if display:
            print(self.response)

        if "data" in self.response:
            return self.response["data"]
        else:
            return {"ERROR":self.response}


def main():
    resp = Response()
    a = resp.get_response_data(f"items/MINIFIG/sw0001a/price")

        
if __name__ == "__main__":
    main()