from datasette import hookimpl
from datasette.utils.asgi import Response


ROBOTS_TXT = """
Sitemap: https://cryptics.eigenfoo.xyz/sitemap.xml
""".strip()

SITEMAP_XML = """
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://cryptics.eigenfoo.xyz/data/charades</loc></url>
  <url><loc>https://cryptics.eigenfoo.xyz/data/clues</loc></url>
  <url><loc>https://cryptics.eigenfoo.xyz/data/indicators</loc></url>
  <url><loc>https://cryptics.eigenfoo.xyz/data/metadata</loc></url>
  <url><loc>https://cryptics.eigenfoo.xyz/data</loc></url>
  <url><loc>https://cryptics.eigenfoo.xyz/datasheet</loc></url>
  <url><loc>https://cryptics.eigenfoo.xyz</loc></url>
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
