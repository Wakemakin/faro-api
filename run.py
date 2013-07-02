import argparse


parser = argparse.ArgumentParser(description="Faro Service. Alpha 2")
parser.add_argument("--database", help="initialize database only",
                    action="store_true")
args = parser.parse_args()

if args.database:
    import os

    from faro_api.database import init_db

    _basedir = os.path.abspath(os.path.dirname(__file__))
    db_file = os.path.join(_basedir, 'faro-api.db')
    try:
        with open(db_file):
            os.remove(db_file)
            pass
    except IOError:
        pass
    init_db()
    exit(0)

from faro_api import app
app.run(debug=True, host='127.0.0.1', port=5002)