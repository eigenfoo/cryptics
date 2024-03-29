---
title: A Dataset of Cryptic Crossword Clues
author-meta: George Ho
description-meta: A dataset of cryptic crossword clues, collected from various blogs and digital archives.
---

`cryptics.georgeho.org` is a dataset of cryptic crossword[^1] clues, indicators and charades, collected from various blogs and digital archives.

[^1]: If you're new to cryptic crosswords, rejoice! A whole new world awaits you! _The New Yorker_ has [an excellent introduction to cryptic crosswords](https://www.newyorker.com/puzzles-and-games-dept/cryptic-crossword/reintroducing-the-new-yorkers-cryptic-crossword), and Matt Gritzmacher has [a daily newsletter with links to crosswords](https://crosswordlinks.substack.com/).

This dataset is a significant work of crossword archivism and scholarship,
as acquiring historical crosswords and structuring their contents require
focused effort and tedious cleaning that few are willing to do for such trivial data -
for example, according to [this 2004 selection guide](/static/documents/Selection_AppendixE_v2.pdf)[^2],
the Library of Congress explicitly does not collect crossword puzzles.

[^2]: Heard through [Saul Pwanson](https://www.saul.pw/) and sourced from the [Internet Archive](https://web.archive.org/web/20170222163604/https://www.loc.gov/library/reports/co_bpr/JIG-S/Selection_AppendixE_v2.pdf).

This project indexes various blogs and digital archives for cryptic crosswords.
Several fields - such as
clues, answers, clue numbers, annotations or commentary, puzzle title and publication date -
are parsed and extracted into a tabular dataset.
The result is **over half a million clues from cryptic crosswords over the past twelve years**.

Two other datasets are subsequently derived from the clues - wordplay indicators and charades (a.k.a. substitutions).
All told, the derived datasets contain **over twelve thousand wordplay indicators** and **over sixty thousand charades**.

Currently the sources for clues are:

- 🇬🇧 [Big Dave's Crossword Blog](http://bigdave44.com/) (_The Daily Telegraph_, _The Sunday Telegraph_)
- 🇺🇸 [_The Browser_](https://thebrowser.com/crossword/)[^3]
- 🇺🇸 [Cru Cryptic Archive](https://theworld.com/~wij/puzzles/cru/) (_The New York Times_ "Cru" Forums)
- 🇬🇧 [Fifteensquared](https://www.fifteensquared.net/) (_Financial Times_, _The Guardian_, _The Independent_)
- 🇮🇳 [The Hindu Crossword Corner](https://thehinducrosswordcorner.blogspot.com/) (_The Hindu_)
- 🇺🇸 [_Leo Edit_](https://www.leoedit.com/?s=Cryptic)[^4]
- 🇨🇦 [National Post Cryptic Crossword Forum](https://natpostcryptic.blogspot.com/) (_National Post_)
- 🇺🇸 [_The New York Times_](https://www.nytimes.com/crosswords) `.puz` archive[^5]
- 🇺🇸 [_The New Yorker_](https://www.newyorker.com/crossword-puzzles-and-games)
- 🇬🇧 [Times for the Times](https://times-xwd-times.livejournal.com/) (_The Times_ of London)

[^3]: _The Browser_'s clues are sourced with the gracious permission of [Dan Feyer](https://twitter.com/danfeyer) and _The Browser_'s editors!

[^4]: As of August 2022, _Leo Edit_ has sadly [discontinued their cryptic crosswords](https://twitter.com/PuzzleTrip/status/1561064129422626822).

[^5]: `.puz` files were provided courtesy of [Michael F. Gill](https://bbtp.net/). As of August 2021, [_The New York Times_ no longer supports `.puz` files](https://www.nytimes.com/2021/08/02/crosswords/nyt-games-no-longer-available-on-across-lite-as-of-aug-9.html).

The data can be [viewed online](/data/clues) and downloaded for free
([CSV](/data/clues.csv?_size=max), [JSON](/data/clues.json), [SQLite](/data.db), [advanced](/data/clues#export)[^6]).
Detailed documentation can be found on [the datasheet](/datasheet)
and the source code for creating the dataset is [available on GitHub](https://github.com/eigenfoo/cryptics).

[^6]: The CSV request will only return the first 1000 rows, [click here](/data/clues.csv?_stream=on&_size=max) to stream all rows (this will take a while). The JSON request is paginated with 100 rows per page.

Send all comments, suggestions and complaints to [hello[&#230;]georgeho.org](mailto:hello[&#230;]georgeho.org).

Please share and enjoy!

\~ [George Ho](https://www.georgeho.org/)
