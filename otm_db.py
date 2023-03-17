import mysql.connector
from simple_logging import timestamp
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def save(df: pd.DataFrame, listing_type: str):
    if listing_type not in ['for-sale', 'to-rent']:
      raise ValueError(f"Argument 'listing_type' must either be 'to-rent' or 'for-sale'. '{listing_type}' was given")

    if listing_type == 'for-sale': 
        table = 'properties' 
    elif listing_type == 'to-rent': 
        table = 'lettings'

    mydb = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PW"),
        database='OTM_Housing_Data'
    )
    mycursor = mydb.cursor()

    sql = "INSERT INTO " + table + " (otm_id, price, bedrooms, area_sq_ft, latitude, longitude, date_accessed, locale, region) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = [tuple(x) for x in list(df.to_numpy())]
    mycursor.executemany(sql, val)
    mydb.commit()
    print(f"{timestamp()}{mycursor.rowcount} record(s) inserted.")

def retrieve(listing_type: str) -> pd.DataFrame:
    if listing_type not in ['for-sale', 'to-rent']:
        raise ValueError(f"Argument 'listing_type' must either be 'to-rent' or 'for-sale'. '{listing_type}' was given")

    listings_type_tables = {'for-sale': 'properties', 'to-rent': 'lettings'}

    print(f"{timestamp()}Retrieving records for {listing_type}")

    mydb =  mysql.connector.connect(
        host="localhost",
        user="otm",
        password="password",
        database='OTM_Housing_Data'
    )
    mycursor = mydb.cursor()

    mycursor.execute(f"SELECT * FROM {listings_type_tables[listing_type]}")
    results = mycursor.fetchall()

    df = pd.DataFrame(results, columns=['otm_id', 'price', 'bedrooms', 'area_sq_ft', 'latitude', 'longitude', 'date_accessed', 'locale', 'region'])

    return df