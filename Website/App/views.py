import random

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


def search_item(request, current_view):
    #get a list of all item ids that exist inside the database 
    item_ids = [item_id[0] for item_id in DB.get_item_ids()] 
    
    #get item from the search bar, if it exists redirect to that items info page
    selected_item = request.POST.get("item_id")

    if selected_item in item_ids:
        return redirect(f"http://127.0.0.1:8000/item/{selected_item}")
    return redirect(current_view)


def index(request):

    if "user_id" not in request.session:
        request.session["user_id"] = -1
    user_id = request.session["user_id"]

    item_ids = [item_id[0] for item_id in DB.get_item_ids()] 

    graph_options = get_graph_options()
    graph_metric = request.POST.get("graph-metric", "avg_price")
    graph_options = sort_dropdown_options(graph_options, graph_metric)

    #if the user has no recently viewed items create a new emtpy list to store items in the future
    if "recently-viewed" not in request.session and user_id == -1:
        request.session["recently-viewed"] = []

    recently_viewed_ids = request.session["recently-viewed"][:RECENTLY_VIEWED_ITEMS_NUM]
    recently_viewed = [DB.get_item_info(item_id)[0] for item_id in recently_viewed_ids]

    #duplicate list eg [1,2,3] -> [1,2,3,1,2,3] for infinite CSS carousel 
    '''recently_viewed.extend(recently_viewed)'''

    recently_viewed = format_item_info(recently_viewed, graph_data={"metric":graph_metric, "user_id":user_id})
    popular_items = format_item_info(DB.get_popular_items()[:10], popular_items=True, home_view="_popular_items", graph_data={"metric":graph_metric})
    new_items = format_item_info(DB.get_new_items()[:10], home_view="_new_items", graph_data={"metric":graph_metric})[:10]

    last_week = dt.today() - timedelta(days=7)
    last_week = last_week.strftime("%d/%m/%y")

    for popular_item in popular_items:
        popular_item["change"] = DB.get_weekly_item_metric_change(popular_item["item_id"], last_week, graph_metric)[0] 

    #set context. random_item_id used when user clicks 'view item info' in middle / about section
    context = {
        "graph_options":graph_options,
        "last_week":last_week,
        "popular_items":popular_items,
        "new_items":new_items,
        "recently_viewed":recently_viewed,
        "random_item_id":random.choice(item_ids),
        "show_graph":False
    }

    if user_id == -1 or len(DB.get_user_items(user_id, "portfolio")) == 0:
        context["portfolio_trending_items"] = False
        context["trending"] = format_item_info(DB.get_biggest_trends(), price_trend=True, graph_data={"metric":"avg_price", "user_id":user_id})
    else:
        context["portfolio_trending_items"] = True
        context["trending"] = format_item_info(DB.biggest_portfolio_changes(user_id), graph_data={"metric":"avg_price", "user_id":user_id})

    return render(request, "App/home.html", context=context)


def item(request, item_id):
 
    if "user_id" in request.session:
        user_id = request.session["user_id"]
    else:
        user_id = -1

    #stops view count being increased on refresh
    if "item_id" not in request.session or request.session.get("item_id") != item_id:
        request.session["item_id"] = item_id
        DB.increment_item_views(item_id)

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

    metric = request.POST.get("graph-metric", "avg_price")

    #[0] since list with one element (being the item)
    item_info = format_item_info(DB.get_item_info(item_id), graph_data={"metric":metric}, price_trend=True)[0]

    graph_options = sort_dropdown_options(get_graph_options(), metric)

    in_portfolio = DB.is_item_in_user_items(user_id, "portfolio", item_id)
    #convert tuple to dict 
    in_portfolio = [{"condition":{"N":"New", "U":"Used"}[_item[0]], "count":_item[1] } for _item in in_portfolio]

    in_watchlist = DB.is_item_in_user_items(user_id, "watchlist", item_id)
    if len(in_watchlist) == 1:
        in_watchlist = "Yes"
    else:
        in_watchlist = "No"

    total_watchers = DB.get_total_owners_or_watchers("watchlist", item_id) 
    total_owners = DB.get_total_owners_or_watchers("portfolio", item_id)

    context = {
        "show_graph":False,
        "item":item_info,
        "graph_options":graph_options,
        "in_portfolio":in_portfolio,
        "in_watchlist":in_watchlist,
        "total_watchers":total_watchers,
        "total_owners":total_owners,
    }


    if item_id != "favicon.ico":

        add_to_user_items_error_msg = request.session.get("add_to_user_items_error_msg", "")

        context.update({
            "add_to_user_items_error_msg":add_to_user_items_error_msg
        })
    
        if "add_to_user_items_error_msg" in request.session:
            del request.session["add_to_user_items_error_msg"]

    return render(request, "App/item.html", context=context)


