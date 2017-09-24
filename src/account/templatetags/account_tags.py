from django import template
from django.contrib.auth.models import User
from reservierung import models

register = template.Library()

@register.filter(name="has_group")
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return group in user.groups.all()

@register.filter(name="is_creator")
def is_creator(user, creator):
    return user == creator
