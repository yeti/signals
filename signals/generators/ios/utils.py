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

def get_objc_data_type(field_type):
    if field_type == Field.ARRAY:
        return "NSArray*"
    else:
        return OBJC_DATA_TYPES[field_type]


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
    if field_name == "id":
        return "theID"
    elif field_name == "description":
        return "theDescription"
    else:
        return field_name


# Remove the $ in front of data object names and upper camel case the name
def get_object_name(obj):
    return obj[1].upper() + obj[2:]
