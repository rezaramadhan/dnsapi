import re

from django import template
from django.core.urlresolvers import reverse, NoReverseMatch

register = template.Library()


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, basestring):
        return text.startswith(starts)
    return False

@register.filter('regexmatch')
def regexmatch(text, regex):

    match = re.search(regex, text)
    print 'debug : '+text+' - '+regex
    print 'debug : '+str(match)
    if match:
        return True
    else :
        return False
