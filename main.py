from responses import *
from database import *
from misc import *

import time

def main():
    
    resp = Respose()
    db = DatabaseManagment()

    target_id = "sw0001a"

    subsets = resp.get_response_data(f"items/MINIFIG/{target_id}/subsets")
    supersets = resp.get_response_data(f"items/MINIFIG/{target_id}/supersets")
    colours = resp.get_response_data(f"items/MINIFIG/{target_id}/colors")

    print(f"{subsets}\n\n{supersets}\n\n{colours}")

if __name__ == "__main__":
    start = time.time()
    main()
    fin = time.time()
    print(f"FINISHED IN {round(fin-start,3)} SECONDS")
