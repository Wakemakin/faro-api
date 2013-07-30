import sys
import logging
import argparse

from faro_api import app

parser = argparse.ArgumentParser(description="Faro Service. Alpha 2")
parser.add_argument("--database", help="recreate database and initialize",
                    action="store_true")
parser.add_argument("--public", help="run on public host",
                    action="store_true")
args = parser.parse_args()

logger = logging.getLogger('faro_api')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

ch.setFormatter(formatter)
logger.addHandler(ch)

if args.database:
    logger.debug("Initializing database. Data dropped.")
    app(create_db=True)
    exit(0)

logger.debug("Starting faro-api node")
if args.public:
    app().run(debug=True, host='0.0.0.0', port=5001)
else:
    app().run(debug=True, host='127.0.0.1', port=5002)
