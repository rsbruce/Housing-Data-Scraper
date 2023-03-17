# Housing-Data-Scraper

## Quick start
Run `pip install -r requirements.txt` 

Execute `python main.py to-rent` or `python main.py for-sale` for property lettings and sales respectively. 

## Overview
This project is a collection of scripts for gathering day-by-day housing data from onthemarket.com

The scraper considers one locale (county or London borough) at a time as it makes requests to the server. By default, each request is for listings uploaded in the last 3 days. The data is collated into pandas DataFrames for processing before being saved.

By default, results will be stored as CSV files in the reuslts folder. The results files will contain raw data for a particular locale and will be timestamped. Locales are grouped by region. For use with MySQL see below.

## Usage with MySQL database
- Ensure MySQL is running on port 3306
- Database name: `OTM_Housing_Data`
- Database tables: `properties` and `lettings`
- Columns for both tables: `otm_id`, `price`, `bedrooms`, `area_sq_ft`, `latitude`, `longitude`, `date_accessed`, `locale`, `region`


## Environment files
- Store database credentials in the env file in the same format as in the example.env file provided
- Do not edit the locations folder or its contents. The files inside contain strings representing geographic regions which are used in request urls. E.g., 'county-durham'
    - For England, Wales and Scotland these are counties and for London these are boroughs
    - England, Wales, Scotland and London are designated as 'regions'; counties and boroughs are designated as 'locales' throughout the code and in the data (MySQL and CSV files)

## Scripts in this Project
### `main.py` 
- will trigger the main scraper function found in `scrape.py`
### `scrape.py` 
- is where the `Scraper` class lives along with the core functionality
### `otm_db.py`
- This is where the database functionality lives
- Saving DataFrames to the DB
- Retrieving DB records and returning a DataFrame
    - This returns a nationwide set of results similar to `collate.py`
### `collate results.py`
- Collates results from CSV files and writes a CSV into `results/nationwide`
### `simple_logging.py`
- Contains a simple function for timestamp formatting in the logs. Useful for checking how long each request has taken

## Data Compliance

On The Market state that scraping their site is within their terms of service _so long as the machine clearly idenitifies itself as doing so_. As such, there is a header field in the GET requests to do just this, found in `scrape.py`.
