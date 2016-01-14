"""
Reserved keywords in respective languages
"""

# More listed here: http://www.binpress.com/tutorial/objective-c-reserved-keywords/43
OBJC_RESERVED_MAPPINGS = {
    "auto": "isAuto",
    "default": "isDefault",
    "description": "theDescription",
    "id": "theID",
    "register": "theRegister",
    "restrict": "shouldRestrict",
    "super": "isSuper",
    "volatile": "isVolatile",
    "int": "isInt",
    "long": "isLong"
}

SWIFT_RESERVED_MAPPINGS = {
    "class": "_class",
    "func": "_func",
    "init": "_init"
}
