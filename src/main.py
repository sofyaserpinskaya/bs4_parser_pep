import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, DOWNLOADS_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEPS_URL,
    STATUS_PATTERN
)
from exceptions import ParserFindTagException
from outputs import control_output
from utils import find_tag, get_soup


PYTHON_VERSIONS_ERROR = 'Не найден список c версиями Python'
UNEXPECTED_STATUSES = (
    'Несовпадающие статусы:\n'
    '{}\n'
    'Статус в карточке: {}\n'
    'Ожидаемые статусы: {}'
)

ARGUMENTS_LOG = 'Аргументы командной строки: {}.'
ARCHIVE_SAVED_LOG = 'Архив был загружен и сохранён: {}.'
ERROR_LOG = 'Ошибка при выполнении.'
PARSER_STARTED_LOG = 'Парсер запущен!'
PARSER_FINISHED_WORK_LOG = 'Парсер завершил работу.'


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    sections_by_python = get_soup(
        session, whats_new_url
    ).select_one(
        '#what-s-new-in-python div.toctree-wrapper'
    ).select('li.toctree-l1')
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_link = urljoin(whats_new_url, section.select_one('a')['href'])
        try:
            soup = get_soup(session, version_link)
            results.append((
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' ')
            ))
        except ConnectionError:
            continue
    return results


def latest_versions(session):
    ul_tags = get_soup(
        session, MAIN_DOC_URL
    ).select('div.sphinxsidebarwrapper ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ValueError(PYTHON_VERSIONS_ERROR)
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in a_tags:
        text_match = re.search(
            r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)',
            a_tag.text
        )
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (a_tag['href'], version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    archive_url = urljoin(
        downloads_url,
        get_soup(
            session, downloads_url
        ).select_one('table.docutils td > a[href$="pdf-a4.zip"]')['href']
    )
    downloads_dir = BASE_DIR / DOWNLOADS_DIR
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / archive_url.split('/')[-1]
    with open(archive_path, 'wb') as file:
        file.write(session.get(archive_url).content)
    logging.info(ARCHIVE_SAVED_LOG.format(archive_path))


def pep(session):
    peps = get_soup(session, PEPS_URL).select('#numerical-index tbody tr')
    results = defaultdict(int)
    unexpected_statuses = []
    for pep in tqdm(peps):
        try:
            pep_url = urljoin(
                PEPS_URL,
                find_tag(
                    pep, 'a', attrs={'class': 'pep reference internal'}
                )['href']
            )
            status = STATUS_PATTERN.search(
                find_tag(get_soup(session, pep_url), 'dl').text
            ).groups()[0]
            results[status] += 1
            expected_status = EXPECTED_STATUS[find_tag(pep, 'td').text[1:]]
            if status not in expected_status:
                unexpected_statuses.append(
                    (str(pep_url), str(status), str(expected_status))
                )
        except (ConnectionError, ParserFindTagException):
            continue
    for item in unexpected_statuses:
        pep_url, status, expected_status = item
        logging.info(UNEXPECTED_STATUSES.format(*item))
    return [
        ('Статус', 'Количество'),
        *sorted(results.items()),
        ('Total', sum(results.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info(PARSER_STARTED_LOG)
    args = configure_argument_parser(
        MODE_TO_FUNCTION.keys()
    ).parse_args()
    logging.info(ARGUMENTS_LOG.format(args))
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        results = MODE_TO_FUNCTION[args.mode](session)
        if results is not None:
            control_output(results, args)
    except Exception:
        logging.exception(msg=ERROR_LOG, stack_info=True)
    logging.info(PARSER_FINISHED_WORK_LOG)


if __name__ == '__main__':
    main()
