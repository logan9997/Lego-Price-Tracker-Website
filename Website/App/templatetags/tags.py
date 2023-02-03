from django import template
from ..models import User
from ..utils import recursive_get_sub_themes

register = template.Library()

#add login status to base.html to either display (logout) / (login + join) in the nav bar
@register.simple_tag(takes_context=True)
def check_login_status(context, request):
    try:
        if request.session["user_id"] != -1:
            context["logged_in"] = True
        else:
            context["logged_in"] = False
    except KeyError:
        context["logged_in"] = False
    return ''


@register.simple_tag(takes_context=True)
def add_username_email_to_context(context, request):
    try: 
        user_id = request.session["user_id"]
        if user_id != -1:
            user_details = User.objects.filter(user_id=user_id)
            context["username"] = user_details.values_list("username", flat=True)[0]
            context["email"] = user_details.values_list("email", flat=True)[0]
    except KeyError:
        return ''
    return ''


@register.filter
def replace_underscore(string):
    return string.replace("_", " ")

@register.filter
def replace_forward_slash(string):
    if string == "/":
        return "index"

    return string.replace("/", "")

@register.filter
def count_theme_indent(theme_path:str):
    indent = theme_path.count("~")
    parent_theme = theme_path.split("~")[0]
    desire_indent = 2

    if indent <= desire_indent and parent_theme in theme_path:
        return "-"*(indent*3) + theme_path.split("~")[-1].replace("_", " ").replace("~", " ")
    return ''


@register.filter
def capitalise(string:str):
    return string.capitalize()
