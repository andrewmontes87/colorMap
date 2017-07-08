import os

from flask import Flask, flash, session, escape, \
    send_from_directory, url_for, render_template, \
    request, abort, redirect, Markup
from flask_script import Manager
from flask_moment import Moment


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'development_secret_key')

manager = Manager(app)
moment = Moment(app)


def before_route_load():
    url_for('static', filename='img/**/*.jpg')
    return True

@app.route('/')
def home_route():
    before_route_load()

    return render_template('home.html', 
                            page_title='Home')


@app.route('/hello')
def hello():
    return 'Hello, World'


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html',
                            page_title='Not Found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html',
                            page_title='Server Error'), 500


if __name__ == "__main__":
    manager.run()