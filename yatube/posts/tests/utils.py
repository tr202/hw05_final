import logging
from dataclasses import dataclass
from string import Formatter

from .config_tests import (APP_NAME, CONFIG_TEST_URLS,
                           OBJECT_RELATED_URL_PARAMS)
from ..models import Post


@dataclass
class TestUrl:
    app_name: str
    page_name: str
    url: str
    template: str = None
    redirect_url: str = None
    kwargs: str = None


def get_obj_test_urls(cls, tested_page_names=CONFIG_TEST_URLS.keys()):
    test_urls = {}
    for name in tested_page_names:
        item = CONFIG_TEST_URLS[name]
        test_url = TestUrl(APP_NAME, name, *item)
        args = [fname for _, fname, _, _ in Formatter().parse(
            str(test_url.url)) if fname]
        args.extend([fname for _, fname, _, _ in Formatter().parse(
            str(test_url.redirect_url)) if fname])
        if len(args) > 0:
            kwargs = {}
            for arg in args:
                try:
                    kwargs[arg] = get_nested_attr(
                        cls, (OBJECT_RELATED_URL_PARAMS[arg][0],
                              OBJECT_RELATED_URL_PARAMS[arg][1]))
                except Exception:
                    logging.exception(f'Error config param for: {arg}')
            test_url.kwargs = kwargs
            try:
                test_url.url = test_url.url.format(**kwargs)
                if not (test_url.redirect_url) is None:
                    test_url.redirect_url = (
                        test_url.redirect_url.format(**kwargs))
            except Exception:
                logging.exception(f'Error config URL for{tested_page_names}')
        test_urls[name] = test_url
    return test_urls


def get_nested_attr(obj, nested_param):
    next = obj
    for p in nested_param:
        next = getattr(next, p)
    return next


def create_posts(count, cls, list=[]):
    if count == 0:
        return list
    list.append(
        Post(
            author=cls.user,
            text='text' + str(count),
            group=cls.group,
            image=cls.image))
    return create_posts(count - 1, cls)
