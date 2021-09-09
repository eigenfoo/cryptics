---
title: Datasheet
nav-links: |
  <nav>
    <a href="/static/index.html">Home</a>
    &centerdot;
    <a href="/static/datasheet.html">Datasheet</a>
    &centerdot;
    <a href="/clues/clues">Data</a>
  </nav>
---

## Motivation

### Why was this dataset created?

This dataset was originally a project for me to practice my webscraping and
data processing skills. Since then, it has evolved to become a potential
resource for cryptic crossword solvers and constructors - for example, one
might use this dataset as a lookup table for answers, or to see how an answer
has been clued in the past by other constructors.

While there is prior art in datasets for cryptic crossword clue datasets
([_Decrypting Cryptic Crosswords_ by Rozner et
al.](https://arxiv.org/abs/2104.08620) and [_Cryptonite_ by Efrat et
al.](https://arxiv.org/abs/2103.01242)), to my knowledge this is the first such
dataset that is at least as large as the research datasets and is openly
accessible.

### Who created this dataset and on whose behalf? Who funded the creation of this dataset?

This dataset was created by me ([George Ho](https://eigenfoo.xyz)) as a side
project in my free time. Any and all expenses were covered by me personally.

## Composition

### What do the rows that comprise this dataset represent?

Each row represents one clue from a published cryptic crossword.

### How many rows are there in total (of each type, if appropriate)?

Clues are sourced from three cryptic crossword blogs and a few online archives
of cryptic crosswords (for more details, see the _Collection Process_ section).

As of September 2021, the number of rows break down as so:

| Source                                                                         | Number of Clues |
|--------------------------------------------------------------------------------|----------------:|
| http://bigdave44.com/                                                          |          208009 |
| http://www.fifteensquared.net/                                                 |          206493 |
| https://times-xwd-times.livejournal.com/                                       |           97238 |
| https://archive.nytimes.com/www.nytimes.com/premium/xword/cryptic-archive.html |            6858 |
| Total                                                                          |          518598 |

### Does this dataset contain all possible rows or is it a sample (not necessarily random) of rows from a larger set?

The dataset is a large portion of the scraped blog posts (and may be considered
exhaustive or nearly so).

However, there are many reasons why a clue may be missing from the dataset - in
order for a clue to be included, the following must be true:

1. The crossword must be covered by a blog
   * The three blogs cover exclusively British newspapers. As such, the
     resulting dataset is heavy in British jargon, such as slang, idioms or
     names of British towns or royalty.
2. The blog must publish a blog post
   * In particular, the blog must include at least the clues and answers of the
     crossword.
   * Many blog posts from the sources are not about crosswords at all (e.g.
     they may be administrative announcements), and those that are may not
     include the clues (instead simply publishing the puzzle name, clue
     numbers, answers and annotations).
3. The blog post must be parseable
   * As explained in the _Collection Process_ section, the clues and answers
     are extracted from the raw HTML by a collection of parsing functions. If
     none of the parsing functions successfully return parsed clues, the raw
     HTML is deemed "unparseable" and is skipped.

### What data does each row consist of?

There are seven columns:

1. `clue`, e.g. `labourers going around spotted tools (8)`
2. `answer`, e.g. `HANDSAWS`
3. `definition`, e.g. `tools`
4. `clue_number`, e.g. `17a`
5. `puzzle_date`: date the puzzle was published, e.g. `2017-08-25`
6. `puzzle_name`: name of the publication and/or puzzle, e.g. `Quick Cryptic 904`
7. `puzzle_url`: if available, a URL to the puzzle itself.

### Is any information missing from individual rows?

Less than 5% of all rows include a `puzzle_url`. Some data may also be missing
(or be `NaN`s) due to data preprocessing errors (see below).

Furthermore, some columns have been scrubbed prior to publishing:

- `source_url`: the URL of the scraped blog post from which this clue comes
- `annotation`: a brief explanation and/or commentary from the blogger
- `is_reviewed`: whether this clue has been reviewed by a human evaluator
- `reviewed_datetime`: if the clue `is_reviewed`, the datetime at which it was
  reviewed

These columns have been dropped to respect the copyright of the scraped blogs.
While it is fair use to republish the cryptic clues in a transformatively
different structured format, the blogs hold the copyright to any annotations
and commentary on the clues.

### Are there any errors, sources of noise, or redundancies in this dataset?

Yes. As described below, errors may be introduced in the dataset through human
error by the blogger, or through machine error by the parsing code.

Human errors may include:

- missing enumerations (i.e. the clue does not specify the number of letters in
  the answer)
- mismatched parentheses or braces
- typos

Machine errors may include:

- missing or redundant definitions
- multi-word answers split across the `answer` and `annotation` columns

### Is this dataset self-contained, or does it link to or otherwise rely on external resources (e.g., websites, tweets, other datasets)?

Asides from the `puzzle_url`, the dataset is self-contained. Users are
encouraged to ignore the `puzzle_url` column and treat the dataset as
self-contained, as the `puzzle_url` column is sparse, does not bring much value
and may be removed in a future version of the dataset.

### Does this dataset contain data that might be considered confidential?

No. All cryptic crossword clues have been published (either in newspapers or
in online publications) and are not confidential.

### Does this dataset contain data that, if viewed directly, might be offensive, insulting, threatening, or might otherwise cause anxiety?

To my knowledge, no. These clues are published in widely syndicated newspapers
or online publications, and are thus unlikely to contain offensive content.

However, identifying offensive content is difficult, particularly for cryptic
crosswords: even if the answer itself is not an offensive word, the wordplay
may involve words or logic that may be offensive. This is probably best
explained by quoting a [Guardian article on cryptic
crosswords](https://www.theguardian.com/crosswords/crossword-blog/2013/dec/18/cryptic-crosswords-too-rude-for-americans-puzzle):

> Even puzzles that appear innocent may have something suggestive squirrelled
> away, as with an early Guardian grid by the setter Paul, which contained,
> without further comment, the entries HORSEMEN, WIDOW TWANKEY, CHARDONNAY,
> SCUNTHORPE, HOT WATER and, of course, MISHIT.

## Collection Process

### How was the data associated with each row acquired? What mechanisms or procedures were used to collect the data?

The data collection process breaks down into roughly three parts.

The first part is simply scraping all the web pages and writing the HTML to a
SQLite table to avoid re-requesting them. Web scraping was done using the
Python `requests` library.

The second part is a collection of functions that each take the scraped HTML
and attempt to parse out the data using `beautifulsoup` and `pandas`. Since
blog posts are written by a small team of individual bloggers - many of whom
stick with a particular blog post template - there are only a small number
(less than a dozen) of distinct "types" of blog posts, from an HTML parsing
perspective. Accordingly, there are around a dozen functions, which are called
successively until one of them doesn't crash and returns a table of parsed
clues. This parsed table then gets written to SQLite.

The third part is human evaluation of the clues. Between the human errors from
the blogger and machine errors from the parsing code, it's instructive to
manually look through a random sample of the clues for any errors. It's
possible to gamify this with a CLI "cryptic practice tool"
([`review.py`](https://github.com/eigenfoo/cryptics/blob/main/cryptics/review.py)),
which displays a random clue, allows the user to ask for crossing letters as
hints, prompts the user for the answer, and allows the user to edit the clue if
necessary. This has surfaced a decent number of systematic errors, which can be
corrected by either modifying the parsing code and re-parsing the saved HTML,
or by simply running ad hoc SQL queries against the table of parsed clues.
However, since I can't possibly manually review all these clues by myself, it's
admittedly difficult to see what further value human evaluation brings.

### Who was involved in the data collection process and how were they compensated?

Since this dataset is the result of a side project in my free time, the only
person involved in the data collection process was me (George Ho). I was not
compensated for this work.

### Over what timeframe was the data collected?

The scraped blog posts cover crosswords published from January 2009 to
September 2021: a twelve year period. New blog posts are being published daily
and can be parsed to augment the dataset.

## Preprocessing and Cleaning

### Was any preprocessing/cleaning of the data done?

Yes. As discussed above, the raw HTML is preprocessed/cleaned by parsing and
extracting the clues from the unstructured HTML into a structured table of
clues and answers. This parsing is the main value-add of this dataset over the
raw blog posts.

### Is the software used to preprocess/clean the data available?

[Yes, you can view it on GitHub.](https://github.com/eigenfoo/cryptics) The
following four modules contain the preprocessing and cleaning code:

- [`cryptics/lists.py`](https://github.com/eigenfoo/cryptics/blob/main/cryptics/lists.py)
- [`cryptics/puzzes.py`](https://github.com/eigenfoo/cryptics/blob/main/cryptics/puzzes.py)
- [`cryptics/tables.py`](https://github.com/eigenfoo/cryptics/blob/main/cryptics/tables.py)
- [`cryptics/text.py`](https://github.com/eigenfoo/cryptics/blob/main/cryptics/text.py)

### Was the raw data saved in addition to the preprocessed/cleaned data (e.g. to support unanticipated future uses)?

Yes: as discussed above, the raw HTML for the blog posts have been saved to
avoid re-requesting. However, the raw HTML is not published, due to size
constraints.

Please [contact
me](https://raw.githubusercontent.com/eigenfoo/eigenfoo.xyz/master/assets/images/email.png)
if you'd like to receive the raw data. Alternatively, you can simply rerun the
open source [`cryptics`](https://github.com/eigenfoo/cryptics) library to
recreate the dataset yourself.

## Uses

### Has this dataset been used for any tasks already? Is there a repository that links to any or all papers or systems that use this dataset?

The most immediate use case is for cryptic crossword constructors and solvers,
both as a lookup table for answers and also to see how an answer has been clued
in the past by other constructors.

Beyond that though, I am unaware of other uses for the dataset. If you are
using it, please [let me know](https://raw.githubusercontent.com/eigenfoo/eigenfoo.xyz/master/assets/images/email.png)!

## Distribution

### How will this dataset will be distributed (e.g., tarball on website, API, GitHub)?

The dataset will be distributed via a hosted [Datasette](https://datasette.io/)
site. For more information, please watch Simon Willison's [introduction to
Datasette on YouTube](https://youtu.be/7kDFBnXaw-c).

### Is this dataset distributed under a copyright or other intellectual property (IP) license, and/or under applicable terms of use (ToU)?

No.

### Have any third parties imposed IP-based or other restrictions on the data?

No.

## Maintenance

### Who is supporting/hosting/maintaining this dataset?

Me, [George Ho](https://eigenfoo.xyz/).

### How can the owner/curator/manager of this dataset be contacted?

I can be reached via [email](https://raw.githubusercontent.com/eigenfoo/eigenfoo.xyz/master/assets/images/email.png).

### Is there an erratum?

Not currently, although there will eventually be a `CHANGELOG.md`.

### Will this dataset be updated (e.g., to correct labeling errors, add new rows, delete rows)?

Yes. There is no set schedule for releases of new versions of the data. Updates
will most likely entail:

- adding new rows from new blog posts
- correcting parsing errors (described above), either by overwriting the row or
  deleting it entirely

### Will older versions of this dataset continue to be supported/hosted/maintained?

Older versions of the data will _not_ be supported, hosted or maintained.

### If others want to extend/augment/build on/contribute to this dataset, is there a mechanism for them to do so?

Yes. Please [raise an issue on
GitHub](https://github.com/eigenfoo/cryptics/issues) if you have a specific
issue in mind. Otherwise, please reach out to me [via
email](https://raw.githubusercontent.com/eigenfoo/eigenfoo.xyz/master/assets/images/email.png).
