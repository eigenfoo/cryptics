---
title: A Dataset of Cryptic Crossword Clues
nav-links: |
  <nav>
    <a href="/">Home</a>
    &centerdot;
    <a href="/datasheet">Datasheet</a>
    &centerdot;
    <a href="/clues/clues">Data</a>
  </nav>
---

`cryptics.eigenfoo.xyz` is a dataset of cryptic crossword clues[^1], collected
from cryptic crossword blogs and publicly available digital cryptic crossword
archives.

[^1]: If you're new to cryptic crosswords, rejoice! A whole new world awaits you! The New Yorker has [an excellent introduction to cryptic crosswords](https://www.newyorker.com/puzzles-and-games-dept/cryptic-crossword/reintroducing-the-new-yorkers-cryptic-crossword), and Matt Gritzmacher has [a daily newsletter with links to crosswords](https://crosswordlinks.substack.com/).

I originally started this project to practice my webscraping and data
engineering skills, but as it's evolved I hope it can be a resource to solvers
and constructors of cryptic crosswords.

`cryptics.eigenfoo.xyz` scrapes several blogs and archives for cryptic
crosswords. Out of the scraped web pages, the clue, answer, clue number, title,
date are parsed out. The result (as of September 2021) is a bit more than half
a million clues from cryptic crosswords over the past twelve years, which makes
for a rich and peculiar dataset.

Currently the sources for clues are:

- [Big Dave's Crossword Blog](http://bigdave44.com/) (_The Daily Telegraph_, _The Sunday Telegraph_)
- [Cru Cryptic Archive](https://archive.nytimes.com/www.nytimes.com/premium/xword/cryptic-archive.html) (_The New York Times_ "Cru" Forums)
- [Fifteensquared](https://www.fifteensquared.net/) (_Financial Times_, _The Guardian_, _The Independent_)
- [Times for the Times](https://times-xwd-times.livejournal.com/) (_The Times_ of London)

The data can be [viewed online](/clues/clues) and downloaded for free
([CSV](/clues/clues.csv?_size=max), [JSON](/clues/clues.json),
[SQLite](/clues.db)). Detailed documentation can be found on [the
datasheet](/static/datasheet.html) and the source code for creating the dataset
is [available on GitHub](https://github.com/eigenfoo/cryptics).

Send all comments, suggestions and complaints to
[george[&#230;]eigenfoo.xyz](mailto:george[&#230;]eigenfoo.xyz).

Please share and enjoy!

\~ [George Ho](https://www.eigenfoo.xyz/)
