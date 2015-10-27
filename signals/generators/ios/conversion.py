"""
Methods to translate the schema variable names and types to desired language's names and types.
"""

# More listed here: http://www.binpress.com/tutorial/objective-c-reserved-keywords/43
RESERVED_MAPPINGS = {
    "auto": "isAuto",
    "default": "isDefault",
    "description": "theDescription",
    "id": "theID",
    "register": "theRegister",
    "restrict": "shouldRestrict",
    "super": "isSuper",
    "volatile": "isVolatile"
}


# Changes a Python variable name to an Objective-C/Swift version
def python_to_objc_variable(python_variable_name, capitalize_first=False):
    words = python_variable_name.split('_')

    def upper_camel_case(words_to_capitalize):
        return "".join(word.capitalize() for word in words_to_capitalize)

    if capitalize_first:
        return upper_camel_case(words)
    else:
        return words[0] + upper_camel_case(words[1:])


# Some field names are reserved in Objective C
def sanitize_field_name(field_name):
    if field_name in RESERVED_MAPPINGS:
        return RESERVED_MAPPINGS[field_name]
    else:
        return field_name


def get_proper_name(name, capitalize_first=False):
    proper_name = sanitize_field_name(name)
    return python_to_objc_variable(proper_name, capitalize_first=capitalize_first)
