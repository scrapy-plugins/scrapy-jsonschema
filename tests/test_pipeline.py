from unittest import TestCase

from scrapy.statscollectors import StatsCollector
from scrapy.exceptions import DropItem
from scrapy_jsonschema.pipeline import JsonSchemaValidatePipeline
from scrapy_jsonschema.item import JsonSchemaItem
from . import valid_schema, valid_docs, invalid_doc_types, invalid_doc_required


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

    def _get_stats_for_docs(self, docs, valid):
        stats = DummyStatsCollector()
        pipeline = JsonSchemaValidatePipeline(stats)

        for doc in docs:
            item = TestItem(**doc)
            if valid:
                pipeline.process_item(item, None)
            else:
                self.assertRaises(DropItem,
                                  pipeline.process_item, item, None)

        return stats
