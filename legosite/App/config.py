import sys

sys.path.insert(1, r"C:\Users\logan\OneDrive\Documents\Programming\Python\apis\BL_API")

from my_scripts.database import *
from my_scripts.responses import *
from .config import *

RESP = Response()
DB = DatabaseManagment()

RECENTLY_VIEWED_ITEMS_NUM = 6
PAGE_NUM_LIMIT = 8
SEARCH_ITEMS_PER_PAGE = 50
USER_ITEMS_ITEMS_PER_PAGE = 10
MAX_SIMILAR_ITEMS = 12
ALL_METRICS = ["avg_price", "min_price", "max_price", "total_quantity"]

REMOVE_CHARS = ["(", ")"]
REMOVE_WORDS = [
    "and", "in", "for", "and", "all", "with", "one", "two",
    "containing", "including", "extra", "modified", "not", "eyes",
    "large", "small", "the", "printed", "legs", "arms", "molded", "dark",
    "light", "tan", "markings", "aqua", "black", "blue", "green", "orange",
    "yellow", "pink", "brown", "coral", "azure", "gray", "nougat", "purple", 
    "red", "turqoise", "lavender", "lime", "maersk", "magenta", "neon",
    "olive", "sand", "reddish", "white", "yellowish", "trans-", "trans", "leg", 
    "arm", "head"
    ]

for func in [str.upper, str.capitalize]:
    REMOVE_WORDS.extend(list(map(func, REMOVE_WORDS)))


def get_sort_options() -> list[dict[str, str]]:
    SORT_OPTIONS = [
        {"value":"avg_price-desc", "text":"Average Price High to Low"},
        {"value":"avg_price-asc", "text":"Average Price Low to High"},
        {"value":"min_price-desc", "text":"Min Price High to Low"},
        {"value":"min_price-asc", "text":"Min Price Low to High"},
        {"value":"max_price-desc", "text":"Max Price High to Low"},
        {"value":"max_price-asc", "text":"Max Price Low to High"},
        {"value":"total_quantity-desc", "text":"Quantity High to Low"},
        {"value":"total_quantity-asc", "text":"Quantity Low to High"},
        {"value":"item_id-asc", "text": "Item ID A to Z"},
        {"value":"item_id-desc", "text": "Item ID Z to A"},
        {"value":"item_name-asc", "text": "Item Name A to Z"},
        {"value":"item_name-desc", "text": "Item Name Z to A"},
    ]
    return SORT_OPTIONS

def get_graph_options() -> list[dict[str, str]]:
    GRAPH_OPTIONS = [
        {"value":"avg_price","text":"Average Price"},
        {"value":"min_price","text":"Minimum Price"},
        {"value":"max_price","text":"Maximum Price"},
        {"value":"total_quantity","text":"Quantity Avialble"},
    ]
    return GRAPH_OPTIONS

def get_search_sort_options() -> list[dict[str,str]]:
    SEARCH_SORT_OPTIONS = [
        {"value":"theme_name-asc", "text":"Theme name Asc"},
        {"value":"theme_name-desc", "text":"Theme name Desc"},
        {"value":"popularity-asc", "text":"popularity Asc"},
        {"value":"popularity-desc", "text":"popularity Desc"},
        {"value":"avg_growth-asc", "text":"Average Growth Asc"},
        {"value":"avg_growth-desc", "text":"Average Growth Desc"},
        {"value":"num_items-asc", "text":"Number of Items Asc"},
        {"value":"num_items-desc", "text":"Number of Items Desc"},
    ]
    return SEARCH_SORT_OPTIONS


def get_trending_options() -> list[dict[str, str]]:
    TRENDING_SORT_OPTIONS = [
        {"value":"avg_price-desc", "text":"Average Price % Change"},
        {"value":"min_price-desc", "text":"Min Price % Change"},
        {"value":"max_price-desc", "text":"Max Price % Change"},
        {"value":"total_quantity-desc", "text":"Quantity % Change"},
    ]
    return TRENDING_SORT_OPTIONS


def get_graph_checkboxes() -> list[dict[str, str]]:
    CHECKBOXES = [
        {"value":"avg_price", "text":"Average Price", "colour":"red"},
        {"value":"min_price", "text":"Minimum Price", "colour":"#00CC00"},
        {"value":"max_price", "text":"Maximum Price", "colour":"#3399FF"},
        {"value":"total_quantity", "text":"Quantity", "colour":"#FF00FF"},
    ]
    return CHECKBOXES