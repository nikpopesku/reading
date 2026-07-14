from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    return mapping.get(key, 0)


@register.simple_tag(takes_context=True)
def querystring(context, **updates):
    params = context["request"].GET.copy()
    for key, value in updates.items():
        if value in (None, ""):
            params.pop(key, None)
        else:
            params[key] = value

    query_string = params.urlencode()
    return f"?{query_string}" if query_string else ""
