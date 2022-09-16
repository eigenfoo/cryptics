from setuptools import find_packages, setup

DESCRIPTION = (
    "A Python library to scrape various cryptic crossword blogs and parse the "
    "scraped blog posts into a structured dataset of cryptic crossword clues."
)

setup(
    name="cryptics",
    version="0.0.0",
    url="https://github.com/eigenfoo/cryptics",
    author="George Ho",
    author_email="hello[æ]georgeho.org",
    description=DESCRIPTION,
    packages=find_packages(),
)
