import os

import pandas as pd
from mkmsdk.api_map import _API_MAP
from mkmsdk.mkm import Mkm

from .market_interaction import MarketInteractionMixin


class MKMAccount(MarketInteractionMixin):
    articles: pd.DataFrame

    def __init__(self):
        self.api = Mkm(_API_MAP['2.0']['api'],
                       _API_MAP['2.0'][os.environ.get('ENVIRONMENT', 'api_root')])
        self.user_account = self.api.account_management.account().json()

    def fetch_stock(self):
        df = pd.DataFrame(self.api.stock_management.get_stock().json().get("article"))

        # extract english card name and language id
        df['enName'] = df['product'].str['enName']
        df['idLanguage'] = df['language'].str['idLanguage']

        self.articles = df.drop(columns=['language', 'comments', 'inShoppingCart',
                                         'product', 'lastEdited'])

        return self.articles

    def update_stock(self):
        articles_to_update = self.articles[['idArticle', 'count', 'adjusted_price']]
        articles_to_update.rename(columns={'adjusted_price': 'price'}, inplace=True)

        articles_to_update = articles_to_update.to_dict('records')

        # as api only supports updating 100 items at a time, slice array into chunks of 100
        for left_slice in range(0, len(articles_to_update), 100):
            right_slice = left_slice + 100
            record_slice = articles_to_update[left_slice:right_slice]
            
            response = self.api.stock_management.change_articles(
                    data={'action': 'put', 'article': articles_to_update})

            success = len(response.json().get('updatedArticles'))
            failure = len(response.json().get('notUpdatedArticles'))

            print(f'Updated {success} articles successful and {failure} unsuccessful!')
