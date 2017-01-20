from unittest import TestCase

from jsonschema.exceptions import SchemaError

from scrapy_jsonschema.item import JsonSchemaItem
from . import valid_schema, invalid_schema


class ValidSchemaTestCase(TestCase):

    def test_invalid_schema(self):
        try:
            class TestItem1(JsonSchemaItem):
                jsonschema = invalid_schema
        except SchemaError:
            pass
        else:
            self.fail('SchemaError was not raised')

    def test_valid_schema(self):
        class TestItem2(JsonSchemaItem):
            jsonschema = valid_schema
