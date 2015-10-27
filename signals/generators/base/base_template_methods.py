from urlparse import urlparse
from signals.parser.api import API
from signals.parser.fields import Field


class BaseTemplateMethods(object):
    """
    Methods used while generating templates
    """
    @staticmethod
    def get_api_request_object(api):
        # We treat both request and parameter objects equally in method signatures
        return getattr(api, 'request_object', getattr(api, 'parameters_object', None))

    @staticmethod
    def get_object_name(request_object, upper_camel_case=False):
        first_letter = request_object.name[1]
        if upper_camel_case:
            first_letter = first_letter.upper()
        return first_letter + request_object.name[2:]

    @staticmethod
    def is_oauth(api):
        return api.authorization == API.OAUTH2 and not api.authorization_optional

    @staticmethod
    def get_media_fields(fields):
        return filter(lambda field: field.field_type in [Field.IMAGE, Field.VIDEO], fields)

    @staticmethod
    def is_url(url):
        parse_result = urlparse(url)
        return parse_result.scheme in ['http', 'https']
