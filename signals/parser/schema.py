import json
from signals.parser.api import GetAPI, PostAPI, PutAPI, PatchAPI, DeleteAPI
from signals.parser.fields import Relationship, Field
from signals.logging import warn, progress

__author__ = 'rudy'


class Schema(object):
    def __init__(self, schema_path):
        self.data_objects = {}
        self.urls = []
        self.schema_path = schema_path

        progress("Parsing your schema file")
        with open(schema_path, "r") as schema_file:
            schema_json = json.loads(schema_file.read())
            self.create_objects(schema_json["objects"])
            self.create_apis(schema_json["urls"])

    def create_apis(self, urls_json):
        for url_json in urls_json:
            self.urls.append(URL(url_json))

    def create_objects(self, object_json):
        for data_object_json in object_json:
            object_name = data_object_json.keys()[0]
            data_object = DataObject(object_name, data_object_json[object_name])
            self.data_objects[data_object.name] = data_object


class DataObject(object):
    def __init__(self, name, json_fields):
        self.fields = []
        self.relationships = []
        self.name = name
        for field_name, field_attributes in json_fields.iteritems():
            self.create_field(field_name, field_attributes)

    def create_field(self, field_name, field_attributes):
        field_attributes = [field_attribute.strip() for field_attribute in field_attributes.split(",")]
        if Relationship.is_relationship(field_attributes):
            self.relationships.append(Relationship(field_name, field_attributes))
        else:
            self.fields.append(Field(field_name, field_attributes))

    def properties(self):
        return self.fields + self.relationships


class URL(object):
    URL_ENDPOINTS = {
        'get': GetAPI,
        'post': PostAPI,
        'put': PutAPI,
        'patch': PatchAPI,
        'delete': DeleteAPI
    }
    VALID_ATTRIBUTES = ['url', 'doc'] + URL_ENDPOINTS.keys()

    def __init__(self, url_json):
        self.url_path = url_json["url"]
        self.documentation = url_json.get("doc")
        self.parse_apis(url_json)
        self.validate_json(url_json)

    def parse_apis(self, url_json):
        # Check for each URL endpoint and create
        for endpoint, api_mapping in self.URL_ENDPOINTS.iteritems():
            api = None
            endpoint_json = url_json.get(endpoint)
            if endpoint_json is not None:
                api = api_mapping(self.url_path, endpoint_json)
            setattr(self, endpoint, api)

    def validate_json(self, url_json):
        # Verify there are no extra or improperly formatted attributes
        for attribute, value in url_json.iteritems():
            if attribute not in self.VALID_ATTRIBUTES:
                warn("Found unsupported attribute, {}, for url: {}".format(attribute, self.url_path))
