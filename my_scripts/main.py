from responses import *
from database import *
from misc import *

import time

def main():
    
    resp = Response()
    db = DatabaseManagment()

    ids = db.get_all_itemIDs()[:4500]
    print(len(ids))

    for _id in ids:
        print(_id[0], f"items/MINIFIG/{_id[0]}")
        
        info = resp.get_response_data(f"items/MINIFIG/{_id[0]}")
        if info == {}:
            info = resp.get_response_data(f"items/SET/{_id[0]}")

        try:
            db.insert_item_info(info)
        except sqlite3.IntegrityError:
            pass


if __name__ == "__main__":
    start = time.time()
    main()
    fin = time.time()
    print(f"FINISHED IN {round(fin-start,3)} SECONDS")
