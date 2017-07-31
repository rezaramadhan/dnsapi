from django import forms

class RecordForm(forms.Form):
    f_hostname = forms.CharField(max_length=100, required=False)
    f_value = forms.CharField(max_length=100)
    f_ttl = forms.CharField(max_length=100, required=False)
    f_type = forms.CharField()
    f_priority = forms.CharField(required=False)

class ZoneForm(forms.Form):
    # Zone Data
    f_zonename = forms.CharField(max_length=100)
    f_zonetype = forms.CharField(max_length=100)
    f_zoneclass = forms.CharField(max_length=100)
    f_zonefilename = forms.CharField(max_length=100, required=False)
    # Forward Zone
    f_forwarders = forms.CharField(max_length=100, required=False)
    # Slave Zone
    f_masters = forms.CharField(max_length=100, required=False)
    # Master Zone
    f_directive = forms.CharField(max_length=100, required=False)
    f_authserv = forms.CharField(max_length=100, required=False)
    f_serialno = forms.CharField(max_length=100, required=False)
    f_slvrefresh = forms.CharField(max_length=100, required=False)
    f_slvretry = forms.CharField(max_length=100, required=False)
    f_slvexpire = forms.CharField(max_length=100, required=False)
    f_maxtimecache = forms.CharField(max_length=100, required=False)
    f_adminemail = forms.CharField(max_length=100, required=False)
    # Other Statements
    f_statement = forms.CharField(max_length=100, required=False)
