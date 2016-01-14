"""
Methods to translate the schema variable names and types to desired language's names and types.
"""
from signals.logging import warn
import reserved_mappings


class BaseConverter(object):

    # Some field names are reserved in target language
    @classmethod
    def sanitize_field_name(cls, field_name):
        if field_name in cls.reserved_mappings:
            converted_name = cls.reserved_mappings[field_name]
            warn("{} is a reserved keyword in {} and is now being converted to {}"
                 .format(field_name, cls.language, converted_name))
            return converted_name
        else:
            return field_name

    # Changes a Python formatted variable name to conform to target language
    @classmethod
    def format_name(cls, python_variable_name, capitalize_first=False):
        words = python_variable_name.split('_')

        def upper_camel_case(words_to_capitalize):
            return "".join(word.capitalize() for word in words_to_capitalize)

        if capitalize_first:
            return upper_camel_case(words)
        else:
            return words[0] + upper_camel_case(words[1:])

    @classmethod
    def get_proper_name(cls, name, capitalize_first=False):
        proper_name = cls.sanitize_field_name(name)
        return cls.format_name(proper_name, capitalize_first=capitalize_first)


class ObjectiveCConverter(BaseConverter):
    language = "Objective-C"
    reserved_mappings = reserved_mappings.OBJC_RESERVED_MAPPINGS


class SwiftConverter(BaseConverter):
    language = "Swift"
    reserved_mappings = reserved_mappings.SWIFT_RESERVED_MAPPINGS
