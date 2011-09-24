from django import template
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') # necessary in mod_python
register = template.Library()
 
# http://djangosnippets.org/snippets/552/
@register.filter()
def currency(value):
    return locale.currency(value, grouping=True)