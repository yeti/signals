from signals.parser.fields import Field
from signals.logging import SignalsError


class API(object):
    CONTENT_TYPE_JSON = 'json'
    CONTENT_TYPE_FORM = 'form'
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basicauth"
    VALID_AUTH = [OAUTH2, BASIC_AUTH]

    def __init__(self, url_path, endpoint_json):
        self.url_path = url_path
        self.documentation = endpoint_json.get('doc')
        self.content_type = endpoint_json.get('content_type', self.CONTENT_TYPE_JSON)

        self.authorization = None
        self.authorization_optional = False
        self.set_authorization(endpoint_json)

    def set_authorization(self, endpoint_json):
        meta = endpoint_json.get('#meta')
        if meta:
            for authorization_attribute in meta.split(","):
                self.process_authorization_attribute(authorization_attribute.strip())

    def process_authorization_attribute(self, attribute):
        if attribute == Field.OPTIONAL:
            self.authorization_optional = True
        elif attribute in self.VALID_AUTH:
            self.authorization = attribute
        else:
            error_message = "Found invalid authorization attribute: {} for {}, exiting."
            raise SignalsError(error_message.format(attribute, self.url_path))


class GetAPI(API):
    RESOURCE_DETAIL = "detail"
    RESOURCE_LIST = "list"
    method = "get"

    def __init__(self, url_path, endpoint_json):
        super(GetAPI, self).__init__(url_path, endpoint_json)

        default_resource_type = self.RESOURCE_DETAIL if ":id" in url_path else self.RESOURCE_LIST
        self.resource_type = endpoint_json.get('resource_type', default_resource_type)

        self.parameters_object = endpoint_json.get('parameters')
        self.response_code = endpoint_json['response'].keys()[0]
        self.response_object = endpoint_json['response'][self.response_code]


class RequestResponseAPI(API):
    def __init__(self, url_path, endpoint_json):
        super(RequestResponseAPI, self).__init__(url_path, endpoint_json)
        self.request_object = endpoint_json['request']
        self.response_code = endpoint_json['response'].keys()[0]
        self.response_object = endpoint_json['response'][self.response_code]


class PostAPI(RequestResponseAPI):
    method = "post"


class PatchAPI(RequestResponseAPI):
    method = "patch"


class PutAPI(RequestResponseAPI):
    method = "put"


class DeleteAPI(API):
    method = "delete"
