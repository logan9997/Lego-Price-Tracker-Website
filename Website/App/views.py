import sys, math, random
from datetime import datetime as dt, timedelta

from django.shortcuts import render, redirect
from .config import * 
from .utils import *

from .forms import (
    AddItemToPortfolio, 
    PortfolioItemsSort, 
    LoginForm,
    SignupFrom,
    DeletePortfolioItem,
    PortfolioPageNavigation,
)

from .models import (
    Price,
    Portfolio,
    Item,
    User,
    Theme
)


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

    if "user_info" not in request.session:
        request.session["user_info"] = {"user_id":-1, "recently-viewed":[]}

    #get a list of all item ids that exist inside the database 
    item_ids = [item_id[0] for item_id in db.get_item_ids()] 
    
    #get item from the search bar, if it exists redirect to that items info page
    selected_item = request.POST.get("minifig_id")
    if selected_item in item_ids:
        return redirect(f"http://127.0.0.1:8000/item/{selected_item}")

    #if the user has no recently viewed items create a new emtpy list to store items in the future
    if "recently-viewed" not in request.session["user_info"]:
        request.session["user_info"]["recently-viewed"] = []

    #get the first x items from recently viewed
    recently_viewed_ids = request.session["user_info"]["recently-viewed"][:RECENTLY_VIEWED_ITEMS_NUM]

    #create dict for each recently viewed item 
    recently_viewed = [{
        "item_id":db.get_item_info(item_id)[0][0],
        "item_name":db.get_item_info(item_id)[0][1],
        "image_path":f"App/images/{db.get_item_info(item_id)[0][0]}.png",
    } for item_id in recently_viewed_ids]

    #duplicate list eg [1,2,3] -> [1,2,3,1,2,3] for infinite CSS carousel 
    recently_viewed.extend(recently_viewed)

    #set context. random_item_id used when user clicks 'view item info' in middle / about section
    context = {
        "recently_viewed":recently_viewed,
        "random_item_id":random.choice(item_ids),
        "trending":db.get_biggest_trends()[0]
    }

    #if user is logged in pass biggest portfolio changes to context 
    if "user_id" in request.session["user_info"]:
        biggest_portfolio_changes = [{
            "image_path":f"App/images/{_item[1]}.png",
            "item_id":_item[1],
            "item_name":_item[0],
            "condition":_item[2],
            "quantity_owned":_item[3],
            "change":_item[4],
            } for _item in db.biggest_portfolio_changes(request.session["user_info"]["user_id"])[:9]]
        context.update({ #MIGHT ONLY NEED ONE
            "biggest_portfolio_changes_1":biggest_portfolio_changes[:len(biggest_portfolio_changes)//2],
            "biggest_portfolio_changes_2":biggest_portfolio_changes[len(biggest_portfolio_changes)//2:],

        })
        #adds the users username to context since they are logged in
        

    return render(request, "App/home.html", context=context)


def item(request, item_id):
    context = {}

    user_info = request.session["user_info"]

    #if no recently viewed items, add item on current page to recently viewed items
    if "recently-viewed" not in request.session:
        user_info["recently-viewed"] = [item_id]
    else:
        #if item is already in recently viewed then revome it (will be added to i=0)
        if item_id in user_info["recently-viewed"]:
            user_info["recently-viewed"].remove(item_id)

        #add the item on the page to i=0
        user_info["recently-viewed"].insert(0, item_id)

        #if more than x recently-viewed items remove last / oldest item
        if len(user_info["recently-viewed"]) > RECENTLY_VIEWED_ITEMS_NUM:
            user_info["recently-viewed"].pop()

        #list is mutable, to save the changes to session
        request.session.modified = True


    if item_id != "favicon.ico":
        # supersets = resp.get_response_data(f"items/MINIFIG/{item_id}/supersets")
        # subsets = resp.get_response_data(f"items/MINIFIG/{item_id}/subsets")

        prices = db.get_minifig_prices(item_id)

        #get all dates of each price record, replace "-" with "/"
        dates = db.get_dates(item_id)
        dates = [d[0].replace("-", "/") for d in dates]

        #if there IS price records then set colours (red/green/gray) for each price (avg,min,max)
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

        #general info dict to be added to context
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
        "losers":losers,
        "winners":winners,
        }
    

    return render(request, "App/trending.html", context=context)


def search(request, theme_path="all"):

    if theme_path == "all":
        sub_themes = [theme[0].strip("'") for theme in db.get_parent_themes()]
        theme_items = [] 
    else:
        theme_items = db.get_theme_items(theme_path.replace("/", "~")) #return all sets for theme
        #get all sub themes (if any)
        sub_themes = db.get_sub_themes(theme_path.replace("/", "~")) #return of all sub-themes (if any) for theme
        #split "~" (used to seperate sub themes in database) with 
        sub_themes = [theme[0].split("~")[0] for theme in sub_themes]
        #remove duplicates
        sub_themes = list(dict.fromkeys(sub_themes))

    context = {
        "sub_themes":sub_themes,
        "theme_items":theme_items,
    }
    

    return render(request, "App/search.html", context=context)


def login(request):
    context = {}

    if "user_info" not in request.session:
        request.session["user_info"] = {"user_id":-1, "recently-viewed":[]}

    #if not login attempts have been made set to 0
    if "login_attempts" not in request.session:
        request.session["login_attempts"] = 0

    #check if login block has exipred
    if "login_retry_date" not in request.session:
        login_blocked = False
    else:
        #format login_retry_date into datetime format to compare with todays date
        login_retry_date = datetime.datetime.strptime(request.session["login_retry_date"].strip('"'), '%Y-%m-%d %H:%M:%S')
        if dt.today() > login_retry_date: 
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
                #filter database to find user with corrisponding username and password
                user = User.objects.filter(username=username, password=password)

                #get the user_id field from user_id
                user_id = user.values_list("user_id", flat=True)[0]

                #set the user_id in session to the user that just logged in, reset login attempts
                request.session["user_info"]["user_id"] = user_id
                request.session["login_attempts"] = 0

                #redirect to home page id login successful
                return redirect("http://127.0.0.1:8000/")
            else:
                #display login error message, increment login_attempts 
                context.update({"login_message":"Username and Password do not match"})
                request.session["login_attempts"] += 1



    #if max login attempts exceeded, then block user for 24hrs and display message on page
    if request.session["login_attempts"] >= 4:
        if not login_blocked:
            #if the useer does not have a login time restriction, create a new one
            tommorow = dt.strptime(str(dt.now() + timedelta(1)).split(".")[0], "%Y-%m-%d %H:%M:%S")
            
            #add the new date to session in json format otherwise serializer error
            request.session["login_retry_date"] = json.dumps(tommorow, default=str)

        #if logim block date already set then display login error message, showing when the user can try to login again
        login_retry_date = request.session["login_retry_date"]
        context.update({"login_message":["YOU HAVE ATTEMPTED LOGIN TOO MANY TIMES:", f"try again on {login_retry_date}"]})

    #add the username to context which can only happen if the user is logged in
    

    return render(request, "App/login.html", context=context)


def logout(request):
    #when logging out delete user_id. 

    '''
    rework sessions for specific user, need to associate recently viewed with a user_id
    otherwise recently viewed items still show after logging out
    '''
    if "user_info" in request.session:
        del request.session["user_info"]
    return redirect("login")


def join(request):

    context = {}

    if "user_info" not in request.session:
        request.session["user_info"] = {"user_id":-1, "recently-viewed":[]}

    if request.method == 'POST':
        form = SignupFrom(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            password_confirmation = form.cleaned_data["password_confirmation"]
            
            #check if passwords match other wise need to display message showing it
            if password == password_confirmation:

                #check if the username / email already exists inside the database, cannot be duplicates
                if not db.if_username_or_email_already_exists(username, email):

                    #if the username or email does not already exist, add the new users details to database
                    db.add_user(username, email, password)

                    #get the new users id to add to session
                    user = User.objects.filter(username=username, password=password)
                    user_id = user.values_list("user_id", flat=True)[0]
                    request.session["user_info"]["user_id"] = user_id
                    request.session.modified = True
                    return redirect("http://127.0.0.1:8000/")

                #set error messages depending on what the user did wrong in filling out the form
                context = {"signup_message":"Username / Email already exists"}
            context = {"signup_message":"Passwords do not Match"}

    #add the username to context which can only happen if the user is logged in
    

    return render(request, "App/join.html", context=context)


def portfolio(request):

    #if no view is selected, default to view=items, page=1
    if "items" not in request.GET.get("view", "") and "trends" not in request.GET.get("view", ""):
        page = int(request.GET.get("page", 1))
        return redirect(f"http://127.0.0.1:8000/portfolio/?view=items&page={page}")

    user_id = request.session["user_info"]["user_id"]

    context = {}
    #if user_id not in session, logged in = False
    if user_id != -1:
        #get all items owned by the logged in user
        portfolio_items = get_portfolio_items(user_id)

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

        #pass items for specific page
        portfolio_items = portfolio_items[ITEMS_PER_PAGE*(page-1):ITEMS_PER_PAGE*page]

        #add all portfolio items. Add all existing items_ids for adding to portfolio
        context.update({
            "portfolio_items":portfolio_items[:ITEMS_PER_PAGE],
            "item_ids":[item_id[0] for item_id in db.get_item_ids()],
        })

        print(context["portfolio_items"])

        #if view is trends (showing graph)
        if request.GET.get("view") == "trends":
            #get prices and dates for trends in portfolio
            portfolio_trends = db.total_portfolio_price_trend(user_id)
            portfolio_trend_dates = [portfolio_item[1] for portfolio_item in portfolio_trends]
            portfolio_trend_prices = [portfolio_item[0] for portfolio_item in portfolio_trends]

            #add prices and dates in seperate lists in context
            context.update({
                "portfolio_trend_dates":portfolio_trend_dates,
                "portfolio_trend_prices":portfolio_trend_prices,
                })
        
        context = {
            "next_page":next_page,
            "back_page":back_page,  
            "current_page":page    
        }


    return render(request, "App/portfolio.html", context=context)


def portfolio_POST(request, page):
    page -= 1
    print(page)
    #Add to portfolio
    context = {}
    user_id = request.session["user_info"]["user_id"]
    portfolio_items = get_portfolio_items(user_id)
    

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
                    
                    #if the item_id with the same condition ('N' / 'U') in portfolio increment quantity
                    if (item_id, condition) in [(portfolio_item["item_id"], portfolio_item["condition"]) for portfolio_item in portfolio_items]:
                        db.update_portfolio_item_quantity(item_id, condition, quantity, user_id)
                    
                    #if item + quantity not in portfolio, add new item entry
                    else:
                        db.add_to_portfolio(item_id, condition, quantity, user_id)
                    return redirect(f"http://127.0.0.1:8000/portfolio/?view=items&page={page}")
            else:
                print(form.errors)

        #SORTING
        elif request.POST.get("form-type") == "sort-form":
            field_order_convert = {"ASC":False, "DESC":True}
            form = PortfolioItemsSort(request.POST)
            if form.is_valid():
                item_filter = form.cleaned_data["sort_field"][0]
                field_order = form.cleaned_data["field_order"][0]

                #update portfolio items order dependant on the sort field from the form
                context["portfolio_items"] = sorted(context["portfolio_items"], key=lambda field:field[item_filter], reverse=field_order_convert[field_order])
            #return render(request, "App/portfolio.html", context=context)
            return redirect(f"http://127.0.0.1:8000/portfolio/?view=items&page={page}")

        #REMOVE ITEM
        elif request.POST.get("form-type") == "delete-item-form":
            form = DeletePortfolioItem(request.POST)
            if form.is_valid():
                item_id = form.cleaned_data["item_to_delete"].split(",")[0]
                condition = form.cleaned_data["item_to_delete"].split(",")[1]
                delete_quantity = form.cleaned_data["delete_quantity"]

                #decrement quantity of item, if quantity < 1, remove from portfolio
                db.decrement_portfolio_item_quantity(item_id, user_id, condition, delete_quantity)
                return redirect(f"http://127.0.0.1:8000/portfolio/?view=items&page={page}")

    return redirect("portfolio")


def watchlist(request):

    user_id = request.session["user_info"]["user_id"]

    context = {}

    return render(request, "App/watchlist.html", context=context)