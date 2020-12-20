# sidenote:
#
# initially tried to use FastAPI, but since all of this is
# dynamic, it just feels like I'm fighting with its
# JSON encoder and its class-model based approach
#
# Custom Encoders through its json_enodable function
# run before any custom ones I define, so its not
# possible to serialize custom types
#
# at that point, I'm getting none of the benefits
# of the types that pydantic gives me, so its not
# particularly worth to use it

import os
from types import FunctionType
from typing import List, Dict, Any, Callable, Iterator
from functools import wraps

import more_itertools
from flask import Blueprint, request

from .common import FuncTuple

# generates a blueprint which
# represents the entire HPI API
# example item in the fdict:
#   'my.github.all': ['events', <function events ...>, ...]
def generate_blueprint(fdict: Dict[str, List[FuncTuple]]) -> Blueprint:
    blue: Blueprint = Blueprint("hpi_api", __name__)
    routes: List[str] = []
    for module_name, funcs in fdict.items():
        for (fname, libfunc) in funcs:
            rule: str = os.path.join("/", module_name.replace(".", "/"), fname)
            assert "." not in rule
            blue.add_url_rule(
                rule, rule, generate_route_handler(libfunc), methods=["GET"]
            )
            routes.append(rule)
    # add /route, to display all routes
    def all_routes() -> Any:
        return {"routes": sorted(routes)}

    blue.add_url_rule("/routes", "route", all_routes, methods=["GET"])
    return blue


# TODO: let user pass basic kwargs as arguments? Can inspect type/signature.bind and coerce
# user can pass GET parameters (limit, page):
#   limit: int (limit number of items, default 50)
#   page: int (default 1)
#   TODO: add sorting:
#       sort: "attribute" (some getattr/dict key on the object), e.g. "dt", or "date"
#       order_by: [asc, desc] (to sort by ascending or descending order (default: asc))
def generate_route_handler(libfunc: FunctionType) -> Callable[[], Any]:
    # need to return either:
    #   - JSON compatible dict
    #   - serialized Response with JSON MimeType
    @wraps(libfunc)
    def route() -> Any:
        # wrap TypeError, common for non-event-like functions to fail
        # when argument count doesnt match
        try:
            resp: Any = libfunc()
        except TypeError as e:
            return f"TypeError: {str(e)}\n", 400
        # if primitive, stats or dict, return directly
        if (
            any([isinstance(resp, _type) for _type in [int, float, str, bool]])
            or isinstance(resp, dict)
            or libfunc.__qualname__ == "stats"
        ):
            return resp
        riter: Iterator[Any] = iter(resp)
        limit: int = 50
        page: int = 1
        if "limit" in request.args:
            limit = int(request.args["limit"])
        if "page" in request.args:
            page = int(request.args["page"])
            if page < 1:
                return "Page must be greater than 1\n", 400
        # exhaust paginations
        for _ in range(page - 1):
            more_itertools.take(limit, riter)
        return_val: List[Any] = more_itertools.take(limit, riter)
        # flask seems to handle serializing any return_val I've tried so far
        # routes that commonly fail:
        #   /input functions (PosixPath is not JSON serializable)
        #   any helper/util function which requires an argument
        #
        # dont have any items which return pandas.DataFrames, but
        # that should be a simple check to convert it to an iterable-thing,
        # if iter() doesnt already do it automatically
        return {"page": page, "limit": limit, "items": return_val}

    return route
