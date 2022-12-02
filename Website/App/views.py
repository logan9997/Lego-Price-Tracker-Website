import sys

from django.shortcuts import render, redirect
from .forms import MinifigSelect


sys.path.insert(1, r"C:\Users\logan\OneDrive\Documents\Programming\Python\api's\BL_API")

from my_scripts.responses import * 
from my_scripts.database import *
from my_scripts.misc import get_star_wars_fig_ids

resp = Respose()


def update_prices_table():
    db = DatabaseManagment()


    figs = get_star_wars_fig_ids()
    figs = [resp.get_response_data(f"items/MINIFIG/{f}/price") for f in figs]
    db.add_price_info(figs)

def index(request):
    
    db = DatabaseManagment()
    if db.check_for_todays_date() == 0:
        update_prices_table()

    with open(r"App\Data\itemIDsList.txt", "r") as ids:
        minifig_ids = ids.readlines()
    minifig_ids = [m.rstrip("\n") for m in minifig_ids]

    selected_minfig = request.POST.get("minifig_id")
    if selected_minfig != None:
        return redirect(f"http://127.0.0.1:8000/{selected_minfig}")

    context = {
        "minifig_ids":minifig_ids
    }

    return render(request, "App/base.html", context=context)


def minifig_page(request, minifig_id):
    db = DatabaseManagment()
    context = {}

    if minifig_id != "favicon.ico":
        supersets = resp.get_response_data(f"items/MINIFIG/{minifig_id}/supersets")
        subsets = resp.get_response_data(f"items/MINIFIG/{minifig_id}/subsets")
        general_info = resp.get_response_data(f"items/MINIFIG/{minifig_id}")
        prices = db.get_minifig_prices(minifig_id)

        parts_info = [resp.get_response_data(f'items/PART/{p["entries"][0]["item"]["no"]["color"]}') for p in subsets]

        context.update({
            "supersets":supersets[0]["entries"],
            "subsets":subsets,
            "general_info":general_info,
            "prices": prices,
            "parts_info":parts_info,
        })



    return render(request, "App/minifig_page.html", context=context)

