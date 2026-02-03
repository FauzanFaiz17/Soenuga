from django import template
from organization.helpers.permissions import has_permission

register = template.Library()

@register.simple_tag(takes_context=True)
def can(context, perm_codename, target=None):
    request = context.get("request")
    return has_permission(request.user, perm_codename, target)
