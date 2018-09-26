from flask import Flask, render_template, request
from pymdicator import indicators
import random
import os
from pandas import read_csv
from numpy import isnan


SAMPLE_SIZE = 100


def __get_start_data():
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data/')
    all_secs = os.listdir(data_dir)
    work_secs = random.sample(all_secs, SAMPLE_SIZE)
    secs = random.sample(all_secs, 10)
    return {
        'secs': dict(zip([s.split('.')[0] for s in secs], secs)),
        'work_secs': dict(
            zip(
                work_secs, 
                [read_csv(
                    os.path.join(
                        data_dir, s)) for s in work_secs]))
    }

start_data = __get_start_data()
menus = ['Momentum']
app = Flask(__name__)
MOMENTUM = "momentum"
DEFAULT_INDICATOR = MOMENTUM
DEFAULT_MOMENTUM_DAYS = 12
MOMENTUM_DAYS = DEFAULT_MOMENTUM_DAYS


def momentum_run(work_secs):
    momIndicator = indicators.Momentum(MOMENTUM_DAYS)
    return momIndicator.calculate_current(start_data['work_secs'])


INDICATOR_RUNNER = {
    MOMENTUM: momentum_run
}


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', heading='Home',
                           title='Team Magic Super-Goal',
                           subheading='Super. Magic. A team with a goal.',
                           menus=menus,
                           secs=start_data['work_secs'])



@app.route('/momentum', methods=["GET", "POST"])
def momentum_page():
    return render_template('momentum.html', heading='Momentum',
                           title='Team Magic Super-Goal - Momentum',
                           subheading='It''s what keeps you rolling down the hill.',
                           menus=menus,
                           momentum_days=MOMENTUM_DAYS)


@app.route('/results', methods=["POST"])
def momentum():
    MOMENTUM_DAYS = request.form.get("momentum-number", DEFAULT_MOMENTUM_DAYS)
    indicator = request.form.get("indicator", "")

    mom = INDICATOR_RUNNER[indicator](start_data['work_secs'])
    clean_mom = dict((k, v) for k, v in mom.iteritems() if not isnan(v))

    return render_template('results.html', heading='Results',
                           title='Team Magic Super-Goal - Results',
                           subheading='Results from {indicator} indicator.'.format(indicator=indicator),
                           menus=menus,
                           indicator_results=clean_mom,
                           momentum_days=MOMENTUM_DAYS)


@app.route('/list')
def security_list():
    return render_template('security-list.html', heading='Ten Random Securities',
                           title='Team Magic Super-Goal - List',
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
