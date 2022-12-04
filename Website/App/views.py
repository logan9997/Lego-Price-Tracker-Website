import sys

from django.shortcuts import render, redirect
from .forms import MinifigSelect


sys.path.insert(1, r"C:\Users\logan\OneDrive\Documents\Programming\Python\api's\BL_API")

from my_scripts.responses import * 
from my_scripts.database import *
from my_scripts.misc import get_star_wars_fig_ids, get_price_colour

resp = Respose()


def update_prices_table():
    db = DatabaseManagment()


    figs = get_star_wars_fig_ids()
    figs = [resp.get_response_data(f"items/MINIFIG/{f}/price") for f in figs]
    print(figs)

    db.add_price_info(figs)

def index(request):
    
    db = DatabaseManagment()
    #print(db.check_for_todays_date())
    if db.check_for_todays_date() == [(0,)]:
        print("UPDATING DB...")
        update_prices_table()
    else:
        print("DB UP TO DATE")

    with open(r"App\Data\itemIDsList.txt", "r") as ids:
        minifig_ids = ids.readlines()
    minifig_ids = [m.rstrip("\n") for m in minifig_ids]

    selected_minfig = request.POST.get("minifig_id")
    if selected_minfig != None:
        return redirect(f"http://127.0.0.1:8000/{selected_minfig}")

    context = {
        "minifig_ids":minifig_ids,
        "header":"HOME"
    }

    return render(request, "App/home.html", context=context)


def minifig_page(request, minifig_id):
    db = DatabaseManagment()
    context = {}

    if minifig_id != "favicon.ico":
        supersets = resp.get_response_data(f"items/MINIFIG/{minifig_id}/supersets")
        subsets = resp.get_response_data(f"items/MINIFIG/{minifig_id}/subsets")

        dates = db.get_dates(minifig_id)
        prices = db.get_minifig_prices(minifig_id)
        general_info = resp.get_response_data(f"items/MINIFIG/{minifig_id}")
        dates = [[c for c in d] for d in dates]
        dates = [d[0] for d in dates]
        print(dates)
        price_changes = {
            "avg_price":get_price_colour(prices[-1][1] - prices[0][1]),
            "min_price":get_price_colour(prices[-1][2] - prices[0][2]),
            "max_price":get_price_colour(prices[-1][3] - prices[0][3]),
        }

        print(prices)

        #provide default value as some items do not have any supersets
        sets_info = []
        if supersets != []:
            sets_info = [resp.get_response_data(f'items/SET/{s["item"]["no"]}') for s in supersets[0]["entries"] if resp.get_response_data(f'items/SET/{s["item"]["no"]}') != None]

        parts_info = [resp.get_response_data(f'items/PART/{p["entries"][0]["item"]["no"]}') for p in subsets]

        context.update({
            "general_info":general_info,
            "prices": prices,
            "price_changes":price_changes,
            "dates":dates,
            "avg_prices":[price[1] for price in prices],
            "parts_info":parts_info,
            "sets_info":sets_info,
            "header":minifig_id.upper(),
        })

    return render(request, "App/minifig_page.html", context=context)

