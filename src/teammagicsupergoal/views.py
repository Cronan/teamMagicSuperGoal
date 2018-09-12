from teammagicsupergoal import app
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    return render_template('clean_blog_basic.html', heading='Home',
                           title='teamMagicSuperGoal',
                           subheading='The magic super goal page.')
