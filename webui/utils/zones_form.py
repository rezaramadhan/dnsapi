from django import forms

class RecordForm(forms.Form):
    f_hostname = forms.CharField(max_length=100, required=False)
    f_value = forms.CharField(max_length=100)
    f_ttl = forms.CharField(max_length=100, required=False)
    f_type = forms.CharField()
    f_priority = forms.CharField(required=False)

class ZoneForm(forms.Form):
    f_directive = forms.CharField(max_length=100)
    f_authserv = forms.CharField(max_length=100)
    f_serialno = forms.CharField(max_length=100)
    f_slvrefresh = forms.CharField(max_length=100, required=False)
    f_slvretry = forms.CharField(max_length=100, required=False)
    f_slvexpire = forms.CharField(max_length=100, required=False)
    f_maxtimecache = forms.CharField(max_length=100, required=False)
    f_adminemail = forms.CharField(max_length=100, required=False)
    f_zonename = forms.CharField(max_length=100)
    f_zonetype = forms.CharField(max_length=100)