def trending(request):

    winners = format_item_info(DB.get_biggest_trends(), price_trend=True, graph_data={"metric":"avg_price"})

    context = {
        "winners":winners,
        "show_graph":True,
        }
    

    return render(request, "App/trending.html", context=context)


def search(request, theme_path='all'):

    if "search" not in request.META.get('HTTP_REFERER'):
        request = clear_session_url_params(request, "graph-metric", "sort-field", "page", sub_dict="url_params")

    if "url_params" in request.session:
        for k, v in request.POST.items():
            request.session["url_params"][k] = v
        options = request.session["url_params"]
    else:
        request.session["url_params"] = {}
        options = {}

    request.session.modified = True

    graph_metric = options.get("graph-metric", "avg_price")
    sort_field = options.get("sort-field", "avg_price-desc")
    current_page = options.get("page", 1)

    if "user_id" in request.session:
        user_id = request.session["user_id"]
    else:
        user_id = -1

    if theme_path != "all":
        theme_path = theme_path.replace("all/", "")

    if theme_path == 'all':
        sub_themes = [theme[0].strip("'") for theme in DB.get_parent_themes()]
        theme_items = [] 
    else:
        theme_items = DB.get_theme_items(theme_path.replace("/", "~")) #return all sets for theme
        theme_items = format_item_info(theme_items, view="search",graph_data={"metric":graph_metric,"user_id":user_id} ,user_id=user_id)
        if len(theme_items) == 0:
            print("REDIRECT - NO ITEMS []")
            redirect_path = "".join([f"{sub_theme}/" for sub_theme in theme_path.split("/")][:-1])
            #return redirect(f"http://127.0.0.1:8000/search/{redirect_path}")

        sub_themes = DB.get_sub_themes(theme_path.replace("/", "~")) #return of all sub-themes (if any) for theme
        #split "~" (used to seperate sub themes in database) with 
        sub_themes = [theme[0].split("~")[0] for theme in sub_themes]
        #remove duplicates
        sub_themes = list(dict.fromkeys(sub_themes))

    current_page = check_page_boundaries(current_page, theme_items, SEARCH_ITEMS_PER_PAGE)
    page_numbers = slice_num_pages(theme_items, current_page, SEARCH_ITEMS_PER_PAGE)


    theme_sort_option = request.POST.get("sort-order", "theme_name-asc")
    theme_sort_options = get_search_sort_options()
    if theme_sort_option != None:
        theme_sort_options = sort_dropdown_options(theme_sort_options, theme_sort_option)

    graph_options = sort_dropdown_options(get_graph_options(), graph_metric)
    sort_options = sort_dropdown_options(get_sort_options(), sort_field)

    theme_items = sort_items(theme_items,sort_field)

    theme_items = theme_items[(current_page-1) * SEARCH_ITEMS_PER_PAGE : (current_page) * SEARCH_ITEMS_PER_PAGE]
    

    if request.method == "POST": 
        if request.POST.get("form-type") != "theme-url":
            order = theme_sort_option.split("-")[1]
            field = theme_sort_option.split("-")[0]
            sub_themes = sort_themes(field, order, sub_themes)

    context = {
        "show_graph":True,
        "current_page":current_page,
        "num_pages":page_numbers,
        "theme_path":theme_path,
        "sub_themes":sub_themes,
        "theme_items":theme_items,
        "theme_sort_options":theme_sort_options,
        "graph_options":graph_options,
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
            if DB.check_login(username, password):
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
                if not DB.if_username_or_email_already_exists(username, email):

                    #if the username or email does not already exist, add the new users details to database
                    DB.add_user(username, email, password)

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

    if view not in request.META.get('HTTP_REFERER'):
        request = clear_session_url_params(request, "graph-metric", "sort-field", "page", sub_dict="url_params")

    graph_options = get_graph_options()
    sort_options = get_sort_options()

    if "url_params" in request.session:
        options = request.session["url_params"]
    else:
        options = {}

    graph_metric = options.get("graph-metric", "avg_price")
    current_page = int(options.get("page", 1))
    sort_field = options.get("sort-field", "avg_price-desc")


    items = DB.get_user_items(user_id, view)
    items = format_item_info(items, view=view, graph_data={"metric":graph_metric, "user_id":user_id})

    current_page = check_page_boundaries(current_page, items, USER_ITEMS_ITEMS_PER_PAGE)
    num_pages = slice_num_pages(items, current_page, USER_ITEMS_ITEMS_PER_PAGE)

    items = sort_items(items, sort_field)
    #keep selected sort field option as first <option> tag
    sort_options = sort_dropdown_options(sort_options, sort_field)

    graph_options = sort_dropdown_options(graph_options, graph_metric)

    total_unique_items = len(items)
    total_price = DB.user_items_total_price(user_id, graph_metric, view)
    items = items[(current_page - 1) * USER_ITEMS_ITEMS_PER_PAGE : int(current_page) * USER_ITEMS_ITEMS_PER_PAGE]

    parent_themes = DB.parent_themes(user_id, view)
    themes = get_sub_themes(user_id, parent_themes, [], -1, view)

    context.update({
        "items":items,
        "num_pages":num_pages,
        "sort_options":sort_options,
        "graph_options":graph_options,
        "themes":themes,
        "total_unique_items":total_unique_items,
        "total_price":total_price,
        "view":view,
        "current_page":current_page,
        "show_graph":True
    })

    return context


def portfolio(request):

    if "user_id" not in request.session or request.session["user_id"] == -1:
        return redirect("index")
    user_id = request.session["user_id"]

    view = request.GET.get("view")

    request.session["portfolio_view"] = view

    context = user_items(request, "portfolio", user_id)

    context["total_items"] = DB.total_portfolio_items(user_id)
    context["view_param"] = f"/?view=items"

    if view == "trends":
        trends_graph_data = DB.get_portfolio_price_trends(user_id)

        trends_graph_dates = [data[0] for data in trends_graph_data]
        trends_graph_prices = [data[1] for data in trends_graph_data]

        context["trends_graph_dates"] = trends_graph_dates
        context["trends_graph_prices"] = trends_graph_prices

    return render(request, "App/portfolio.html", context=context)


def view_POST(request, view):

    if "user_id" not in request.session or request.session["user_id"] == -1:
        return redirect("index")
    user_id = request.session["user_id"]

    items = DB.get_user_items(user_id, view=view)

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
                DB.update_portfolio_item_quantity(user_id, item_id, condition, quantity)
            else:
                DB.add_to_user_items(item_id, user_id, view, condition=condition, quantity=quantity)

    if "url_params" in request.session:
        for k, v in request.POST.items():
            request.session["url_params"][k] = v
    else:
        request.session["url_params"] = {}

    request.session.modified = True

    portfolio_view = ""
    if view == "portfolio":
        portfolio_view = "?view=" + request.session.get("portfolio_view", "items")
    return redirect(f"http://127.0.0.1:8000/{view}/" + portfolio_view)



def watchlist(request):

    if "user_id" not in request.session or request.session["user_id"] == -1:
        return redirect("index")
    user_id = request.session["user_id"]

    context = user_items(request, "watchlist", user_id)

    return render(request, "App/watchlist.html", context=context)


def add_to_user_items(request, item_id):

    view = request.POST.get("view-type")


    if "user_id" not in request.session or request.session["user_id"] == -1:
        return redirect("index")
    user_id = request.session["user_id"]

    user_item_ids = [_item[0] for _item in DB.get_user_items(user_id, view)]
    portfolio_items_and_condition = DB.get_portfolio_items_condition(user_id)

    if view == "portfolio":

        form = AddItemToPortfolio(request.POST)
        if form.is_valid():
            condition = form.cleaned_data["condition"]
            quantity = form.cleaned_data["quantity"]

            if (item_id, condition) not in portfolio_items_and_condition:
                DB.add_to_user_items(user_id, item_id, view, condition=condition, quantity=quantity)
            else:
                condition = {"U":"Used", "N":"New"}[condition]
                request.session["add_to_user_items_error_msg"] = f"{item_id} ({condition}) is already in your portfolio"
    else:
        if item_id not in user_item_ids:
            DB.add_to_user_items(user_id, item_id, view)
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
                    {DB.check_password_id_match(user_id, old_password):"'Old password' is incorrect"},
                    {new_password == confirm_password:"'New password' and 'Confirm password' do not match"},
                ]

                #add all dict keys to list, use all() method on list[bool] to see if all password change conditions are met
                if all([all(rule) for rule in rules]):
                    DB.update_password(user_id, old_password, new_password)
                else:
                    #pass an error message to context, based on what condition was not satisfied
                    context["change_password_error_message"] = get_change_password_error_message(rules)

        #-Email preferences
        elif request.POST.get("form-type") == "email-preference-form":
            form = EmailPreferences(request.POST)
            if form.is_valid():
                email = form.cleaned_data["email"]
                preference = form.cleaned_data["preference"][0]
                DB.update_email_preferences(user_id, email, preference)

        #-Change personal info
        elif request.POST.get("form-type") == "personal-details-form":
            form = PersonalInfo(request.POST)
            if form.is_valid():
                username = form.cleaned_data["username"]

                #update username is database
                DB.change_username(user_id, username)

    #USER INFO

    #MEMBERSHIP 

    return render(request, "App/profile.html", context=context)