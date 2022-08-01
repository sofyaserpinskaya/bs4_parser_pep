from exceptions import ParserFindTagException

from bs4 import BeautifulSoup
from requests import RequestException


RESPONSE_ERROR = 'Не удалось получить страницу {}.'
REQUEST_ERROR = 'Возникла ошибка при загрузке страницы {}.'
SEARCH_TAG_ERROR = 'Не найден тег {tag} {attrs}.'


def get_response(session, url):
    try:
        response = session.get(url)
        if response is None:
            raise ValueError(RESPONSE_ERROR.format(url))
        response.encoding = 'utf-8'
        return response
    except RequestException:
        raise RequestException(REQUEST_ERROR.format(url))


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=({} if attrs is None else attrs))
    if searched_tag is None:
        raise ParserFindTagException(
            SEARCH_TAG_ERROR.format(tag=tag, attrs=attrs)
        )
    return searched_tag


def get_soup(session, url):
    response = get_response(session, url)
    return BeautifulSoup(response.text, features='lxml')
