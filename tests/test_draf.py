from unittest import TestCase

from scrapy_jsonschema.draft import (
    JSON_SCHEMA_DRAFT_3,
    JSON_SCHEMA_DRAFT_4,
    JSON_SCHEMA_DRAFT_6,
    JSON_SCHEMA_DRAFT_7,
)


class DraftTest(TestCase):
    "Test that draft constants values hasn't been change by mistake"

    def test_draft_3(self):
        assert JSON_SCHEMA_DRAFT_3 == "http://json-schema.org/draft-03/schema#"

    def test_draft_4(self):
        assert JSON_SCHEMA_DRAFT_4 == "http://json-schema.org/draft-04/schema#"

    def test_draft_6(self):
        assert JSON_SCHEMA_DRAFT_6 == "http://json-schema.org/draft-06/schema#"

    def test_draft_7(self):
        assert JSON_SCHEMA_DRAFT_7 == "http://json-schema.org/draft-07/schema#"
