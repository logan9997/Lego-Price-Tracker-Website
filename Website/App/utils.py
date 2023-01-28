#miscellaneous functions.
import sys
import math

sys.path.insert(1, r"C:\Users\logan\OneDrive\Documents\Programming\Python\apis\BL_API")

from my_scripts.database import *
from .config import *

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


def get_current_page(request, portfolio_items:list) -> int:
    #current page
    page = int(request.GET.get("page", 1)) 
    #number of pages, ITEMS_PER_PAGE items per page
    pages = math.ceil(len(portfolio_items) / ITEMS_PER_PAGE) 
    #boundaries for next and back page
    back_page = page - 1
    next_page = page + 1
    if page == pages: 
        next_page = page
    elif page == 1:
        back_page = page

    if back_page <= 0:
        back_page = 1

    print(back_page, page, next_page)

    return back_page, page, next_page


def get_change_password_error_message(rules:list[dict]) -> str:
    for rule in rules:
        rule = rule.popitem()
        if not rule[0]:
            return rule[1]


def sort_themes(field:str, order:str, sub_themes:list[str]) -> list[str]:


    order_convert = {"ASC":False, "DESC":True}
    order = order_convert[order[0]]
    print(order)
    if field[0] == "theme_name":
        return sorted(sub_themes, reverse=order)
    return sub_themes

    #elif field == "popularity":
    #elif field == "avg_growth":
    #else:

def get_watchlist_items(user_id) -> list[str]:
    items = db.get_watchlist_items(user_id)

    items = [{
        "item_id":item[0],
        "item_name":item[1],
        "year_released":item[2],
        "Item_type":item[3],
        "avg_price":item[4],
        "min_price":item[5],
        "max_price":item[6],
        "total_quantity":item[7],
        "img_path":f"App/images/{item[0]}.png",
    } for item in items]
    return items


def sort_watchlist_items(watchlist_items, sort) -> list[str]:

    sort_field = sort.split("-")[0]
    order = {"asc":False, "desc":True}[sort.split("-")[1]]
    

    watchlist_items = sorted(watchlist_items, key=lambda field:field[sort_field], reverse=order)
    return watchlist_items


def sort_sort_field_options(sort_options:list, sort_field:str) -> list[str]:

    selected_sort = [option for option in sort_options if option["value"] == sort_field][0]
    sort_options.insert(0, sort_options.pop(sort_options.index(selected_sort)))

    return sort_options

def sort_graph_options(graph_options:list[dict[str,str]], selected_field:str):

    selected_field = [option for option in graph_options if option["value"] == selected_field][0]
    graph_options.insert(0, graph_options.pop(graph_options.index(selected_field)))
    
    return graph_options

def recursive_get_sub_themes(user_id:int, parent_themes:list[str], themes:list[dict], indent) -> list[str]:

    indent += 1
    for theme in parent_themes:
        sub_themes = db.watchlist_sub_themes(user_id, theme[0])
        sub_themes = [t for t in sub_themes if t.count("~") == indent]
        print(theme)
        themes.append({
            "theme_path":theme[0],
            "count":theme[1],
            "total_price":theme[2],
            "sub_themes":sub_themes,
        })

        recursive_get_sub_themes(user_id, sub_themes, themes, indent)

    return themes

