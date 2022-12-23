import sys
from datetime import datetime as dt, timedelta

from django.shortcuts import render, redirect
from django.core import serializers

from .forms import (
    AddItemToPortfolio, 
    PortfolioItemsSort, 
    LoginForm,
    SignupFrom
)

from .models import (
    Price,
    Portfolio,
    Item,
    User,
    Theme
)

sys.path.insert(1, r"C:\Users\logan\OneDrive\Documents\Programming\Python\api's\BL_API")

from my_scripts.responses import * 
from my_scripts.database import *
from my_scripts.misc import get_price_colour

resp = Response()
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
    # if db.check_for_todays_date() == [(0,)]:
    #     print("UPDATING DB...")
    #     #update_prices_table()
    # else:
    #     print("DB UP TO DATE")

    item_ids = [item_id[0] for item_id in db.get_item_ids()] 

    selected_minfig = request.POST.get("minifig_id")
    if selected_minfig in item_ids:
        return redirect(f"http://127.0.0.1:8000/item/{selected_minfig}")

    if "recently-viewed" not in request.session:
        request.session["recently-viewed"] = []

    context = {
        "header":"HOME",
        "recently_viewed":request.session["recently-viewed"]
    }

    return render(request, "App/home.html", context=context)


def item(request, item_id):
    context = {}

    #recently viewed items
    if "recently-viewed" not in request.session:
        request.session["recently-viewed"] = [item_id]
    else:
        if item_id in request.session["recently-viewed"]:
            request.session["recently-viewed"].remove(item_id)

        request.session["recently-viewed"].insert(0, item_id)

        if len(request.session["recently-viewed"]) > 10:
            request.session["recently-viewed"].pop()

        request.session.modified = True
    print(request.session["recently-viewed"])

    if item_id != "favicon.ico":
        # supersets = resp.get_response_data(f"items/MINIFIG/{item_id}/supersets")
        # subsets = resp.get_response_data(f"items/MINIFIG/{item_id}/subsets")

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
        # sets_info = []
        # if supersets != []:
        #     sets_info = [resp.get_response_data(f'items/SET/{s["item"]["no"]}') for s in supersets[0]["entries"] if resp.get_response_data(f'items/SET/{s["item"]["no"]}') != None]

        # parts_info = [resp.get_response_data(f'items/PART/{p["entries"][0]["item"]["no"]}') for p in subsets]

        # print(db.get_item_info(item_id)[0][2])
        general_info = {
            "item_id":db.get_item_info(item_id)[0][0],
            "name":db.get_item_info(item_id)[0][1],
            "year_released":db.get_item_info(item_id)[0][2],
        }

        context.update({
            "general_info":general_info,
            "image_path":f"App/images/{item_id}.png",
            "prices": prices,
            "dates":dates,
            "avg_prices":[price[1] for price in prices],
            # "parts_info":parts_info,
            # "sets_info":sets_info,
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
        "image_path":f"App/images/{m[1]}.png",

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


def theme(request, themes):
    #theme = "".join([theme + "/" for theme in themes])
    theme_items = db.get_theme_items(themes) #return all sets for theme
    sub_themes = db.get_sub_themes(themes) #return of all sub-themes (if any) for theme

    context = {
        "header":themes,
        "theme_items":theme_items,
        "sub_themes":sub_themes,
    }

    return render(request, "App/theme.html", context=context)


def login(request):

    context = {}
    #if not login attempts have been made set to 0
    if "login_attempts" not in request.session:
        request.session["login_attempts"] = 0

    #check if login block has exipred
    if "login_retry_date" not in request.session:
        login_blocked = False
    else:
        if dt.today() > request.session["login_retry_date"]: 
            login_blocked = False
        else:
            login_blocked = True

    #analyse login form
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid() and not login_blocked:
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            #check if username and password match, create new user_id session, del login_attempts session
            if db.check_login(username, password):
                user_id = User.objects.filter(username=username, password=password)
                user_id = user_id.values_list("user_id", flat=True)[0]
                request.session["user_id"] = user_id
                del request.session["login_attempts"]
                return redirect("http://127.0.0.1:8000/")
            else:
                print("no login")

            #if login not valid
            request.session["login_attempts"] += 1
            return redirect("http://127.0.0.1:8000/login/")



    #if max login attempts exceeded, then block user for 24hrs and display message on page
    if request.session["login_attempts"] >= 5:
        tommorow = dt.now() + timedelta(1)
        request.session["login_retry_date"] = tommorow
        context.update({"login_message":f"YOU HAVE ATTEMPTED LOGIN TOO MANY TIMES try again on {str(tommorow)}"})

    print("LOGIN ATTEMPTS",request.session["login_attempts"])



    return render(request, "App/login.html", context=context)


def join(request):

    if request.method == 'POST':
        form = SignupFrom(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            password_confirmation = form.cleaned_data["password_confirmation"]
            
            print(username, password, password_confirmation, email)
            if password == password_confirmation:
                if db.check_if_username_or_email_exists(username, email):
                    db.add_user(username, email, password)
                    user_id = User.objects.filter(username=username, password=password)
                    user_id = user_id.values_list("user_id", flat=True)[0]
                    request.session["user_id"] = user_id
                    return redirect("http://127.0.0.1:8000/")

    context = {}

    return render(request, "App/join.html", context=context)


def portfolio(request):
    if "user_id" not in request.session:
        user_id = "Null"
    else:
        user_id = request.session["user_id"]
    
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

    context = {
        "portfolio_items":portfolio_items,
    }
    #Add to portfolio
    if request.method == "POST":
        if request.POST.get("form-type") == "add-item-form":
            form = AddItemToPortfolio(request.POST)
            if form.is_valid():
                item_id = form.cleaned_data["item_id"]
                condition = form.cleaned_data["condition"]
                quantity = form.cleaned_data["quantity"]

                #if the item ID exists, add to database
                item_ids = [item_id[0] for item_id in db.get_item_ids()]
                if item_id in item_ids:

                    if (item_id, condition) in [(portfolio_item["item_id"], portfolio_item["condition"]) for portfolio_item in portfolio_items]:
                        db.update_portfolio_item_quantity(item_id, condition, quantity, user_id)
                    else:
                        db.add_to_portfolio(item_id, condition, quantity, user_id)
                    return redirect("http://127.0.0.1:8000/portfolio/")
        #sorting
        elif request.POST.get("form-type") == "sort-form":
            field_order_convert = {"ASC":False, "DESC":True}
            form = PortfolioItemsSort(request.POST)
            if form.is_valid():
                item_filter = form.cleaned_data["sort_field"][0]
                field_order = form.cleaned_data["field_order"][0]
                context["portfolio_items"] = sorted(context["portfolio_items"], key=lambda field:field[item_filter], reverse=field_order_convert[field_order])
            return render(request, "App/portfolio.html", context=context)

        

    return render(request, "App/portfolio.html", context=context)