import sys
import os
from pathlib import Path
from scrape import Scraper
from simple_logging import timestamp
import otm_db
from dotenv import load_dotenv
import mysql.connector
from datetime import date

load_dotenv()

if __name__ == "__main__":
   listing_type = sys.argv[1]
   if listing_type not in ['for-sale', 'to-rent']:
      raise ValueError(f"Argument 'listing_type' must either be 'to-rent' or 'for-sale'. '{listing_type}' was given")

   locations_dir = Path(__file__).parent / 'locations'
   locations_files = [locations_dir / 'england.txt', locations_dir / 'london.txt', locations_dir / 'scotland.txt', locations_dir / 'wales.txt']

   try:
      mydb = mysql.connector.connect(
         host=os.getenv("DB_HOST"),
         user=os.getenv("DB_USER"),
         password=os.getenv("DB_PW"),
         database='OTM_Housing_Data'
      )
      use_db = True
      print("Connected to database")
   except:
      use_db = False
      print("Database connection failed. Results will be stored as CSV files the results folder.")

   for locations_file in locations_files:
      with open(locations_file) as file:
         locations = [line.rstrip() for line in file if line[0] != '#']
         region = Path(file.name).stem

      for location in locations:
         print(f'{timestamp()}Properties {listing_type.replace("-", " ")} in {location}')
         scraper = Scraper(listing_type, region, location)
         
         df = scraper.scrape()
         
         if use_db:
            otm_db.save(df, listing_type)
         else:
            results_dir = Path(__file__).parent / 'results' / listing_type / region / location
            Path(results_dir).mkdir(parents=True, exist_ok=True)
            results_file = results_dir / f'{date.today().strftime("%Y-%m-%d")}_results.csv'
            
            df.to_csv(results_file)