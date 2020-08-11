from abc import ABCMeta

import re
import six
from jsonschema import (
    Draft3Validator,
    Draft4Validator,
    Draft6Validator,
    Draft7Validator,
    FormatChecker
)
from scrapy_jsonschema.draft import (
    JSON_SCHEMA_DRAFT_3,
    JSON_SCHEMA_DRAFT_4,
    JSON_SCHEMA_DRAFT_6,
    JSON_SCHEMA_DRAFT_7,
)

from jsonschema import (
    draft3_format_checker,
    draft4_format_checker,
    draft6_format_checker,
    draft7_format_checker,
)

from scrapy.item import DictItem, Field, _BaseItemMeta


def _merge_schema(base, new):
    if base is None or new is None:
        return base or new

    if all(isinstance(x, dict) for x in (base, new)):
        return {
            key: _merge_schema(base.get(key), new.get(key))
            for key in six.viewkeys(base) | six.viewkeys(new)
        }
    if all(isinstance(x, (list, tuple)) for x in (base, new)):
        return list(base) + list(new)
    return base


class JsonSchemaMeta(_BaseItemMeta):

    # For backward compatibility
    format_checker = FormatChecker()

    draft_to_validator = {
        JSON_SCHEMA_DRAFT_3: Draft3Validator,
        JSON_SCHEMA_DRAFT_4: Draft4Validator,
        JSON_SCHEMA_DRAFT_6: Draft6Validator,
        JSON_SCHEMA_DRAFT_7: Draft7Validator,
    }

    draft_to_format_checker = {
        JSON_SCHEMA_DRAFT_3: draft3_format_checker,
        JSON_SCHEMA_DRAFT_4: draft4_format_checker,
        JSON_SCHEMA_DRAFT_6: draft6_format_checker,
        JSON_SCHEMA_DRAFT_7: draft7_format_checker,
    }

    combination_schemas_keywords = ['allOf', 'anyOf', 'oneOf']

    def __new__(mcs, class_name, bases, attrs):
        cls = super(JsonSchemaMeta, mcs).__new__(mcs, class_name, bases, attrs)
        fields = {}
        schema = attrs.get('jsonschema', {})
        if cls.merge_schema:
            # priority: left to right
            for base in bases:
                base_schema = getattr(base, 'jsonschema', None)
                if base_schema:
                    schema = _merge_schema(schema, base_schema)
            setattr(cls, 'jsonschema', schema)
        if not schema:
            raise ValueError(
                '{} must contain "jsonschema" attribute'.format(cls.__name__)
            )
        cls.validator = cls._get_validator(schema)
        cls.validator.check_schema(schema)
        for k in cls.get_top_level_property_names(schema):
            fields[k] = Field()
        cls.fields = cls.fields.copy()
        cls.fields.update(fields)

        pattern_properties = schema.get('patternProperties', {})
        cls.pattern_properties = [
            re.compile(p)
            for p in pattern_properties.keys()
            if p is not 'additionalProperties'
        ]
        return cls

    @classmethod
    def get_top_level_property_names(cls, schema):
        for field in schema.get('properties', {}):
            yield field

        for keyword in cls.combination_schemas_keywords:
            for subschema in schema.get(keyword, []):
                for field in subschema.get('properties', {}):
                    yield field

    @classmethod
    def _get_validator(cls, schema):
        draft_version = schema.get('$schema')
        # Default to Draft4Validator for backward-compatibility
        validator_class = cls.draft_to_validator.get(
            draft_version, Draft4Validator
        )
        format_checker = cls.draft_to_format_checker.get(
            schema.get('$schema'), draft4_format_checker
        )
        return validator_class(schema, format_checker=format_checker)


@six.add_metaclass(JsonSchemaMeta)
class JsonSchemaItem(DictItem):
    jsonschema = {"properties": {}}
    merge_schema = False  # Off for backward-compatibility

    def __setitem__(self, key, value):
        if key in self.fields:
            self._values[key] = value
        elif any(x.match(key) for x in self.pattern_properties):
            self.fields[key] = Field()
            self._values[key] = value

        else:
            raise KeyError(
                "%s does not support field: %s"
                % (self.__class__.__name__, key)
            )
