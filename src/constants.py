import re
from pathlib import Path


MAIN_DOC_URL = 'https://docs.python.org/3/'
PEPS_URL = 'https://peps.python.org/'


BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = 'downloads'
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'
RESULTS_DIR = 'results'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
STATUS_PATTERN = re.compile('.*Status:\n(?P<status>.*)')


EXPECTED_STATUS = {
    'A': ['Active', 'Accepted'],
    'D': ['Deferred'],
    'F': ['Final'],
    'P': ['Provisional'],
    'R': ['Rejected'],
    'S': ['Superseded'],
    'W': ['Withdrawn'],
    '': ['Draft', 'Active'],
}
FILE_OUTPUT_ARGUMENT = 'file'
PRETTY_OUTPUT_ARGUMENT = 'pretty'
