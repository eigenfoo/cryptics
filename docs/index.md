---
title: A Dataset of Cryptic Crossword Clues
author-meta: George Ho
description-meta: A dataset of cryptic crossword clues, collected from various blogs and publicly available digital archives.
---

`cryptics.eigenfoo.xyz` is a dataset of cryptic crossword clues[^1], collected
from various blogs and publicly available digital archives. I originally
started this project to practice my web scraping and data engineering skills,
but as it's evolved I hope it can be a resource to solvers and constructors of
cryptic crosswords.

[^1]: If you're new to cryptic crosswords, rejoice! A whole new world awaits you! The New Yorker has [an excellent introduction to cryptic crosswords](https://www.newyorker.com/puzzles-and-games-dept/cryptic-crossword/reintroducing-the-new-yorkers-cryptic-crossword), and Matt Gritzmacher has [a daily newsletter with links to crosswords](https://crosswordlinks.substack.com/).

The project scrapes several blogs and digital archives for cryptic crosswords.
Out of these collected web pages, the clues, answers, clue numbers, blogger's
explanation and commentary, puzzle title and publication date are all parsed
and extracted into a tabular dataset. The result (as of September 2021) is **a
little over half a million clues from cryptic crosswords over the past twelve
years**, which makes for a rich and peculiar dataset.

Currently the sources for clues are:

- [Big Dave's Crossword Blog](http://bigdave44.com/) (_The Daily Telegraph_, _The Sunday Telegraph_)
- [Cru Cryptic Archive](https://archive.nytimes.com/www.nytimes.com/premium/xword/cryptic-archive.html) (_The New York Times_ "Cru" Forums)
- [Fifteensquared](https://www.fifteensquared.net/) (_Financial Times_, _The Guardian_, _The Independent_)
- [The Hindu Crossword Corner](https://thehinducrosswordcorner.blogspot.com/) (_The Hindu_)
- [Times for the Times](https://times-xwd-times.livejournal.com/) (_The Times_ of London)

The data can be [viewed online](/clues/clues) and downloaded for free
([CSV](https://cryptics.eigenfoo.xyz/clues/clues.csv?_stream=on&_size=max),
[JSON](/clues/clues.json), [SQLite](/clues.db),
[advanced](/clues/clues#export)[^2]). Detailed documentation can be found on
[the datasheet](/datasheet) and the source code for creating the dataset is
[available on GitHub](https://github.com/eigenfoo/cryptics).

[^2]: The CSV request will only return the first 1000 rows, [click here](/clues/clues.csv?_stream=on&_size=max) to stream all rows (this will take a while). The JSON request is paginated with 100 rows per page.

Send all comments, suggestions and complaints to
[george[&#230;]eigenfoo.xyz](mailto:george[&#230;]eigenfoo.xyz).

Please share and enjoy!

\~ [George Ho](https://www.eigenfoo.xyz/)
