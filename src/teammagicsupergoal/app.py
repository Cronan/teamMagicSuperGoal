from flask import Flask, render_template
from teammagicsupergoal import utils
import random

app = Flask(__name__)


def __get_start_data():
    secs = random.sample(utils.list_files(utils.PATHS[utils.STOCKS]), 10)
    secs.sort()
    keys = [s.split('.')[0] for s in secs]
    return {
        'secs': dict(zip(keys, secs))
    }

start_data = __get_start_data()
menus = ['Screen1', 'Screen2']


@app.route('/')
@app.route('/index')
def index():
    return render_template('clean_blog.html', heading='Ten Random Securities',
                           title='Team Magic Super-Goal',
                           subheading='Sitting in a row.',
                           menus=menus,
                           secs=start_data['secs'])


@app.route('/security/<security>')
def security(security):
    return render_template('security.html', heading='Security ' + security,
                           title='Team Magic Super-Goal - Security',
                           subheading='All the details.',
                           menus=menus,
                           security=security)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8750')
