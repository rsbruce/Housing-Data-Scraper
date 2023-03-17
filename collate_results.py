import pandas as pd
from pathlib import Path
import datetime
import re
import sys

def main(listing_type):
    root_dir = Path(__file__).parent
    results_dir = root_dir / 'results' / listing_type / 'nationwide'
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    results_file = results_dir / 'collated_results.csv'

    results_by_region = {
        'england': pd.DataFrame(),
        'london': pd.DataFrame(),
        'scotland': pd.DataFrame(),
        'wales': pd.DataFrame()
    }

    for region in results_by_region.keys():
        results_region_dir = root_dir / 'results' / listing_type / region

        locale_results_dfs = []

        for csv in results_region_dir.glob('**/*.csv'):
            matches = re.search('(.*)_results.csv', csv.name)
            file_date = matches.group(1)
            file_date = datetime.datetime.strptime(file_date, '%Y-%m-%d').date()

            df = pd.read_csv(csv).drop(columns='Unnamed: 0')

            locale = csv.parent.name
            locale_column = pd.Series([locale] * df.shape[0], name='locale', dtype='str')

            date_accessed = str(file_date)
            date_accessed_column = pd.Series([date_accessed] * df.shape[0], name='date_accessed', dtype='str')

            locale_results_dfs.append(pd.concat([df, date_accessed_column, locale_column], axis=1))

        if len(locale_results_dfs) > 0:
            region_results_df = pd.concat(locale_results_dfs).reset_index().drop(columns='index')
            region_column = pd.Series([region] * region_results_df.shape[0], name='region', dtype='str')
            results_by_region[region] = pd.concat([region_results_df, region_column], axis=1)

    nationwide_results = pd.concat(list(results_by_region.values())).reset_index().drop(columns='index')
    
    if nationwide_results.empty:
        return 'Query produced an empty set of results.'
    else:
        nationwide_results = nationwide_results.drop_duplicates(subset='id')
        nationwide_results = nationwide_results[nationwide_results['price'] != 0]
        nationwide_results.to_csv(results_file)

    return results_file
    
        
if __name__ == "__main__":
    valid_listing_types = ['for-sale', 'to-rent']
    try: 
        if sys.argv[1] in valid_listing_types:
            listing_type = sys.argv[1]
        else:
            raise ValueError
        main(listing_type)
    except:
        print(f"Usage: `python collate_results.py [LISTING_TYPE]` Where [LISTING TYPE] is one of {str(valid_listing_types)}")







