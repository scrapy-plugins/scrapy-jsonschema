import pytest
from unittest import TestCase

from jsonschema.exceptions import SchemaError
from jsonschema import Draft4Validator, Draft7Validator

from scrapy_jsonschema.item import JsonSchemaItem, _merge_schema
from scrapy_jsonschema.draft import JSON_SCHEMA_DRAFT_7
from jsonschema.exceptions import ValidationError

from . import (
    valid_schema,
    invalid_schema,
    merge_schema_base,
    merge_schema_base_2,
    merge_schema_new,
)


class ValidSchemaTestCase(TestCase):

    schema1 = {
        "both": 1,
        "only_base": 2,
        "nested": {"list_to_merge": [1, 2], "both": "foo"},
    }
    schema2 = {
        "both": 3,
        "only_new": 4,
        "nested": {"list_to_merge": [3], "both": "bar", "only_new": "baz"},
    }

    def test_no_schema(self):
        with pytest.raises(ValueError):

            class TestNoSchema(JsonSchemaItem):
                jsonschema = None

    def test_invalid_schema(self):
        with pytest.raises(SchemaError):

            class TestItem1(JsonSchemaItem):
                jsonschema = invalid_schema

    def test_valid_schema(self):
        class TestItem2(JsonSchemaItem):
            jsonschema = valid_schema

    def test_merge_schema_func(self):
        expected = {
            "both": 1,
            "only_base": 2,
            "only_new": 4,
            "nested": {
                "list_to_merge": [1, 2, 3],
                "both": "foo",
                "only_new": "baz",
            },
        }
        self.assertEqual(_merge_schema(self.schema1, self.schema2), expected)

    def test_merge_schema_none(self):
        self.assertEqual(_merge_schema(self.schema1, None), self.schema1)
        self.assertEqual(_merge_schema(None, self.schema1), self.schema1)

    def test_merge_schema(self):
        class Base(JsonSchemaItem):
            jsonschema = merge_schema_base

        class Base2(JsonSchemaItem):
            jsonschema = merge_schema_base_2

        class Merged(Base, Base2):
            jsonschema = merge_schema_new
            merge_schema = True

    def test_get_validator(self):
        schema = {
            "$schema": JSON_SCHEMA_DRAFT_7,
            "title": "Item with Schema Draft",
        }

        draft7_validator = JsonSchemaItem._get_validator(schema)
        self.assertTrue(isinstance(draft7_validator, Draft7Validator))

        no_draft_chema = {"title": "Item without schema Draft"}
        default_validator = JsonSchemaItem._get_validator(no_draft_chema)
        self.assertTrue(isinstance(default_validator, Draft4Validator))

    def test_format_validation(self):
        schema = {
            "$schema": JSON_SCHEMA_DRAFT_7,
            "title": "Item with Schema Draft",
            "properties": {
                "url": {
                    "type": "string",
                    "format": "uri"
                }
            }
        }

        with pytest.raises(ValidationError):
            draft7_validator = JsonSchemaItem._get_validator(schema)
            draft7_validator.validate({'url': 'this is not an uri'})

        draft7_validator.validate({'url': 'http://localhost'})
