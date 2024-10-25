An automatic JSON API for [HPI](https://github.com/karlicoss/HPI)

This inspects functions in each `HPI` module file, generating routes for each of them.

This provides access to the data fine, but I wouldn't recommend putting this up on the public internet as this allows anything that can make a GET request to call arbitrary functions in HPI; At least put it behind some authenticated proxy or host it on a private port

This uses [`my.core.serialize`](https://github.com/karlicoss/HPI/blob/master/my/core/serialize.py) to convert the responses to JSON, which uses [`orjson`](https://github.com/ijl/orjson) under the hood, to serialize datetimes, namedtuples and dataclasses much faster than the stdlib.

If you have any suggestions/trouble with getting this to work, feel free to open an Issue/PR!

---

### Installation

Requires `python3.7+`

To install with pip, run:

    pip install git+https://github.com/purarue/HPI_API

---

### Usage

For each function in an HPI module, this generates a HTTP route. For example, if you had the module `my.reddit`, which had a function `comments`, which returned an iterator/list of your `reddit` comments, requesting `/my/reddit/comments` would call that function.

- If the function fails to be called, it returns an HTTP code > 400.
- If the function succeeds
  - and this returns a primitive, a `dict` or this is the stats function, it returns the value directly
  - otherwise, this assumes its returning some iterable event-like response, supporting the following GET params:
    - limit: int (defaults to 50) - how many items to return per page
    - page: int (defaults to 1) - which page to return
    - sort: str "attribute_name" - some getattr/dictionary key on the object returned from the HPI function), e.g. "dt", or "date", to sort by date. If not provided, returns the same order as the underlying HPI function
    - order_by: one of [asc, desc] (default: asc) - to sort by ascending or descending order

Theres no limit to the `limit` param, if you wanted to grab all the data, you can always do something like `?limit=99999999999999999&page=1`

Though I'm not a huge fan of pagination, the `limit` included anyways. Otherwise, if not behind `cachew`, some responses may take a _long_ time to compute

After installing, you can run this server with:

```bash
$ python3 -m my_api server  # or `hpi_api server`
```

To list the routes, you can run one of the following:

```bash
$ curl 'localhost:5050/routes'
$ hpi_api list-modules --functions
$ hpi_api server --print-routes
```

Here are some examples:

```bash
$ curl 'localhost:5050/my/zsh/history?limit=3'
{"items":[{"command":"z","dt":"Mon, 18 May 2020 08:23:22 GMT","duration":0},{"command":"en env_config.zsh","dt":"Mon, 18 May 2020 08:23:22 GMT","duration":0},{"command":"ls","dt":"Mon, 18 May 2020 08:23:22 GMT","duration":0}],"limit":3,"page":1}
$ curl 'localhost:5050/my/github/all/events?limit=1' | jq -r '.items | .[0]'
{
  "body": "Note: This is used for [gitopen](https://github.com/purarue/dotfiles/commit/4c57fd97cbb2605e63d0cf5d2af37039fe6e6d35)",
  "dt": "Thu, 14 Feb 2019 21:05:40 GMT",
  "eid": "commoit_comment_https://github.com/purarue/mac-dotfiles/commit/d4ac3c30dd3df1b626f92eb61f651a27852ff86f#commitcomment-32324943",
  "is_bot": false,
  "link": "https://github.com/purarue/mac-dotfiles/commit/d4ac3c30dd3df1b626f92eb61f651a27852ff86f#commitcomment-32324943",
  "summary": "commented on https://github.com/purarue/mac-dotfiles/commit/d4ac3c30dd3df1b626f92eb61f651a27852ff86f#commitcomment-32324943"
}
$ curl localhost:5050/my/zsh/stats
{"value":{"history":{"count":266722}}}
$ curl 'localhost:5050/my/zsh/history?sort=command&order_by=desc&limit=2'
{"items":[{"command":"~/code/plaintext-playlist/plainplay | basename","dt":"Thu, 28 May 2020 06:52:58 GMT","duration":3},{"command":"~/code/plaintext-playlist/plainplay | basename","dt":"Thu, 28 May 2020 06:52:39 GMT","duration":2}],"limit":2,"page":1}
```

---

### Configuration

To change the port this runs on, you can use the `--port` flag to change the port this runs on (default is `5050`) when running with `hpi_api server`.

By default, this allows CORS requests, you can pass the `--no-cors` flag to disable that.

If you want to customize the application further, you can import the generated Flask application to add routes, or run it with another WSGI compatible server, like [`waitress`](https://pypi.org/project/waitress/):

```python
from my_api.server import generate_server

app = generate_server()

## ... configure whatever you want, add routes to Flask app

if __name__ == "__main__":
    from waitress import serve
    serve(app, port=8123, host="0.0.0.0")
```
