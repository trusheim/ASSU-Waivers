from django import template
import locale
register = template.Library()
 
# http://djangosnippets.org/snippets/552/
@register.filter()
def currency(value):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') # necessary in mod_python
    return locale.currency(value, grouping=True)