from abc import ABCMeta

import six
from jsonschema import Draft4Validator
from scrapy.item import DictItem, Field


def _merge_schema(base, new):
    if base is None:
        return new
    if new is None:
        return base
    if all(isinstance(x, dict) for x in (base, new)):
        return {
            key: _merge_schema(base.get(key), new.get(key))
            for key in six.viewkeys(base) | six.viewkeys(new)
        }
    if all(isinstance(x, (list, tuple)) for x in (base, new)):
        return list(base) + list(new)
    return base


class JsonSchemaMeta(ABCMeta):
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
            raise ValueError('{} must contain "jsonschema" attribute'
                             .format(cls.__name__))
        cls.validator = Draft4Validator(schema)
        cls.validator.check_schema(schema)
        for k in schema['properties']:
            fields[k] = Field()
        cls.fields = cls.fields.copy()
        cls.fields.update(fields)
        return cls


@six.add_metaclass(JsonSchemaMeta)
class JsonSchemaItem(DictItem):
    jsonschema = {
        "properties": {}
    }
    merge_schema = False  # Off for backward-compatibility
