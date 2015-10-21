"""
Creates list of Objective-C or Swift specific method parameter names and types.
"""


class Parameter(object):
    def __init__(self, name):
        self.name = name

    @staticmethod
    def has_id_field(request_object):
        return request_object and reduce(lambda x, y: x or y.name == 'id', request_object.fields, False)
