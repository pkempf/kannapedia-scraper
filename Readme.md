# Kannapedia scraper, by Peter Kempf

### How to use

This is currently a very WIP scraper for individual Kannapedia listings. To use it, after installing with `pip install -r requirements.txt`, then call `python scraper.py` using the flag `-u`, supplying a url suffix (e.g. srr14419582), and optionally with the flag -d, to download the files.

For example: `python scraper.py -u srr14419582`

This specific example has already been called in the uploaded repository, and the resulting CSV files have been stored in the `/UC_170-srr14419582/` directory.

### Current output

This program currently outputs three main CSV files: general information (strain_name.metadata.csv), cannabinoid and terpinoid information (strain_name.chemicals.csv), and variant information (strain_name.variants.csv). If the -d flag is selected, it will also download all of the available files into that directory; if it is not selected, it will instead list the links in the last field of the metadata CSV file.
