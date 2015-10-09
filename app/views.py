from flask import render_template, redirect, request, flash, url_for, g
from flask.ext.login import LoginManager, current_user, login_user, login_required, logout_user
from app import app, db, lm, reddit_api, models, forms
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REDIRECT_URI
import praw, random

@app.route('/')
@app.route('/index')
def index():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/authorize')
def authorize():
    # TODO: verify state
    # TODO: error handling

    url = reddit_api.generate_url('uniqueKey', ['identity', 'history'], True)

    return redirect(url)

@app.route('/authorize_callback')
def authorize_callback():
    # TODO: check if state is same
    # TODO: complete error handling

    if request.args.get('error'):
        error = request.args.get('error')
        flash(error)

        if error == 'access_denied' and g.user is not None and g.user.is_authenticated():
            return redirect(url_for('logout'))

        return render_template('index.html')

    elif request.args.get('code'):
        return redirect(url_for('login', code=request.args.get('code')))

    else:
        flash('error')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET','POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('dashboard'))

    if request.args.get('code'):
        code = request.args.get('code')

        url = reddit_api.login_reddit_user(code)

        return redirect(request.args.get('next') or url)

    else:
        flash('Invalid request.')
        return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = forms.RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = models.User.query.filter_by(username=form.username.data).first()
        user.username = form.username.data
        user.email = form.email.data
        user.age = form.age.data
        user.gender = form.gender.data
        user.location = form.location.data
        user.bio = form.bio.data
        db.session.commit()
        return redirect(url_for('match'))
    return render_template('register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/match')
@login_required
def match():
    return render_template('match.html')

@app.route('/friend')
@login_required
def friend():
    return render_template('friend.html')

@app.route('/friend_match')
@login_required
def friend_match():
    #TODO: use counter or similar to get people who are favorites of multiples of your favorites
    user = g.user

    favs = user.favorited_subs().all()

    matches = []

    for sub in favs:
        users = sub.favorited_users().all()

        for u in users:
            if u.username is not user.username and user.is_matched(u) == False:
                if models.User.query.filter_by(reddit_username=u.username).first():
                    favs = models.User.query.filter_by(reddit_username=u.username).first().favorited_subs().all()
                else:
                    favs = reddit_api.get_favorite_subs(u)

                lis = ['onsite', u.username, sub.name]
                for fav in favs:
                    lis.append(fav.name)
                matches.append(lis)

    if len(matches) > 3:
        matches = random.sample(matches, 3)

    if len(matches) == 0:
        matches = reddit_api.get_offsite_users(favs)

        if len(matches) == 0:
            matches = None

    return render_template('results.html', matches=matches)

@app.route('/date')
@login_required
def date():
    return redirect(url_for('friend'))

@app.route('/matches')
@login_required
def matches():
    return render_template('matches.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/accept', methods=['POST', 'GET'])
@login_required
def accept():
    user = g.user
    match_username = request.form['match']

    if models.User.query.filter_by(username=match_username).first():
        match_user = models.User.query.filter_by(username=match_username).first()

        m = user.match(match_user)
        db.session.add(m)
        db.session.commit()

    return 'success'

@lm.user_loader
def load_user(id):
    return models.User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
