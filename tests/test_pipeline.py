from unittest import TestCase

from scrapy.statscol import StatsCollector
from scrapy.exceptions import DropItem
from scrapy_jsonschema.pipeline import JsonSchemaValidatePipeline
from scrapy_jsonschema.item import JsonSchemaItem
from . import (
    valid_schema, valid_docs, invalid_doc_types, invalid_doc_required,
    merge_schema_base, merge_schema_base_2,  merge_schema_new, merged_valid_docs, merged_invalid_docs
)


class DummyStatsCollector(StatsCollector):
    def __init__(self):
        self._stats = {}


class TestItem(JsonSchemaItem):
    jsonschema = valid_schema


class JsonSchemaValidatePipelineTestCase(TestCase):

    def test_with_valid_items(self):
        stats = self._get_stats_for_docs(valid_docs, True)
        self.assertEqual(stats.get_stats(), {})

    def test_with_invalid_items(self):
        invalid_docs = invalid_doc_required + invalid_doc_types
        for doc in invalid_docs:
            stats = self._get_stats_for_docs([doc], False)
            self.assertNotEqual(stats.get_stats(), {})

    def test_with_merged_schema(self):
        class Base(JsonSchemaItem):
            jsonschema = merge_schema_base
        class Base2(JsonSchemaItem):
            jsonschema = merge_schema_base_2
        class Merged(Base, Base2):
            jsonschema = merge_schema_new
            merge_schema = True
        stats = self._get_stats_for_docs(merged_valid_docs, True, Merged)
        self.assertEqual(stats.get_stats(), {})
        for doc in merged_invalid_docs:
            stats = self._get_stats_for_docs([doc], False, Merged)
            self.assertNotEqual(stats.get_stats(), {})

    def _get_stats_for_docs(self, docs, valid, item_cls=TestItem):
        stats = DummyStatsCollector()
        pipeline = JsonSchemaValidatePipeline(stats)

        for doc in docs:
            item = item_cls(**doc)
            if valid:
                pipeline.process_item(item, None)
            else:
                self.assertRaises(DropItem,
                                  pipeline.process_item, item, None)

        return stats
