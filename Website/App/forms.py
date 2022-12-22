from django import forms

class ItemSelect(forms.Form):
    item_id = forms.CharField(max_length=20)


class AddItemToPortfolio(forms.Form):
    item_id = forms.CharField(max_length=20)
    condition = forms.CharField(max_length=1)
    quantity = forms.IntegerField()


class PortfolioItemsSort(forms.Form):
    sort_field = forms.MultipleChoiceField(choices=(
        ("item_name", "item_name"), ("condition", "condition")
    ))
    field_order = forms.MultipleChoiceField(choices=(
        ("ASC", "ASC"), ("DESC", "DESC")
    ))


class LoginForm(forms.Form):
    username = forms.CharField(max_length=16)
    password = forms.CharField(max_length=22)


class SignupFrom(forms.Form):
    email = forms.CharField(max_length=60)
    username = forms.CharField(max_length=16)
    password = forms.CharField(max_length=22)
    password_confirmation = forms.CharField(max_length=22)