"""
Methods to translate the schema names and types to objective c variable names and types.
"""
from signals.parser.fields import Field

OBJC_DATA_TYPES = {
    Field.DATE: "NSDate*",
    Field.DATETIME: "NSDate*",
    Field.INTEGER: "NSNumber*",
    Field.DECIMAL: "NSNumber*",
    Field.FLOAT: "NSNumber*",
    Field.STRING: "NSString*",
    Field.TEXT: "NSString*",
    Field.BOOLEAN: "NSNumber*",
    Field.IMAGE: "UIImage*",
    Field.VIDEO: "NSURL*"
}

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


def get_objc_data_type(field):
    if field.array:
        return "NSArray*"
    else:
        return OBJC_DATA_TYPES[field.field_type]


# Changes a python variable name to an objective c version
def python_to_objc_variable(python_variable_name, capitalize_first=False):
    words = python_variable_name.split('_')

    def upper_camel_case(words):
        return "".join(word.capitalize() for word in words)

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
