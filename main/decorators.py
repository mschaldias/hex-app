from functools import wraps
import zoneinfo
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone


def activate_timezone(view_func):
    """
        this decorator ensures that a view will 
        activate the local timezone before running
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            # get django_timezone from cookie
            tzname = request.COOKIES.get("django_timezone")
            if tzname:
                timezone.activate(zoneinfo.ZoneInfo(tzname))
            else:
                timezone.deactivate()
        except Exception as e:
            timezone.deactivate()
        
        response = view_func(request, *args, **kwargs)
        timezone.deactivate()
        return response
    
    return wrapper