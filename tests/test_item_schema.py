from unittest import TestCase

from jsonschema.exceptions import SchemaError

from scrapy_jsonschema.item import JsonSchemaItem, _merge_schema
from . import (
    valid_schema,
    invalid_schema,
    merge_schema_base,
    merge_schema_base_2,
    merge_schema_new,
)


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

    def test_merge_schema_func(self):
        schema1 = {
            'both': 1,
            'only_base': 2,
            'nested': {'list_to_merge': [1, 2], 'both': 'foo'},
        }
        schema2 = {
            'both': 3,
            'only_new': 4,
            'nested': {'list_to_merge': [3], 'both': 'bar', 'only_new': 'baz'},
        }
        expected = {
            'both': 1,
            'only_base': 2,
            'only_new': 4,
            'nested': {
                'list_to_merge': [1, 2, 3],
                'both': 'foo',
                'only_new': 'baz',
            },
        }
        self.assertEqual(_merge_schema(schema1, schema2), expected)

    def test_merge_schema(self):
        class Base(JsonSchemaItem):
            jsonschema = merge_schema_base

        class Base2(JsonSchemaItem):
            jsonschema = merge_schema_base_2

        class Merged(Base, Base2):
            jsonschema = merge_schema_new
            merge_schema = True
