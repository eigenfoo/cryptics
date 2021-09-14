# [`cryptics.eigenfoo.xyz`](https://cryptics.eigenfoo.xyz/)

> `cryptics.eigenfoo.xyz` is a dataset of cryptic crossword clues, collected from
> various blogs and publicly available digital archives.

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

For more information, please see [`cryptics.eigenfoo.xyz`](https://cryptics.eigenfoo.xyz/).

## License

This dataset is made available under the [Open Database
License](http://opendatacommons.org/licenses/odbl/1.0/). A human-readable
summary is [available
here](https://opendatacommons.org/licenses/odbl/summary/). Any rights in
individual contents of the database are licensed under the [Database Contents
License](http://opendatacommons.org/licenses/dbcl/1.0/).

HTML and CSS code was modified from
[`pandoc-markdown-css-theme`](https://github.com/jez/pandoc-markdown-css-theme),
which is licensed under the [Blue Oak Model
License](https://blueoakcouncil.org/license/1.0.0). The remainder of the code
is licensed under the [MIT License](https://mit-license.org/).

## Colophon

`cryptics.eigenfoo.xyz` is written in Python and run on a mix of [Digital Ocean
Droplets (Basic Plan)](https://www.digitalocean.com/products/droplets/)  and a
personal MacBook Pro.

The data is published using [Datasette](https://datasette.io/) and deployed on
[Heroku (Free Web Dyno)](https://dashboard.heroku.com/apps). Datasette has been
remarkably easy to work with and a pleasure to use.

The documentation is a static site adapted from
[`pandoc-markdown-css-theme`](https://github.com/jez/pandoc-markdown-css-theme).
