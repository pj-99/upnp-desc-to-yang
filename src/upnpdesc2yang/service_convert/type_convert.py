from datetime import datetime


def upnp_to_yang_type(upnp_type):
    """
    Given a upnp type str, convert it to yang type
    """
    _upnp_to_yang_map = {
        "boolean": "boolean",
        "string": "string",
        "ui1": "uint8",
        "ui2": "uint16",
        "ui4": "uint32",
        "ui8": "uint64",
        "i1": "int8",
        "i2": "int16",
        "i4": "int32",
        "i8": "int64",
        "uri": "inet:uri",
        "datetime.tz": "yang:date-and-time",
        "bin.base64": "binary",
    }

    return _upnp_to_yang_map[upnp_type.lower()]


def upnp_type_to_python_type(upnp_type):
    """
    Given a upnp type str, convert it to python type
    """
    _upnp_to_python_map = {
        "boolean": bool,
        "ui1": int,
        "ui2": int,
        "ui4": int,
        "ui8": int,
        "i1": int,
        "i2": int,
        "i4": int,
        "i8": int,
        "string": str,
        "uri": str,
        "datetime.tz": datetime,
        "bin.base64": bytes,
    }
    return _upnp_to_python_map[upnp_type.lower()]
