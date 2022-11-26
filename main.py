from responses import *
from database import *

import time

def main():
    start = time.time()

    resp = Respose()
    db = DatabaseManagment()

    item1 = resp.get_response("items/MINIFIG/sw0282/price")
    item2 = resp.get_response("items/MINIFIG/sw0283/price")
    db.add_price_info([item1, item2])

    fin = time.time()
    print(f"FIN IN {fin-start}")

if __name__ == "__main__":
    main()

