import sys

from django.shortcuts import render, redirect
from .forms import MinifigSelect


sys.path.insert(1, r"C:\Users\logan\OneDrive\Documents\Programming\Python\api's\BL_API")

from my_scripts.responses import * 

resp = Respose()

def index(request):

    minifig_ids = ["sw0001a", "sw0001b", "sw0001c"]

    selected_minfig = request.POST.get("minifig_id")
    if selected_minfig != None:
        return redirect(f"http://127.0.0.1:8000/{selected_minfig}")

    context = {
        "minifig_ids":minifig_ids
    }

    return render(request, "App/base.html", context=context)


def minifig_page(request, minifig_id):

    supersets = resp.get_response_data(f"items/MINIFIG/{minifig_id}/supersets")[0]["entries"]
    subsets = resp.get_response_data(f"items/MINIFIG/{minifig_id}/subsets", display=True)

    context = {
        "minifig_id":minifig_id,
        "supersets":supersets,
        "subsets":subsets,
    }

    return render(request, "App/minifig_page.html", context=context)

