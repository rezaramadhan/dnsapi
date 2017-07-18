from django import forms

class ZoneForm(forms.Form):
    f_hostname = forms.CharField(max_length=100, required=False)
    f_value = forms.CharField(max_length=100)
    f_ttl = forms.CharField(max_length=100, required=False)
    f_type = forms.CharField()
    f_priority = forms.CharField(required=False)
