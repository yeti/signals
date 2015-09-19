import sys
import contextlib
from StringIO import StringIO
from signals.parser.schema import Schema


@contextlib.contextmanager
# Taken from http://stackoverflow.com/questions/5974557/testing-python-scripts
# which is from python's own test suite.
def captured_output(stream_name):
    """Run the 'with' statement body using a StringIO object in place of a
       specific attribute on the sys module.
       Example use (with 'stream_name=stdout'):

       with captured_stdout() as s:
           print("hello")
           assert s.getvalue() == "hello"
    """
    orig_stdout = getattr(sys, stream_name)
    setattr(sys, stream_name, StringIO())
    try:
        yield getattr(sys, stream_name)
    finally:
        setattr(sys, stream_name, orig_stdout)

def captured_stdout():
    return captured_output("stdout")

def captured_stderr():
    return captured_output("stderr")

def captured_stdin():
    return captured_output("stdin")

def create_dynamic_schema(objects_json, urls_json):
    schema = Schema("./tests/files/empty_schema.json")
    schema.create_objects(objects_json)
    schema.create_apis(urls_json)
    schema.validate_apis_and_objects()
    schema.add_relationship_objects()
    return schema