import sys

from django.shortcuts import render, redirect

sys.path.insert(1, r"C:\Users\logan\OneDrive\Documents\Programming\Python\api's\BL_API")

from my_scripts.responses import * 
from my_scripts.database import *
from my_scripts.misc import get_star_wars_fig_ids, get_price_colour

resp = Respose()
db = DatabaseManagment()


def update_prices_table():
    #return  (item_ids, type) grouped by item id
    items = db.group_by_items()[500:700]
    
    #update prices
    type_convert = {"M":"MINIFIG", "S":"SET"}
    for item in items:
        item_info = resp.get_response_data(f"items/{type_convert[item[1]]}/{item[0]}/price")
        db.add_price_info(item_info)


def index(request):
    
    #print(db.check_for_todays_date())
    if db.check_for_todays_date() == [(0,)]:
        print("UPDATING DB...")
        #update_prices_table()
    else:
        print("DB UP TO DATE")

    item_ids = [item_id[0] for item_id in db.get_item_ids()] 

    selected_minfig = request.POST.get("minifig_id")
    if selected_minfig in item_ids:
        return redirect(f"http://127.0.0.1:8000/item/{selected_minfig}")

    context = {
        "header":"HOME"
    }

    return render(request, "App/home.html", context=context)


def item(request, item_id):
    context = {}

    if item_id != "favicon.ico":
        supersets = resp.get_response_data(f"items/MINIFIG/{item_id}/supersets")
        subsets = resp.get_response_data(f"items/MINIFIG/{item_id}/subsets")

        prices = db.get_minifig_prices(item_id)
        dates = db.get_dates(item_id)
        dates = [[c for c in d] for d in dates]
        dates = [d[0] for d in dates]
        dates = [d.replace("-", "/") for d in dates]

        if len(prices) > 0:
            context.update({
                "avg_price":get_price_colour(prices[-1][1] - prices[0][1]),
                "min_price":get_price_colour(prices[-1][2] - prices[0][2]),
                "max_price":get_price_colour(prices[-1][3] - prices[0][3]),
            })

        #provide default value as some items do not have any supersets
        sets_info = []
        if supersets != []:
            sets_info = [resp.get_response_data(f'items/SET/{s["item"]["no"]}') for s in supersets[0]["entries"] if resp.get_response_data(f'items/SET/{s["item"]["no"]}') != None]

        parts_info = [resp.get_response_data(f'items/PART/{p["entries"][0]["item"]["no"]}') for p in subsets]

        print(db.get_item_info(item_id)[0][2])

        general_info = {
            "item_id":db.get_item_info(item_id)[0][0],
            "name":db.get_item_info(item_id)[0][1],
            "year_released":db.get_item_info(item_id)[0][2],
            "thumbnail_url":db.get_item_info(item_id)[0][3]
        }

        context.update({
            "general_info":general_info,
            "prices": prices,
            "dates":dates,
            "avg_prices":[price[1] for price in prices],
            "parts_info":parts_info,
            "sets_info":sets_info,
            "header":item_id.upper(),
        })

    return render(request, "App/item.html", context=context)


def trending(request):

    losers, winners = db.get_biggest_trends()
    #create list[dict] of all of the biggest winners / losers
    winners = [{
        "name":m[0],
        "id":m[1],
        "change":m[2],
        "img_url":db.get_thumbnail_url(m[1])[0][0]
    } for m in winners]


    context = {
        "header":"Trending",
        "losers":losers,
        "winners":winners,
        }

    return render(request, "App/trending.html", context=context)


def search(request):
    #get theme_path, thumbnail_url for each theme (type = 'S')
    themes = [theme for theme in db.get_parent_themes()]

    context = {
        "header":"Search",
        "theme_details":themes,
    }

    return render(request, "App/search.html", context=context)


def theme_page(request, theme_path):
    #get item_id, type for all items equal to theme_path
    theme_items = db.get_theme_items(theme_path)

    context = {
        "header":theme_path,
        "theme_items":theme_items,
    }

    return render(request, "App/theme.html", context=context)