# -*- coding: utf-8 -*-
"""
Ignore the unused imports, this file's purpose is to make visible
anything which a user might need to import from newspaper.
View newspaper/__init__.py for its usage.
"""
__title__ = 'newspaper'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'

import os
import shutil
import feedparser


from . import settings
from .article import Article
from .configuration import Configuration
from .mthreading import NewsPool
from .settings import POPULAR_URLS, TRENDING_URL
from .source import Source
from .utils import extend_config, print_available_languages


def build(url='', dry=False, config=None, **kwargs):
    """Returns a constructed source object without
    downloading or parsing the articles
    """
    config = config or Configuration()
    config = extend_config(config, kwargs)
    url = url or ''
    s = Source(url, config=config)
    if not dry:
        s.build()
    return s


def build_article(url='', config=None, **kwargs):
    """Returns a constructed article object without downloading
    or parsing
    """
    config = config or Configuration()
    config = extend_config(config, kwargs)
    url = url or ''
    a = Article(url, config=config)
    return a


def languages():
    """Returns a list of the supported languages
    """
    print_available_languages()


def popular_urls():
    """Returns a list of pre-extracted popular source urls
    """
    with open(POPULAR_URLS) as f:
        urls = ['http://' + u.strip() for u in f.readlines()]
        return urls


def hot():
    """Returns a list of hit terms via google trends
    """
    try:
        listing = feedparser.parse(TRENDING_URL)['entries']
        trends = [item['title'] for item in listing]
        return trends
    except Exception as e:
        print('ERR hot terms failed!', str(e))
        return None


def fulltext(html, language='en'):
    """Takes article HTML string input and outputs the fulltext
    Input string is decoded via UnicodeDammit if needed
    """
    from .cleaners import DocumentCleaner
    from .configuration import Configuration
    from .extractors import ContentExtractor
    from .outputformatters import OutputFormatter

    config = Configuration()
    config.language = language

    extractor = ContentExtractor(config)
    document_cleaner = DocumentCleaner(config)
    output_formatter = OutputFormatter(config)

    doc = config.get_parser().fromstring(html)
    doc = document_cleaner.clean(doc)

    top_node = extractor.calculate_best_node(doc)
    top_node = extractor.post_cleanup(top_node)
    text, article_html = output_formatter.get_formatted(top_node)
    return text


def clear_cache():
    res_dir_fn = settings.ARTICLE_DIRECTORY
    resource_directory = os.path.join(settings.TOP_DIRECTORY, res_dir_fn)
    if os.path.exists(resource_directory):
        os.removedirs(resource_directory)
        os.mkdir(resource_directory)

    anchor_directory = settings.ANCHOR_DIRECTORY
    if os.path.exists(anchor_directory):
        shutil.rmtree(anchor_directory)
        os.mkdir(anchor_directory)

    memo_directory = settings.MEMO_DIR
    if os.path.exists(memo_directory):
        shutil.rmtree(memo_directory)
        os.mkdir(memo_directory)

    return resource_directory

