import pandas as pd
import requests
from bs4 import BeautifulSoup
import time


def search_on_habr(queries, pages):
    url = 'https://habr.com/ru/search/'

    def parse_article(article):
        date = (
            pd.to_datetime(
                article.find('time').get('datetime')
            ).date()
        )
        title = article.find('h2').text
        if not article.find('a', 'tm-title__link'):
            link = article.find('a').get('href')
        else:
            link = article.find('a', 'tm-title__link').get('href')
        full_link = f'https://habr.com{link}'
        likes = article.find('span', 'tm-votes-meter__value').text
        return {'date': date, 'title': title, 'link': full_link, 'likes': likes}

    result = pd.DataFrame()

    for query in queries:
        params = {'q': query}  # parameter for GET request

        for page in range(1, pages + 1):
            url_with_page = f'{url}page{page}/'
            response = requests.get(url_with_page, params).text  # GET-request for the query from the 'queries' list
            time.sleep(0.3)
            soup = BeautifulSoup(response, features='lxml')
            articles = soup.find_all('article', 'tm-articles-list__item')

            for article in articles:
                row = parse_article(article)  # the dict as a row for result DataFrame
                result = pd.concat([result, pd.DataFrame([row])], ignore_index=True)

    result.drop_duplicates(subset=['link'], inplace=True, ignore_index=True)
    return result


def get_full_text(posts_df):
    for i, link in enumerate(posts_df['link']):
        req = requests.get(link).text
        soup = BeautifulSoup(req, features='lxml')
        if soup.find('div', 'tm-article-body'):
            full_text = soup.find('div', 'tm-article-body').text.strip()
            posts_df.loc[i, 'text'] = full_text
    return posts_df


def main():
    queries = ['python', 'анализ данных']
    posts = search_on_habr(queries, 3)
    print(get_full_text(posts)[['title', 'text']].head())


main()
