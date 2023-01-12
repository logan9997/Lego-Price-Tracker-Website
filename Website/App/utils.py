#miscellaneous functions.
import sys

sys.path.insert(1, r"C:\Users\logan\OneDrive\Documents\Programming\Python\api's\BL_API")

from my_scripts.database import *

db = DatabaseManagment()

def get_portfolio_items(user_id) -> list[str]:
    portfolio_items = db.get_portfolio_items(user_id) 

    #format portfolio items into dict for readability in template
    portfolio_items = [{
        "image_path":f"App/images/{portfolio_item[0]}.png",
        "item_id":portfolio_item[0],
        "condition":portfolio_item[1],
        "quantity":portfolio_item[2],
        "item_name":portfolio_item[3],
        "item_type":portfolio_item[4],
        "year_released":portfolio_item[5],
        # "avg_price":portfolio_item[6],
        # "min_price":portfolio_item[7],
        # "max_price":portfolio_item[8],
        # "total_quantity":portfolio_item[9], 
    } for portfolio_item in portfolio_items]

    return portfolio_items