# my_sls_scraper/crawl.py
import sys
import types
import os
import logging
from urllib.parse import urlparse

from scrapy.spiderloader import SpiderLoader
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Need to "mock" sqlite for the process to not crash in AWS Lambda / Amazon Linux
sys.modules["sqlite"] = types.ModuleType("sqlite")
sys.modules["sqlite3.dbapi2"] = types.ModuleType("sqlite.dbapi2")


def is_in_aws():
    return os.getenv('AWS_EXECUTION_ENV') is not None


def has_task_token():
    return os.getenv('TASK_TOKEN_ENV_VARIABLE') is not None


def crawl(settings={}, spider_name="", key="", spider_kwargs={}):
    project_settings = get_project_settings()
    spider_loader = SpiderLoader(project_settings)
    spider_cls = spider_loader.load(spider_name)

    feed_uri = ""
    feed_format = "csv"
    spider_key = ""
    try:
        spider_key = urlparse(spider_kwargs.get("start_urls")[0]).hostname if spider_kwargs.get(
            "start_urls") else urlparse(spider_cls.start_urls[0]).hostname
    except Exception as e:
        logging.exception("Spider or kwargs need start_urls.")
        logging.exception(e)

    if is_in_aws():
        # Lambda can only write to the /tmp folder.
        settings['HTTPCACHE_DIR'] = "/tmp"
        feed_uri = f"s3://{os.getenv('FEED_BUCKET_NAME')}/{spider_name}_{key}.csv"
    else:
        feed_uri = "file://{}/%(name)s-{}-%(time)s.json".format(
            os.path.join(os.getcwd(), "feed"),
            spider_key,
        )

    settings['FEED_URI'] = feed_uri
    settings['FEED_FORMAT'] = feed_format

    process = CrawlerProcess({**project_settings, **settings})

    process.crawl(spider_cls, **spider_kwargs)
    process.start()

    if is_in_aws() and has_task_token():
        import boto3
        import json
        client = boto3.client('stepfunctions')
        client.send_task_success(
            taskToken=os.getenv('TASK_TOKEN_ENV_VARIABLE'),
            output=json.dumps({"feed_uri": feed_uri})
        )
