import sys
import logging
import argparse


parser = argparse.ArgumentParser(description="Faro Service. Alpha 2")
parser.add_argument("--database", help="recreate database and initialize",
                    action="store_true")
parser.add_argument("--public", help="run on public host",
                    action="store_true")
args = parser.parse_args()

if args.database:
    import os

    _basedir = os.path.abspath(os.path.dirname(__file__))
    db_file = os.path.join(_basedir, 'faro.db')
    try:
        with open(db_file):
            os.remove(db_file)
            pass
    except IOError:
        pass
    #db.init_db()

logger = logging.getLogger('faro_api')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

ch.setFormatter(formatter)
logger.addHandler(ch)

from faro_api import app
logger.debug("Starting faro-api node")
if args.public:
    app().run(debug=True, host='0.0.0.0', port=5001)
else:
    app().run(debug=True, host='127.0.0.1', port=5002)
