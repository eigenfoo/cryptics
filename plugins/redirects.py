""" Adapted from https://til.simonwillison.net/datasette/redirects-for-datasette """

from datasette import hookimpl
from datasette.utils.asgi import Response


@hookimpl
def register_routes():
    return [
        # TODO: /clues/clues -> /data/clues (?)
        (
            # E.g. /clues/clues/123 -> /data/clues/123
            r"^/clues/clues/(?P<rowid>[0-9]+)$",
            lambda request: Response.redirect(
                "/data/clues/{rowid}".format(**request.url_vars), status=301
            ),
        ),
        (
            # E.g. /clues/clues?x=foo&y=bar -> /data/clues?x=foo&y=bar 
            r"^/clues/clues$",
            lambda request: Response.redirect(
                "/data/clues"
                + (("?" + request.query_string) if request.query_string else ""),
                status=301,
            ),
        ),
        (
            # E.g. /crypticclueaday -> Google Sheet
            r"^/crypticclueaday$",
            lambda request: Response.redirect(
                "https://docs.google.com/spreadsheets/d/1wltYlh7YLG8KxR5fOkLB8xCJzOmBP9N3vQN9bBLwuHk",
                status=301
            ),
        ),
    ]
