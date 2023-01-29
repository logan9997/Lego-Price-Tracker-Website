#miscellaneous functions.
import sys
import math

from django.shortcuts import redirect

sys.path.insert(1, r"C:\Users\logan\OneDrive\Documents\Programming\Python\apis\BL_API")

from my_scripts.database import *
from .config import *

db = DatabaseManagment()

def get_user_items(user_id, view):
    items = db.get_user_items(user_id, view)
    item_dicts = []
    for item in items:
        item_dict = {
        "item_id":item[0],
        "item_name":item[1],
        "year_released":item[2],
        "Item_type":item[3],
        "avg_price":item[4],
        "min_price":item[5],
        "max_price":item[6],
        "total_quantity":item[7],
        "img_path":f"App/images/{item[0]}.png",
        }

        if view == "portfolio":
            item_dict.update({
                "condition":item[8],
                "owned_quantity":item[9]
            })

        item_dicts.append(item_dict)

    return item_dicts

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


    order_convert = {"ASC":False, "DESC":True}
    order = order_convert[order[0]]
    if field[0] == "theme_name":
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

def user_items_get_requests(request) -> tuple[str, int, str]:
    #get requests
    graph_metric = request.GET.get("graph-metric", "avg_price")
    page = int(request.GET.get("page", 1))
    sort_field = request.GET.get("sort-field", "avg_price-desc")

    return graph_metric, page, sort_field


def user_items(request, view, user_id):

    context = {}
    
    items = get_user_items(user_id, view)

    graph_options = get_graph_options()
    sort_options = get_sort_options()

    graph_metric, page, sort_field = user_items_get_requests(request)

    for item in items:
        item["prices"] = [] ; item["dates"] = []
        for price_date_info in db.get_user_item_graph_info(user_id, item["item_id"], graph_metric, view):
            item["prices"].append(price_date_info[0])
            item["dates"].append(price_date_info[1])

    num_pages = [i+1 for i in range((len(items) // ITEMS_PER_PAGE ) + 1)]

    if sort_field != None:
        items = sort_items(items, sort_field)
        #keep selected sort field option as first <option> tag
        sort_options = sort_dropdown_options(sort_options, sort_field)

    graph_options = sort_dropdown_options(graph_options, graph_metric)

    total_items = len(items)

    items = items[(page - 1) * ITEMS_PER_PAGE : page * ITEMS_PER_PAGE]

    parent_themes = db.parent_themes(user_id, view)
    themes = recursive_get_sub_themes(user_id, parent_themes, [], -1, view)

    total_price = db.user_items_total_price(user_id, graph_metric, view)

    context.update({
        "items":items,
        "num_pages":num_pages,
        "sort_options":sort_options,
        "graph_options":graph_options,
        "themes":themes,
        "total_items":total_items,
        "total_price":total_price,
        "view":view,
    })

    return context
