import enum
import logging
from functools import wraps

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from flask import request

from GlobalStorage import list_meters, get_meter
from Stromzähler.Config import cookie_sign_key

import re


logging.getLogger(__name__)
class ClearanceLevel(enum.Enum):
    LOCAL = "Local"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

local_ip_pattern = re.compile("^(192\\.168\\.|localhost|127\\.0\\.0\\.1)")


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
            elif level == ClearanceLevel.HIGH and ("maintenance-"+uuid) in request.cookies:
                cookie = request.cookies["maintenance-"+uuid]
                # Check maintainer session cookie
                # TODO move pub key loading into global storage
                try:
                    cookie = jwt.decode(cookie, cookie_sign_key, issuer="smartmeter", algorithms="HS512")
                    if cookie["device_uuid"] != uuid:
                        raise jwt.InvalidTokenError
                    kwargs["user_id"] = cookie["id"]
                    return func(*args, **kwargs)
                except jwt.InvalidTokenError as e:
                    logging.warning(f"Invalid token from {request.host}")
                    return "Invalid token", 401
            elif level == ClearanceLevel.LOCAL:
                global local_ip_pattern
                if local_ip_pattern.match(request.host):
                    return func(*args, **kwargs)
                else:
                    logging.warning(f"Access from extern to local func from {request.host}")
                    return "Can only be accessed on the local network", 401
            logging.warning(f"No sec clearance for level [{level}] from {request.host}")
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
