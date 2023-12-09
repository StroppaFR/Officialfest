from itertools import chain
import os

# Website lang, should be in ['fr', 'en', 'es]
LANG = os.environ.get('OFFICIALFEST_LANG') or 'fr'
LOCALE = {'fr': 'fr_FR', 'en': 'en_US', 'es': 'es_ES'}[LANG]

# Forum configuration
FORUM_THREADS_PER_PAGE = 15
FORUM_MESSAGES_PER_PAGE = 10 # note that the first page will always contain one more message
FORUM_ALLOWED_PICTOS = list(chain(range(115), range(116, 118), range(1000, 1186), range(1190, 1239)))

# Forum search function configuration
FORUM_SEARCH_MAX_STRINGS = 5
FORUM_SEARCH_MAX_RESULTS = 1000
FORUM_SEARCH_DEFAULT_MIN_DATE = '2006-02-27'
FORUM_SEARCH_DEFAULT_MAX_DATE = '2023-12-31'

# Hammerfest website domains that will replace original URLs (www.hammerfest.fr, etc.) in forum.html/redirect
HAMMERFEST_FR_URL='https://fr.officialfest.nikost.dev'
HAMMERFEST_ES_URL='https://es.officialfest.nikost.dev'
HAMMERFEST_EN_URL='https://en.officialfest.nikost.dev'

# Score pages configuration
SCORES_PER_PAGE = 30
SCORES_RISING_USERS_PER_PYRAMID_STEP = {
        'fr': {1: 1, 2: 10, 3: 100, 4: 1000},
        'en': {1: 1, 2:  2, 3:  10, 4:   50},
        'es': {1: 1, 2: 10, 3: 100, 4:  500}
}[LANG]
LEAGUES_PARAM = '|'.join(str(v) for v in sorted(SCORES_RISING_USERS_PER_PYRAMID_STEP.values()))
