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
