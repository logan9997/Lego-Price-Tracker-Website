from django import template
from ..models import User

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