# v2022.02.06

## Data

- Added clues scraped from blog posts published from previous release date.
- Migrated domain from `cryptics.eigenfoo.xyz` to `cryptics.georgeho.org`. All
  URLs should automatically redirect.

# v2022.01.16

## Data

- Removed daily "update-deploy" job (from `v2021.11.07`). The dataset will once
  again be updated only manually by me.

## Documentation

- Updated contact email.

# v2021.11.08

## Code

- Added `robots.txt` at https://cryptics.eigenfoo.xyz/robots.txt
- Added `sitemap.xml` at https://cryptics.eigenfoo.xyz/sitemap.xml

# v2021.11.07

## Data

- Added a daily "update-deploy" job to scrape new blog posts, parse their clues
  and publish the latest dataset.

# v2021.10.24

## Data

- Added one-off CSV dump of `cru_cryptics` three PDF puzzles, courtesy of
  [Michael F. Gill](https://bbtp.net/).
- Added clues scraped from blog posts published from previous release date.

## Code

- Fixed `raw_definitions` in several parsing functions; re-ran on unparsed blog
  posts.

# v2021.10.16

## Data

- Changed source of Cru Cryptics from [The New York Times' archive
  page](https://archive.nytimes.com/www.nytimes.com/premium/xword/cryptic-archive.html)
  to [William I. Johnston's archive](https://theworld.com/~wij/puzzles/cru/).
  Thanks to Michael F. Gill for pointing this out!
- Remove erroneous `puzzle_date`s from clues parsed from `.puz` files.
- Added clues scraped from blog posts published from previous release date.

## Code

- Fixed some minor bugs with `review.py`

# v2021.10.04

## Data

- Added `indicators`, `indicators_by_clue`, `charades` and `charades_by_clue`
  tables. All indicators and charades are identified via regexes.

## Code

- Renamed database from `clues` to `data`. Added appropriate URL redirects.

# v2021.09.29

## Data

- Manually corrected several hundred rows.

## Code

- Added Clicky analytics to Datasette webpages.
- Improved function docstrings.
- Refactored `main.py` to both populate database with new blog posts and also
  parse new blog posts.

# v2021.09.18

## Data

- Added Michael F. Gill's digital archive of _The New York Times_ cryptic
  crosswords.
- Added National Post Cryptic Crossword Archive for Cox and Rathvon (a.k.a.
  Hex) cryptic crosswords.
- Allowed caching of raw `.puz` files.
- Added `source` column, dropped `puzzle_url` columns.
- Added facet over `source` column.

# v2021.09.15

## Data

- Added [The Hindu Crossword
  Corner](https://thehinducrosswordcorner.blogspot.com/) as a scraped blog,
  which adds approximately 67,000 clues.
- Deleted duplicate rows in the `clues` table.
- Added clues scraped from blog posts published from previous release date.

# v2021.09.12

## Data

- Licensed database under the [Open Database License
  (ODbL)](https://opendatacommons.org/licenses/odbl/1-0/) and contents under
  the [Database Contents License
  (DCL)](https://opendatacommons.org/licenses/dbcl/1-0/).
- Added `metadata` table with `license` and `last_built` datetime.
- Added `source_url` column to the `clues` table.

## Code and Documentation

- Added Clicky analytics to documentation webpages.
- Acknowledged [Blue Oak Model
  License](https://blueoakcouncil.org/license/1.0.0) from
  [`pandoc-markdown-css-theme`](https://github.com/jez/pandoc-markdown-css-theme),
  and license remaining code under the [MIT License](https://mit-license.org/).

# v2021.09.10

Initial release on [https://cryptics.eigenfoo.xyz/](https://cryptics.eigenfoo.xyz/).
