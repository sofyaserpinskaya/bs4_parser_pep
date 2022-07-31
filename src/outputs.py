import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT, FILE, PRETTY, RESULTS_DIR


FILE_SAVED = 'Файл с результатами был сохранён: {}.'


def default_output(results):
    for row in results:
        print(*row)


def pretty_output(results):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / RESULTS_DIR
    results_dir.mkdir(exist_ok=True)
    file_path = (
        results_dir /
        f'{cli_args.mode}_{dt.datetime.now().strftime(DATETIME_FORMAT)}.csv'
    )
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)
    logging.info(FILE_SAVED.format(file_path))


def control_output(results, cli_args):
    outputs = {
        PRETTY: (pretty_output, [results]),
        FILE: (file_output, [results, cli_args]),
        None: (default_output, [results]),
    }
    output_function, parameters = outputs[cli_args.output]
    output_function(*parameters)
