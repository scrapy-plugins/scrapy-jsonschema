from abc import ABCMeta

import six
from jsonschema import (
    Draft3Validator,
    Draft4Validator,
    Draft6Validator,
    Draft7Validator,
)

from scrapy_jsonschema.draft import (
    JSON_SCHEMA_DRAFT_3,
    JSON_SCHEMA_DRAFT_4,
    JSON_SCHEMA_DRAFT_6,
    JSON_SCHEMA_DRAFT_7,
)

from scrapy.item import DictItem, Field


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


class JsonSchemaMeta(ABCMeta):

    draft_to_validator = {
        JSON_SCHEMA_DRAFT_3: Draft3Validator,
        JSON_SCHEMA_DRAFT_4: Draft4Validator,
        JSON_SCHEMA_DRAFT_6: Draft6Validator,
        JSON_SCHEMA_DRAFT_7: Draft7Validator,
    }

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
        for k in schema['properties']:
            fields[k] = Field()
        cls.fields = cls.fields.copy()
        cls.fields.update(fields)
        return cls

    @classmethod
    def _get_validator(cls, schema):
        draft_version = schema.get('$schema')
        # Default to Draft4Validator for backward-compatibility
        validator_class = cls.draft_to_validator.get(
            draft_version, Draft4Validator
        )
        return validator_class(schema)


@six.add_metaclass(JsonSchemaMeta)
class JsonSchemaItem(DictItem):
    jsonschema = {"properties": {}}
    merge_schema = False  # Off for backward-compatibility
