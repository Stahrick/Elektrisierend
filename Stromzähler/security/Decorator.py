import enum
from functools import wraps
from flask import request

from GlobalStorage import list_meters, get_meter

import re

class ClearanceLevel(enum.Enum):
    LOCAL = "Local"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

local_ip_pattern = re.compile("^(192\\.168\\.|localhost)")


def clearance_level_required(level):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            uuid = str(kwargs.get("device_uuid"))
            if level == ClearanceLevel.LOW:
                return func(*args, **kwargs)
            elif level == ClearanceLevel.MEDIUM and request.headers.get('X-Client-Certificate'):
                # Perform certificate verification logic here
                cert = request.headers.get('X-Client-Certificate')
                return func(*args, **kwargs)
            elif level == ClearanceLevel.HIGH and ("maintainer-"+uuid) in request.cookies:
                cookie = request.cookies["maintainer-"+uuid]
                # Check maintainer session cookie
                return func(*args, **kwargs)
            elif level == ClearanceLevel.LOCAL:
                global local_ip_pattern
                if local_ip_pattern.match(request.host):
                    return func(*args, **kwargs)
                else:
                    return "Can only be accessed on the local network", 401
            return "No security clearance for this action", 401  # Unauthorized
        return wrapper
    return decorator


def device_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        uuid = str(kwargs.get("device_uuid"))
        if uuid is not None and uuid in list_meters():
            device = get_meter(uuid)
            kwargs["device"] = device  # Pass the device object to the route handler
            return f(*args, **kwargs)
        else:
            return "UUID not found", 404
    return decorated
