import dask.dataframe as dd
import pandas as pd
from mkmsdk.mkm import Mkm

from .helper import convert_boolean


class MarketInteractionMixin:
    api: Mkm
    user_account: dict

    def _validate_market_article(self, market_article: dict) -> bool:
        same_user_check = (market_article['seller']['idUser'] ==
                           self.user_account['account']['idUser'])
        if market_article.get('isPlayset') or same_user_check:
            return False
        return True

    def _market_lookup(self, article, max_results: int = 500) -> list:
        response = self.api.market_place.articles(
                product=article.idProduct,
                params={'minUserScore': 1,
                        'idLanguage': article.idLanguage,
                        'minCondition': article.condition,
                        'isFoil': convert_boolean(article.isFoil),
                        'isSigned': convert_boolean(article.isSigned),
                        'isAltered': convert_boolean(article.isAltered),
                        'maxResults': max_results})

        market_articles = response.json()['article']
        return list(filter(self._validate_market_article, market_articles))

    @staticmethod
    def _extract_prices(market_articles: list) -> pd.Series:
        prices = [article['price'] for article in market_articles]
        return pd.Series(prices)

    @staticmethod
    def _calculate_means(prices: pd.Series) -> pd.Series:
        return pd.Series({
                '3_mean': prices.iloc[:3].mean().round(2),
                '5_mean': prices.iloc[:5].mean().round(2),
                '10_mean': prices.iloc[:10].mean().round(2),
                '50_mean': prices.iloc[:50].mean().round(2),
                'total_mean': prices.mean().round(2),
        })

    def _lookup_and_calculate(self, article):
        market_articles = self._market_lookup(article)
        market_prices = self._extract_prices(market_articles)
        return self._calculate_means(market_prices)

    def fetch_market_means(self, max_partitions: int = 100) -> pd.DataFrame:
        articles = self.fetch_stock()

        ddf = dd.from_pandas(articles, npartitions=min(articles.shape[0], max_partitions))
        market_means = ddf.apply(self._lookup_and_calculate, axis=1,
                                 meta={'3_mean': float, '5_mean': float, '10_mean': float,
                                       '50_mean': float, 'total_mean': float})

        combined_ddf = dd.concat([ddf, market_means], axis=1)

        self.articles = combined_ddf.compute(scheduler='threads')

        return self.articles

    def adjust_price(self, chosen_mean_column: str) -> pd.DataFrame:
        if chosen_mean_column not in self.articles.columns:
            print(f'The chosen mean column {chosen_mean_column} does not exist')

        else:
            self.articles['chosen_mean'] = chosen_mean_column
            self.articles['change'] = self.articles[chosen_mean_column] - self.articles.price
            self.articles['adjusted_price'] = self.articles[chosen_mean_column]
            
        return self.articles
