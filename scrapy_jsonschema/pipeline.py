import re

from scrapy.exceptions import DropItem

from scrapy_jsonschema import JsonSchemaItem


class JsonSchemaValidatePipeline(object):

    STAT_FMT = 'jsonschema/errors/{field}'
    REQUIRED_RE = re.compile("'(.+?)' is a required property")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def __init__(self, stats):
        self.stats = stats

    def process_item(self, item, spider):
        if not isinstance(item, JsonSchemaItem):
            return item

        errors = list(item.validator.iter_errors(dict(item)))
        paths_messages = []
        for error in errors:
            absolute_path = list(error.absolute_path)
            # error path is not available when required field is not filled
            # so we parse error message. Nasty.
            required_match = self.REQUIRED_RE.search(error.message)
            if required_match:
                absolute_path.append(required_match.group(1))
            path = '.'.join(map(str, absolute_path))
            self.stats.inc_value(self.STAT_FMT.format(field=path))
            paths_messages.append((path, error.message))
        if errors:
            error_msg = ''
            for path, message in paths_messages:
                error_msg += u'{}: {}\n'.format(path, message)
            raise DropItem(u'schema validation failed: \n {}'.format(error_msg))

        return item
