import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from pathlib import Path
from datetime import date
from simple_logging import timestamp

class Scraper():
    def __init__(self, listing_type, region, locale) -> None:
        # Set query data
        self.listing_type = listing_type
        self.region = region
        self.locale = locale
        # Set base HTTP request data
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0',
            'x-description': 'Housing data collection bot'
            }
        self.base_url = 'https://www.onthemarket.com'

    def set_listings_index_soup(self, page_num=1):
        listings_index_url = '/'.join([self.base_url, self.listing_type, '1-bed-property', self.locale]) + f'?page={page_num}&recently-added=24-hours'
        htmlDoc = requests.get(listings_index_url, headers=self.headers).text
        self.listings_index_soup = BeautifulSoup(htmlDoc, features="html.parser")

    def set_listing_soup_and_text(self, id=''):
        htmlDoc = requests.get("/".join([self.base_url, 'details', id]), headers=self.headers).text
        self.listing_soup = BeautifulSoup(htmlDoc, features="html.parser")
        self.listing_text = self.listing_soup.get_text()

    def find_property_ids_on_page(self, page_num=1):
        self.set_listings_index_soup(page_num=page_num)
        links_on_current_page = self.listings_index_soup.find_all('a')
        property_ids = []
        for link in links_on_current_page:
            href = link.get('href')
            matches = re.search('\/details\/(\d+)\/$', href)
            if matches: 
                property_ids.append(matches.group(1))
        return list(set(property_ids))

    def find_price(self):
        if self.listing_type == 'for-sale':
            price_matches = re.search('(£[\d|\,|\s]+)', self.listing_text)
        else:
            price_matches = re.search('(£[\d|\,|\s]+pcm)', self.listing_text)
        return re.sub('[£|\s|\,|pcm]', '', price_matches[0]) if price_matches else 0

    def find_listing_bedroom_count(self):
        bedroom_matches = re.search('(\d+)\sbedroom', self.listing_text)
        return bedroom_matches.group(1) if bedroom_matches else 0

    def find_listing_area_sq_ft(self):
        area_sq_ft_matches = re.search('([\d\,]+)\ssq\sft', self.listing_text)
        return re.sub(',', '', area_sq_ft_matches.group(1)) if area_sq_ft_matches else 0

    def find_listing_coords(self):
        scripts = [str(script) for script in self.listing_soup.find_all('script')]
        for script in scripts:
            coords_matches = re.findall('center=(-*\d+\.\d+)%2C(-*\d+\.\d+)', script)
            if coords_matches:
                return coords_matches[0][0], coords_matches[0][1]
        return 0, 0

    def scrape(self):
        # Find number of pages of listings
        self.set_listings_index_soup(page_num=1)
        links_on_first_page = self.listings_index_soup.find_all('a')
        n_pages = 1
        for link in links_on_first_page:
            href = link.get('href')
            matches = re.search('page=(\d+)', href)
            n_pages = max(n_pages, int(matches.group(1)) + 1) if matches else n_pages

        # Fill a list with dataframes which each represent one page of results
        pages_of_results = [pd.DataFrame()] * n_pages
        for page_num in range(n_pages):
            print(f'{timestamp()}Page {page_num + 1} of {n_pages}')

            # Fill dataframe row by row
            property_ids = self.find_property_ids_on_page(page_num=page_num)
            n_properties_on_page = len(property_ids)
            proto_df = {
                'id': [0] * n_properties_on_page, 
                'price': [0] * n_properties_on_page, 
                'bedrooms': [0] * n_properties_on_page, 
                'area_sq_ft': [0] * n_properties_on_page, 
                'latitude': [0] * n_properties_on_page, 
                'longitude': [0] * n_properties_on_page,
                'date_accessed': [date.today().strftime("%Y-%m-%d")] * n_properties_on_page,
                'locale': [self.locale] * n_properties_on_page,
                'region': [self.region] * n_properties_on_page
            }

            for index, id in enumerate(property_ids):
                self.set_listing_soup_and_text(id=id)
                proto_df['id'][index] = id
                proto_df['price'][index] = self.find_price()
                proto_df['bedrooms'][index] = self.find_listing_bedroom_count()
                proto_df['area_sq_ft'][index] = self.find_listing_area_sq_ft()
                proto_df['latitude'][index], proto_df['longitude'][index] = self.find_listing_coords()

            pages_of_results[page_num] = pd.DataFrame(proto_df)

        # Join pages of results as one dataframe and save
        df = pd.concat(pages_of_results).reset_index().drop(columns='index').drop_duplicates(subset='id')

        return df