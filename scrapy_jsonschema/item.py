from abc import ABCMeta

import six
from jsonschema import Draft4Validator
from scrapy.item import DictItem, Field


class JsonSchemaMeta(ABCMeta):
    def __new__(mcs, class_name, bases, attrs):
        cls = super(JsonSchemaMeta, mcs).__new__(mcs, class_name, bases, attrs)
        fields = {}
        schema = attrs.get('jsonschema')
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
