from datasette import hookimpl
from datasette.utils.asgi import Response


ROBOTS_TXT = """
Sitemap: https://cryptics.georgeho.org/sitemap.xml
""".strip()

SITEMAP_XML = """
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://cryptics.georgeho.org/data/charades</loc></url>
  <url><loc>https://cryptics.georgeho.org/data/clues</loc></url>
  <url><loc>https://cryptics.georgeho.org/data/indicators</loc></url>
  <url><loc>https://cryptics.georgeho.org/data/metadata</loc></url>
  <url><loc>https://cryptics.georgeho.org/data</loc></url>
  <url><loc>https://cryptics.georgeho.org/datasheet</loc></url>
  <url><loc>https://cryptics.georgeho.org</loc></url>
</urlset>
""".strip()


@hookimpl
def register_routes():
    return [
        ("^/robots.txt$", robots_txt),
        ("^/sitemap.xml$", sitemap_xml),
    ]


def robots_txt():
    return Response.text(ROBOTS_TXT)


def sitemap_xml():
    return Response(SITEMAP_XML, 200, content_type="application/xml")
