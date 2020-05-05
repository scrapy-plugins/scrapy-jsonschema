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

class SchemaWithCombiningKeywords(TestCase):

    schema_allOf = {
      "$schema": JSON_SCHEMA_DRAFT_7,
        "allOf": [
            {
                "properties": {"foo": {"type": "string"}},
                "required": ["foo"],
            },
            {
                "properties": {"bar": {"type": "number"}},
                "required": ["bar"]
            }
        ]
    }

    schema_anyOf = {
      "$schema": JSON_SCHEMA_DRAFT_7,
        "anyOf": [
            {
                "properties": {"foo": {"type": "string"}},
                "required": ["foo"],
            },
            {
                "properties": {"bar": {"type": "number"}},
                "required": ["bar"]
            }
        ]
    }

    schema_oneOf = {
      "$schema": JSON_SCHEMA_DRAFT_7,
        "oneOf": [
            {
                "properties": {"foo": {"type": "string"}},
                "required": ["foo"],
            },
            {
                "properties": {"bar": {"type": "number"}},
                "required": ["bar"]
            }
        ]
    }

    def test_all_of_schema(self):

        class allOfItem(JsonSchemaItem):
            jsonschema = self.schema_allOf

        item = allOfItem()
        item['foo'] = 'foo'
        item['bar'] = 2
        self.assertFalse(list(item.validator.iter_errors(dict(item))))

        with pytest.raises(AssertionError):
            item = allOfItem()
            item['foo'] = 'foo'
            self.assertFalse(list(item.validator.iter_errors(dict(item))))


    def test_any_of_schema(self):

        class anyOfItem(JsonSchemaItem):
            jsonschema = self.schema_anyOf

        item = anyOfItem()
        item['foo'] = 'foo'
        item['bar'] = 2
        self.assertFalse(list(item.validator.iter_errors(dict(item))))

        item = anyOfItem()
        item['foo'] = 'foo'
        self.assertFalse(list(item.validator.iter_errors(dict(item))))

        item = anyOfItem()
        item['bar'] = 2
        self.assertFalse(list(item.validator.iter_errors(dict(item))))

    def test_one_of_schema(self):

        class oneOfItem(JsonSchemaItem):
            jsonschema = self.schema_oneOf

        item = oneOfItem()
        item['foo'] = 'foo'
        self.assertFalse(list(item.validator.iter_errors(dict(item))))

        item = oneOfItem()
        item['bar'] = 2
        self.assertFalse(list(item.validator.iter_errors(dict(item))))

        with pytest.raises(AssertionError):
            item = oneOfItem()
            item['foo'] = 'foo'
            item['bar'] = 2
            self.assertFalse(list(item.validator.iter_errors(dict(item))))

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

    def test_pattern_properties(self):
        schema = {
            "$schema": JSON_SCHEMA_DRAFT_7,
            "title": "Item with Schema Draft",
            "properties": {
                "title": {
                    "type": "string",
                },
            },
            "additionalProperties": False,
            "patternProperties": {
                r"image_\d+": {"type": "string"},
                "additionalProperties": False,
            },
        }

        draft7_validator = JsonSchemaItem._get_validator(schema)
        draft7_validator.validate({'image_1': 'http://foo.com/bar/1'})
        with pytest.raises(ValidationError):
            draft7_validator.validate({'image_a': 'http://foo.com/bar/a'})

        class PatternPropertiesItem(JsonSchemaItem):
            jsonschema = schema

        item = PatternPropertiesItem()
        item['image_1'] = 'http://foo.com/bar/1'

        with pytest.raises(KeyError):
            item['image_a'] = 'http://foo.com/bar/a'
