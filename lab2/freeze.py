import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from flask_frozen import Freezer
from app import app

app.config['FREEZER_DESTINATION'] = os.path.join(os.path.dirname(__file__), 'build')
app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_IGNORE_MIMETYPE_WARNINGS'] = True

freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()
    print('Done! Static files in build/')
