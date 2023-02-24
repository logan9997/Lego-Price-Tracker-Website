import sys
import math

sys.path.insert(1, r"C:\Users\logan\OneDrive\Documents\Programming\Python\apis\BL_API")

from my_scripts.database import *
from .config import *

DB = DatabaseManagment()

def clean_html_codes(string:str):
    codes = {
        "&#41;":")", 
        "&#40;":"("
    }

    for k, v in codes.items():
        if k in string:
            string = string.replace(k ,v)
    return string


def format_item_info(items, **kwargs):

    if kwargs.get("view") == "search":
        user_item_ids_portfolio = DB.is_item_in_user_items(kwargs.get("user_id"), "portfolio")
        user_item_ids_watchlist = DB.is_item_in_user_items(kwargs.get("user_id"), "watchlist")

    item_dicts = []
    print(len(items))
    for item in items:
        item_dict = {
        "item_id":item[0],
        "item_name":clean_html_codes(item[1]),
        "year_released":item[2],
        "item_type":item[3],
        "avg_price":item[4],
        "min_price":item[5],
        "max_price":item[6],
        "total_quantity":item[7],
        "img_path":f"App/images/{item[0]}.png",
        }

        if kwargs.get("view") == "portfolio":
            item_dict.update({
                "condition":item[8],
                "owned_quantity":item[9]
            })

        elif kwargs.get("view") == "search":
            item_dict.update({
                "in_portfolio":item[0] in user_item_ids_portfolio,
                "in_watchlist":item[0] in user_item_ids_watchlist,
            })

        if kwargs.get("price_trend", False) and kwargs.get("view") == "portfolio":
            item_dict.update({
                "price_change":item[10]
            })

        elif kwargs.get("price_trend", False):
             item_dict.update({
                "price_change":item[8]
            })           

        graph_data = kwargs.get("graph_data", False)

        if graph_data != False:
            graph_metric = graph_data.get("metric")
            user_id = graph_data.get("user_id")

            item_dict.update({
                "prices":append_item_graph_info(item[0], graph_metric=graph_metric, user_id=user_id)[0],
                "dates":append_item_graph_info(item[0], graph_metric=graph_metric, user_id=user_id)[1],
            })

        item_dicts.append(item_dict)

    return item_dicts


def format_theme_items(theme_items):
    theme_items_formated = [
        {
            "item_id":item[0],
            "item_type":item[1],
            "img_path":f"App/images/{item[0]}.png",
        } for item in theme_items
    ]

    return theme_items_formated


def biggest_theme_trends():
    themes = DB.biggest_theme_trends()
    themes_formated = [
        {
            "theme_path":theme[0],
            "change":theme[1]
        } for theme in themes
    ]

    losers_winners = {
        "biggest_winners":themes_formated[:5],
        "biggest_losers":themes_formated[-5:][::-1]
    }

    return losers_winners 

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

    return back_page, page, next_page


def get_change_password_error_message(rules:list[dict[str, str]]) -> str:
    for rule in rules:
        rule = rule.popitem()
        if not rule[0]:
            return rule[1]


def sort_themes(field:str, order:str, sub_themes:list[str]) -> list[str]:
    order_convert = {"asc":False, "desc":True}
    order = order_convert[order]
    if field == "theme_name":
        return sorted(sub_themes, reverse=order)
    return sub_themes

    #elif field == "popularity":
    #elif field == "avg_growth":
    #else:


def sort_items(items, sort) -> list[str]:
    sort_field = sort.split("-")[0]
    order = {"asc":False, "desc":True}[sort.split("-")[1]]
    items = sorted(items, key=lambda field:field[sort_field], reverse=order)
    return items


def sort_dropdown_options(options:list[dict[str,str]], field:str) -> list[dict[str,str]]:

    #loop through all options. If options["value"] matches to desired sort field, assign to variable
    selected_field = [option for option in options if option["value"] == field][0]

    #push selected element to front of list, remove its old position
    options.insert(0, options.pop(options.index(selected_field)))
    
    return options

def get_sub_themes(user_id:int, parent_themes:list[str], themes:list[dict], indent:int, view:str) -> list[str]:

    indent += 1
    for theme in parent_themes:
        sub_themes = DB.sub_themes(user_id, theme[0], view)
        sub_themes = [theme_path for theme_path in sub_themes if theme_path.count("~") == indent]

        themes.append({
            "theme_path":theme[0],
            "count":theme[1],
            "total_price":theme[2],
            "sub_themes":sub_themes,
        })

        get_sub_themes(user_id, sub_themes, themes, indent, view)

    return themes


def check_page_boundaries(current_page, items):
    if current_page > math.ceil(len(items) / ITEMS_PER_PAGE):
        current_page = 1
    return current_page


def slice_num_pages(items, current_page):
    num_pages = [i+1 for i in range((len(items) // ITEMS_PER_PAGE ) + 1)]

    list_slice_start = current_page - (PAGE_NUM_LIMIT // 2)
    list_slice_end = current_page - (PAGE_NUM_LIMIT // 2) + PAGE_NUM_LIMIT  

    if list_slice_end > len(num_pages):
        list_slice_end = len(num_pages) -1
        list_slice_start = list_slice_end - PAGE_NUM_LIMIT
    if list_slice_start < 0 :
        list_slice_end -= list_slice_start
        list_slice_start = 0

    num_pages = num_pages[list_slice_start:list_slice_end]

    #remove last page. if len(items) % != 0 by ITEMS_PER_PAGE -> blank page with no items
    if len(items) % ITEMS_PER_PAGE == 0:
        num_pages.pop(-1)

    return num_pages


def append_item_graph_info(item_id, graph_metric, **kwargs):
    prices = [] ; dates = []
    for price_date_info in DB.get_item_graph_info(item_id, graph_metric, view=kwargs.get("view"), user_id=kwargs.get("user_id")):
        prices.append(price_date_info[0])
        dates.append(price_date_info[1])
    return prices, dates
