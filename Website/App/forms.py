from django import forms

class MinifigSelect(forms.Form):
    minifig_id = forms.CharField(max_length=10)



