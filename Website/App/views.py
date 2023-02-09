import random

from pprint import pprint

from datetime import (
    datetime as dt, 
    timedelta
)

from django.shortcuts import render, redirect
from .config import *
from .utils import *

from .forms import (
    AddItemToPortfolio, 
    PortfolioItemsSort, 
    LoginForm,
    SignupFrom,
    AddOrRemovePortfolioItem,
    ChangePassword,
    EmailPreferences,
    PersonalInfo,
    SearchSort,
)

from .models import (
    User,
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


def search_item(request, current_view):
    #get a list of all item ids that exist inside the database 
    item_ids = [item_id[0] for item_id in db.get_item_ids()] 
    
    #get item from the search bar, if it exists redirect to that items info page
    selected_item = request.POST.get("item_id")
    print(current_view)
    print(selected_item)
    if selected_item in item_ids:
        return redirect(f"http://127.0.0.1:8000/item/{selected_item}")
    return redirect(current_view)

def index(request):

    #set user_id if no user is logged in, get user_id from session
    if "user_id" not in request.session:
        request.session["user_id"] = -1
    user_id = request.session["user_id"]

    #get a list of all item ids that exist inside the database 
    item_ids = [item_id[0] for item_id in db.get_item_ids()] 

    #if the user has no recently viewed items create a new emtpy list to store items in the future
    if "recently-viewed" not in request.session and user_id == -1:
        request.session["recently-viewed"] = []

    #get the first x items from recently viewed
    recently_viewed_ids = request.session["recently-viewed"][:RECENTLY_VIEWED_ITEMS_NUM]

    #create dict for each recently viewed item 
    recently_viewed = [{
        "item_id":db.get_item_info(item_id)[0][0],
        "item_name":db.get_item_info(item_id)[0][1],
        "image_path":f"App/images/{db.get_item_info(item_id)[0][0]}.png",
    } for item_id in recently_viewed_ids]

    #duplicate list eg [1,2,3] -> [1,2,3,1,2,3] for infinite CSS carousel 
    '''recently_viewed.extend(recently_viewed)'''

    #set context. random_item_id used when user clicks 'view item info' in middle / about section
    context = {
        "recently_viewed":recently_viewed,
        "random_item_id":random.choice(item_ids),
        "trending":db.get_biggest_trends()[0]
    }

    #if user is logged in pass biggest portfolio changes to context 
    if "user_id" in request.session:
        biggest_portfolio_changes = [{
            "image_path":f"App/images/{_item[1]}.png",
            "item_id":_item[1],
            "item_name":_item[0],
            "condition":_item[2],
            "quantity_owned":_item[3],
            "change":_item[4],
            } for _item in db.biggest_portfolio_changes(user_id)[:9]]
        context.update({ #MIGHT ONLY NEED ONE
            "biggest_portfolio_changes_1":biggest_portfolio_changes[:len(biggest_portfolio_changes)//2],
            "biggest_portfolio_changes_2":biggest_portfolio_changes[len(biggest_portfolio_changes)//2:],

        })
        #adds the users username to context since they are logged in
        

    return render(request, "App/home.html", context=context)


def item(request, item_id):
    context = {}

    '''
    CHANGE IF USER IS LOGGED IN!!
    '''
    #if no recently viewed items, add item on current page to recently viewed items
    if "recently-viewed" not in request.session:
        request.session["recently-viewed"] = [item_id]
    else:
        #if item is already in recently viewed then revome it (will be added to i=0)
        if item_id in request.session["recently-viewed"]:
            request.session["recently-viewed"].remove(item_id)

        #add the item on the page to i=0
        request.session["recently-viewed"].insert(0, item_id)

        #if more than x recently-viewed items remove last / oldest item
        if len(request.session["recently-viewed"]) > RECENTLY_VIEWED_ITEMS_NUM:
            request.session["recently-viewed"].pop()

        #list is mutable, to save the changes to session
        request.session.modified = True


    if item_id != "favicon.ico":

        #STORE THIS IN DATABASE!
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

        add_error_msg = request.session.get("add_to_user_items_error_msg", "")

        context.update({
            "general_info":general_info,
            "image_path":f"App/images/{item_id}.png",
            "prices": prices,
            "dates":dates,
            "avg_prices":[price[1] for price in prices],
            "add_error_msg":add_error_msg
            # "parts_info":parts_info,
            # "sets_info":sets_info,
        })
    
        if "add_to_user_items_error_msg" in request.session:
            del request.session["add_to_user_items_error_msg"]

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


def search(request, theme_path='all'):

    if "user_id" in request.session:
        user_id = request.session["user_id"]
    else:
        user_id = -1

    page = 0

    if theme_path != "all":
        redirect_path = "".join([f"{sub_theme}/" for sub_theme in theme_path.split("/")][:-1])
        theme_path = theme_path.replace("all/", "")

    if theme_path == 'all':
        sub_themes = [theme[0].strip("'") for theme in db.get_parent_themes()]
        theme_items = [] 
    else:
        theme_items = db.get_theme_items(theme_path.replace("/", "~")) #return all sets for theme
        theme_items = format_item_info(theme_items, view="search", user_id=user_id)[page * SEARCH_ITEMS_PER_PAGE : (page+1) * SEARCH_ITEMS_PER_PAGE]
        if len(theme_items) == 0:
            print("REDIRECT - NO ITEMS []")
            #return redirect(f"http://127.0.0.1:8000/search/{redirect_path}")

        sub_themes = db.get_sub_themes(theme_path.replace("/", "~")) #return of all sub-themes (if any) for theme
        #split "~" (used to seperate sub themes in database) with 
        sub_themes = [theme[0].split("~")[0] for theme in sub_themes]
        #remove duplicates
        sub_themes = list(dict.fromkeys(sub_themes))

    graph_metric = "avg_price"

    for item in theme_items:
        item["prices"] = [] ; item["dates"] = []
        for price_date_info in db.get_item_graph_info(item["item_id"], graph_metric):
            item["prices"].append(price_date_info[0])
            item["dates"].append(price_date_info[1])

    sort_option = request.POST.get("sort-order")
    sort_options = get_search_sort_options()
    if sort_option != None:
        sort_options = sort_dropdown_options(sort_options, sort_option)

    if request.method == "POST": 
        if request.POST.get("form-type") != "theme-url":
            order = sort_option.split("-")[1]
            field = sort_option.split("-")[0]
            sub_themes = sort_themes(field, order, sub_themes)

    context = {
        "theme_path":theme_path,
        "sub_themes":sub_themes,
        "theme_items":theme_items,
        "sort_options":sort_options,
        "biggest_theme_trends":biggest_theme_trends()
    }
    
    return render(request, "App/search.html", context=context)


def login(request):
    context = {}

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
                request.session["user_id"] = user_id
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
    del request.session["user_id"]
    return redirect("login")


def join(request):

    context = {}

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
                    request.session["user_id"] = user_id
                    request.session.modified = True
                    return redirect("http://127.0.0.1:8000/")

                #set error messages depending on what the user did wrong in filling out the form
                context["signup_message"] = "Username / Email already exists"
            context["signup_message"] = "Passwords do not Match"

    #add the username to context which can only happen if the user is logged in
    return render(request, "App/join.html", context=context)


def user_items(request, view, user_id):

    context = {}

    items = db.get_user_items(user_id, view)

    items = format_item_info(items, view=view)

    graph_options = get_graph_options()
    sort_options = get_sort_options()

    if "url_params" in request.session:
        options = request.session["url_params"]
    else:
        options = {}

    graph_metric = options.get("graph-metric", "avg_price")
    current_page = int(options.get("page", 1))
    sort_field = options.get("sort-field", "avg_price-desc")

    current_page = check_page_boundaries(current_page, items)

    for item in items:
        item["prices"] = [] ; item["dates"] = []
        for price_date_info in db.get_item_graph_info(item["item_id"], graph_metric, view=view, user_id=user_id):
            item["prices"].append(price_date_info[0])
            item["dates"].append(price_date_info[1])

    
    num_pages = slice_num_pages(items, current_page)

    items = sort_items(items, sort_field)
    #keep selected sort field option as first <option> tag
    sort_options = sort_dropdown_options(sort_options, sort_field)

    graph_options = sort_dropdown_options(graph_options, graph_metric)

    total_unique_items = len(items)
    total_price = db.user_items_total_price(user_id, graph_metric, view)

    items = items[(current_page - 1) * ITEMS_PER_PAGE : int(current_page) * ITEMS_PER_PAGE]

    parent_themes = db.parent_themes(user_id, view)
    themes = recursive_get_sub_themes(user_id, parent_themes, [], -1, view)

    context.update({
        "items":items,
        "num_pages":num_pages,
        "sort_options":sort_options,
        "graph_options":graph_options,
        "themes":themes,
        "total_unique_items":total_unique_items,
        "total_price":total_price,
        "view":view,
        "current_page":current_page
    })

    return context


def portfolio(request):

    if "user_id" not in request.session or request.session["user_id"] == -1:
        return redirect("index")
    user_id = request.session["user_id"]

    view = request.GET.get("view")

    request.session["portfolio_view"] = view

    context = user_items(request, "portfolio", user_id)

    context["total_items"] = db.total_portfolio_items(user_id)
    context["view_param"] = f"/?view=items"

    if view == "trends":
        trends_graph_data = db.get_portfolio_price_trends(user_id)

        trends_graph_dates = [data[0] for data in trends_graph_data]
        trends_graph_prices = [data[1] for data in trends_graph_data]

        context["trends_graph_dates"] = trends_graph_dates
        context["trends_graph_prices"] = trends_graph_prices

    return render(request, "App/portfolio.html", context=context)


def view_POST(request, view):

    if "user_id" not in request.session or request.session["user_id"] == -1:
        return redirect("index")
    user_id = request.session["user_id"]

    items = db.get_user_items(user_id, view=view)

    portfolio_items = format_item_info(items, view=view)

    if request.POST.get("form-type") == "remove-or-add-portfolio-item":
        form = AddOrRemovePortfolioItem(request.POST)
        if form.is_valid():
            item_id = form.cleaned_data["item_id"]
            remove_or_add = form.cleaned_data["remove_or_add"]
            condition = form.cleaned_data["condition"][0]
            quantity = int(form.cleaned_data["quantity"])

            if remove_or_add == "-":
                quantity *= -1

            if (item_id, condition) in [(_item["item_id"], _item["condition"]) for _item in portfolio_items]:
                db.update_portfolio_item_quantity(user_id, item_id, condition, quantity)
            else:
                db.add_to_user_items(item_id, user_id, view, condition=condition, quantity=quantity)

    if "url_params" in request.session:
        for k, v in request.POST.items():
            request.session["url_params"][k] = v
    else:
        request.session["url_params"] = {}

    request.session.modified = True

    portfolio_view = ""
    if view == "portfolio":
        portfolio_view = "?view=" + request.session.get("portfolio_view", "items")
    print("portfolio_view", portfolio_view)
    return redirect(f"http://127.0.0.1:8000/{view}/" + portfolio_view)



def watchlist(request):

    if "user_id" not in request.session or request.session["user_id"] == -1:
        return redirect("index")
    user_id = request.session["user_id"]

    context = user_items(request, "watchlist", user_id)

    return render(request, "App/watchlist.html", context=context)


def add_to_user_items(request, item_id):

    view = request.POST.get("view-type")
    print(view)

    #view = request.session["view-type"]

    if view == "portfolio":
        form = AddItemToPortfolio(request.POST)
        if form.is_valid():
            condition = form.cleaned_data["condition"]
            quantity = form.cleaned_data["quantity"]
        else:print(form.errors)

    if "user_id" not in request.session or request.session["user_id"] == -1:
        return redirect("index")
    user_id = request.session["user_id"]

    user_item_ids = [_item[0] for _item in db.get_user_items(user_id, view)]
    portfolio_items_and_condition = db.get_portfolio_items_condition(user_id)

    if view == "portfolio":
        if (item_id, condition) not in portfolio_items_and_condition:
            db.add_to_user_items(user_id, item_id, view, condition=condition, quantity=quantity)
        else:
            request.session["add_to_user_items_error_msg"] = f"{item_id}, {condition} is already in your portfolio"
    else:
        if item_id not in user_item_ids:
            db.add_to_user_items(user_id, item_id, view)
        else:
            request.session["add_to_user_items_error_msg"] = f"{item_id} is already in your watchlist"

    return redirect(f"http://127.0.0.1:8000/item/{item_id}")


def profile(request):

    if "user_id" not in request.session or request.session["user_id"] == -1:
        return redirect("index")
    user_id = request.session["user_id"]

    context = {
        "username":User.objects.filter(user_id=user_id).values_list("username", flat=True)[0],
        "name":"NO NAME FIELD IN DATABASE",
        "email":User.objects.filter(user_id=user_id).values_list("email", flat=True)[0],
    }

    #SETTINGS
    print(request.POST.get("form-type"))
    
    if request.method == "POST":
        #-Change password
        if request.POST.get("form-type") == "change-password-form":
            form = ChangePassword(request.POST)
            if form.is_valid():
                old_password = form.cleaned_data["old_password"]
                new_password = form.cleaned_data["new_password"]
                confirm_password = form.cleaned_data["confirm_password"]
        
                #list of rules that must all return True for the password to be updated, with corrisponding error messages
                #to be displayed to the user.
                rules:list[dict] = [ 
                    {db.check_password_id_match(user_id, old_password):"'Old password' is incorrect"},
                    {new_password == confirm_password:"'New password' and 'Confirm password' do not match"},
                ]

                #add all dict keys to list, use all() method on list[bool] to see if all password change conditions are met
                if all([all(rule) for rule in rules]):
                    db.update_password(user_id, old_password, new_password)
                else:
                    #pass an error message to context, based on what condition was not satisfied
                    context["change_password_error_message"] = get_change_password_error_message(rules)

        #-Email preferences
        elif request.POST.get("form-type") == "email-preference-form":
            form = EmailPreferences(request.POST)
            if form.is_valid():
                email = form.cleaned_data["email"]
                preference = form.cleaned_data["preference"][0]
                db.update_email_preferences(user_id, email, preference)
                print(email, preference)
            else:print(form.errors)

        #-Change personal info
        elif request.POST.get("form-type") == "personal-details-form":
            form = PersonalInfo(request.POST)
            if form.is_valid():
                username = form.cleaned_data["username"]

                #update username is database
                db.change_username(user_id, username)

    #USER INFO

    #MEMBERSHIP 

    return render(request, "App/profile.html", context=context)