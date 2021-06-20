#!/usr/bin/env python
# coding=utf-8
import glob
import importlib
import logging
import os
from types import MethodType

from falcon import API

logger = logging.getLogger(__name__)


def _load_api_modules(api_modules_path):
    apis = glob.glob("{}/**/*.py".format(api_modules_path), recursive=True)
    for api in apis:
        f_name = os.path.basename(api)
        if not f_name.startswith("__"):
            api_ = api.replace("/", ".")[0:-3]
            importlib.import_module(api_)


_REGISTERED_API_MODULES = {}


def _register_api_function(uri, func, method="GET"):
    module = func.__module__
    if module not in _REGISTERED_API_MODULES:
        _REGISTERED_API_MODULES[module] = {(uri, func, method)}
    else:
        _REGISTERED_API_MODULES[module].add((uri, func, method))


def route(uri, method="GET"):
    def decorator(func):
        _register_api_function(uri, func, method)

    return decorator


class APIProxy:
    def __init__(self, module):
        self._module = module

    def __repr__(self):
        return f"Routes for module: {self._module}, {self.__dict__}"


def _build_actions(obj, func, method):
    func_name = f"on_{method.lower()}_{func.__name__}"

    def wrapper(*args, **kwargs):
        logger.debug(f"{args[0]}, \n{args[1]}, \n{args[2]}")
        params = args[3:]
        if params:
            return func(*params, **kwargs)
        return func(**kwargs)

    setattr(obj, func_name, MethodType(wrapper, obj))


def register_routes(api: API):
    _load_api_modules()
    logger.debug(f"Routes: {_REGISTERED_API_MODULES}")

    for module, routes in _REGISTERED_API_MODULES.items():
        api_proxy = APIProxy(module)
        for uri, func, method in routes:
            _build_actions(api_proxy, func, method)
            api.add_route(uri, api_proxy, suffix=func.__name__)

