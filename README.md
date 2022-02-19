# A Dataset of Cryptic Crossword Clues

> `cryptics.georgeho.org` is a dataset of cryptic crossword clues,
> collected from various blogs and digital archives.

This repository contains:

- The [`cryptics`](https://github.com/eigenfoo/cryptics/tree/main/cryptics)
  Python library to scrape various cryptic crossword blogs and parse the
  scraped blog posts into a structured dataset of cryptic crossword clues.
- The [`docs`](https://github.com/eigenfoo/cryptics/tree/main/docs),
  [`static`](https://github.com/eigenfoo/cryptics/tree/main/static) files and
  [`templates`](https://github.com/eigenfoo/cryptics/tree/main/templates)
  needed to generate the static site for documentation.
- Miscellanous
  [`scripts`](https://github.com/eigenfoo/cryptics/tree/main/scripts) and
  [`queries`](https://github.com/eigenfoo/cryptics/tree/main/queries) to
  publish and deploy the Datasette instance.

For more information, please see [`cryptics.georgeho.org`](https://cryptics.georgeho.org/).

## License

This dataset is made available under the [Open Database License](http://opendatacommons.org/licenses/odbl/1.0/).
A human-readable summary is [available here](https://opendatacommons.org/licenses/odbl/summary/).
Any rights in individual contents of the database are licensed under the [Database Contents License](http://opendatacommons.org/licenses/dbcl/1.0/).

HTML and CSS code was modified from [`pandoc-markdown-css-theme`](https://github.com/jez/pandoc-markdown-css-theme),
which is licensed under the [Blue Oak Model License](https://blueoakcouncil.org/license/1.0.0).
The remainder of the code is licensed under the [MIT License](https://mit-license.org/).

## Colophon

`cryptics.georgeho.org` is written in a mix of Python, Bash and SQL
and is run on my personal laptop.

The data is published using [Datasette](https://datasette.io/)
and deployed on a [Heroku Free Web Dyno](https://dashboard.heroku.com/apps).
Datasette has been remarkably easy to work with and a pleasure to use.

The documentation is a static site adapted from
[`pandoc-markdown-css-theme`](https://github.com/jez/pandoc-markdown-css-theme).
