from exceptions import ParserFindTagException

from bs4 import BeautifulSoup
from requests import RequestException


REQUEST_ERROR = 'Возникла ошибка при загрузке страницы {}.'
SEARCH_TAG_ERROR = 'Не найден тег {tag} {attrs}.'


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        raise ConnectionError(REQUEST_ERROR.format(url))


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=({} if attrs is None else attrs))
    if searched_tag is None:
        raise ParserFindTagException(
            SEARCH_TAG_ERROR.format(tag=tag, attrs=attrs)
        )
    return searched_tag


def get_soup(session, url):
    return BeautifulSoup(get_response(session, url).text, features='lxml')
