from flask import render_template, redirect, request, flash, url_for, g
from flask.ext.login import LoginManager, current_user, login_user, login_required, logout_user
from app import app, db, lm, reddit_api, models
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REDIRECT_URI
import praw

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/authorize')
def authorize():
    # TODO: verfify state
    # TODO: abstract praw for multiple instances

    url = reddit_api.generate_url('uniqueKey', 'identity', True)

    return redirect(url)

@app.route('/authorize_callback')
def authorize_callback():
    # TODO: check if state is same
    # TODO: error handling
    # TODO: login user
    # TODO: abstract for multiple praw instances
    # TODO: praw-multiprocess

    if request.args.get('error'):
        error = request.args.get('error')
        flash(error)
        if error == 'access_denied' and g.user is not None and g.user.is_authenticated():
            return redirect(url_for('logout'))
        return render_template('index.html')
    else:
        user = reddit_api.create_user(request.args.get('code'))
        return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))

    user = models.User.query.get(1)
    login_user(user)

    return redirect(request.args.get('next') or url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@lm.user_loader
def load_user(id):
    return models.User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
