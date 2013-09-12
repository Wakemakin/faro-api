import logging
import argparse

import faro_auth

parser = argparse.ArgumentParser(description="Faro Service. Alpha 2")
parser.add_argument("--database", help="recreate database and initialize",
                    action="store_true")
parser.add_argument("--public", help="run on public host",
                    action="store_true")
args = parser.parse_args()

logger = logging.getLogger('faro_auth')

if args.database:
    logger.debug("Initializing database. Data dropped.")
    faro_auth.app(create_db=True)
    exit(0)

logger.debug("Starting faro-auth node")
if args.public:
    faro_auth.app().run(debug=True, host='0.0.0.0', port=5001)
else:
    faro_auth.app().run(debug=True, host='127.0.0.1', port=5002)
