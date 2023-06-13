import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = 'https://habr.com/ru/search/'
queries = ['python', 'анализ данных']


def search_on_habr(queries):
    result = pd.DataFrame()
    for query in queries:
        params = {'q': query}
        response = requests.get(URL, params).text  # GET-request for the query from the 'queries' list
        soup = BeautifulSoup(response, features='lxml')
        articles = soup.findAll('div', 'tm-article-snippet')
        for article in articles:
            date = (
                pd.to_datetime(
                    article.find('span', 'tm-article-datetime-published')
                    .find('time').get('datetime')
                ).date()
            )
            title = article.find('h2', 'tm-title tm-title_h2').find('span').text
            link = article.find('h2', 'tm-title tm-title_h2').find('a').get('href')
            full_link = f'habr.com{link}'
            row = {'date': date, 'title': title, 'link': full_link}
            result = pd.concat([result, pd.DataFrame([row])], ignore_index=True)
    result.drop_duplicates(subset=['link'], inplace=True)
    return result


print(search_on_habr(queries))


