from django import template

register = template.Library()


@register.filter(name='division')
def division(value, arg):
    try:
        return int(value) // int(arg)
    except:
        return ''


@register.filter
def halve_list(value: list):
    try:
        length = len(value)
        if length % 2 == 0:
            half = length // 2
        else:
            half = len(value) // 2 + 1
        return value[:half], value[half:]
    except:
        return []
