import sys
import math

sys.path.insert(1, r"C:\Users\logan\OneDrive\Documents\Programming\Python\apis\BL_API")

from my_scripts.database import *
from .config import *

db = DatabaseManagment()

def format_item_info(items, **view):
    item_dicts = []
    print(items[1:2])
    for item in items:
        item_dict = {
        "item_id":item[0],
        "item_name":item[1],
        "year_released":item[2],
        "item_type":item[3],
        "avg_price":item[4],
        "min_price":item[5],
        "max_price":item[6],
        "total_quantity":item[7],
        "img_path":f"App/images/{item[0]}.png",
        }

        if view.get("view") == "portfolio":
            item_dict.update({
                "condition":item[8],
                "owned_quantity":item[9]
            })

        item_dicts.append(item_dict)

    return item_dicts


def format_theme_items(theme_items):
    theme_items_formated = [
        {
            "item_id":item[0],
            "item_type":item[1],
            "img_path":f"App/images/{item[0]}.png",
        }
    for item in theme_items]
    return theme_items_formated


def biggest_theme_trends():
    themes = db.biggest_theme_trends()
    themes_formated = [
        {
            "theme_path":theme[0],
            "change":theme[1]
            }
    for theme in themes]
    return {
        "biggest_winners":themes_formated[:5],
        "biggest_losers":themes_formated[-5:][::-1]
        }

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


def get_change_password_error_message(rules:list[dict]) -> str:
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

def recursive_get_sub_themes(user_id:int, parent_themes:list[str], themes:list[dict], indent:int, view:str) -> list[str]:

    indent += 1
    for theme in parent_themes:
        sub_themes = db.sub_themes(user_id, theme[0], view)
        sub_themes = [t for t in sub_themes if t.count("~") == indent]

        themes.append({
            "theme_path":theme[0],
            "count":theme[1],
            "total_price":theme[2],
            "sub_themes":sub_themes,
        })

        recursive_get_sub_themes(user_id, sub_themes, themes, indent, view)

    return themes


def slice_num_pages(num_pages, current_page):
    a = current_page - (PAGE_NUM_LIMIT // 2)
    b = current_page - (PAGE_NUM_LIMIT // 2) + PAGE_NUM_LIMIT  

    if b > len(num_pages):
        b = len(num_pages) -1
        a = b - PAGE_NUM_LIMIT
    if a < 0 :
        b -= a
        a = 0

    num_pages = num_pages[a:b]
    return num_pages



