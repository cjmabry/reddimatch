from flask import render_template, redirect, request, flash, url_for, g, jsonify, session
from flask.ext.login import LoginManager, current_user, login_user, login_required, logout_user
from app import app, db, lm, reddit_api, models, forms, socketio
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REDIRECT_URI
from flask_socketio import emit, send, join_room, leave_room, rooms
import praw, random, datetime, string
from pprint import pprint
from sqlalchemy import func, and_
from haversine import haversine
from math import cos, pi

# TODO (secondary) when opening new tabs user is not logged in new tabs
# TODO (secondary) refactor views.py

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('match'))
    return render_template('index.html')

@app.route('/authorize')
def authorize():
    # TODO verify state
    # TODO error handling

    url = reddit_api.generate_url('uniqueKey', ['identity', 'history'], True)

    return redirect(url)

@app.route('/authorize_callback')
def authorize_callback():
    # TODO check if state is same
    # TODO complete error handling

    if request.args.get('error'):
        error = request.args.get('error')
        flash(error)

        if error == 'access_denied' and current_user is not None and current_user.is_authenticated:
            return redirect(url_for('logout'))

        return render_template('index.html')

    elif request.args.get('code'):
        return redirect(url_for('login', code=request.args.get('code')))

    else:
        flash('error')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user is not None and current_user.is_authenticated:
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

    if current_user.registered:
        return redirect(url_for('match'))

    form = forms.RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = current_user
        user.username = form.username.data
        user.bio = form.bio.data
        user.newsletter = True
        user.registered = True
        user.created_on = datetime.datetime.now()
        user.email_verified = False

        if form.email.data:
            user.email = form.email.data

        favorite_subs = []
        favorite_subs.append(form.favorite_sub_1.data.lower())

        if form.favorite_sub_2.data:
            favorite_subs.append(form.favorite_sub_2.data.lower())

        if form.favorite_sub_3.data:
            favorite_subs.append(form.favorite_sub_3.data.lower())

        user.unfavorite_all()

        for sub in favorite_subs:

            # strip /r/ from name
            if '/' in sub:
                sub = sub.split('/')[-1]

            if models.Subreddit.query.filter_by(name = sub).first() is None:
                subreddit = models.Subreddit(name=sub)
                db.session.add(subreddit)
                db.session.commit()
                user.favorite(subreddit)
            else:
                subreddit = models.Subreddit.query.filter_by(name = sub).first()
                user.favorite(subreddit)

        db.session.commit()
        return redirect(url_for('match'))
    return render_template('register.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = forms.RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = current_user
        user.username = form.username.data

        if form.email.data:
            user.email = form.email.data

        user.bio = form.bio.data
        favorite_subs = []
        favorite_subs.append(form.favorite_sub_1.data)

        if form.favorite_sub_2.data:
            favorite_subs.append(form.favorite_sub_2.data)

        if form.favorite_sub_3.data:
            favorite_subs.append(form.favorite_sub_3.data)

        user.unfavorite_all()

        for sub in favorite_subs:
            if models.Subreddit.query.filter_by(name=sub).first():
                sub = models.Subreddit.query.filter_by(name=sub).first()
                user.favorite(sub)
            elif models.Subreddit.query.filter_by(name=sub).first() is None:
                r = reddit_api.praw_instance()
                try:
                    r.get_subreddit(sub, fetch=True)
                except Exception as e:
                    flash(e)
                    return render_template('dashboard.html', form=form)

                subreddit = models.Subreddit(name=sub)
                db.session.add(subreddit)
                db.session.commit()
                user.favorite(subreddit)
            else:
                print 'error'

        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html', form=form)

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
    #TODO use counter or similar to get people who are favorites of multiples of your favorites
    user = current_user

    favs = user.favorited_subs().all()

    matches = []

    for sub in favs:
        users = sub.favorited_users().all()

        for u in users:
            if u.username is not user.username and not user.is_matched(u) and not user.is_rejected(u) and not u.is_rejected(user):

                u.status = 'onsite'
                u.type = 'friend'

                matches.append(u)

    if len(matches) > 3:
        matches = random.sample(matches, 3)

    if len(matches) == 0:
        matches = reddit_api.get_offsite_users(favs)

        if len(matches) == 0:
            matches = None

    return render_template('results.html', matches=matches)

@app.route('/date', methods = ['GET', 'POST'])
@login_required
def date():
    form = forms.DateRegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        current_user.age = form.age.data
        current_user.gender_id = form.gender.data
        current_user.date_searchable = not form.searchable.data

        radius = form.radius.data
        min_age = form.min_age.data
        max_age = form.max_age.data
        desired_gender = form.desired_gender.data

        db.session.add(current_user)
        db.session.commit()

        return redirect(url_for('date_match', age=form.age.data,gender_id=form.gender.data, radius=form.radius.data, min_age = min_age, max_age= max_age, desired_gender=desired_gender))

    return render_template('date.html', form=form);

@app.route('/date_match', methods=['GET','POST'])
@login_required
def date_match():

    age = int(request.args.get('age'))
    gender_id = int(request.args.get('gender_id'))
    radius = int(request.args.get('radius'))
    min_age = int(request.args.get('min_age'))
    max_age = int(request.args.get('max_age'))
    latitude = float(current_user.latitude)
    longitude = float(current_user.longitude)
    desired_gender = int(request.args.get('desired_gender'))


    print gender_id
    print desired_gender

    # print 'age'
    # print age
    #
    # print 'gender'
    # print gender

    # print 'radius'
    # print radius
    # print 'min_age'
    # print min_age
    # print 'max_age'
    # print max_age
    # print 'latitude'
    # print latitude
    # print 'longitude'
    # print longitude
    # print 'desired_gender'
    # print desired_gender

    matches = []

    # mileInLongitudeDegree = 69.174 * cos(latitude)

    deltaLat = radius/69.174 + 2
    # deltaLong = radius / mileInLongitudeDegree

    lat_min = latitude - deltaLat
    lat_max = latitude + deltaLat
    # long_min = longitude - deltaLong
    # long_max = longitude + deltaLong

    # print 'mileInLongitudeDegree'
    # print mileInLongitudeDegree
    # print 'lat_min'
    # print lat_min
    # print 'lat_max'
    # print lat_max
    # print 'long_min'
    # print long_min
    # print 'long_max'
    # print long_max


    if radius == 101:
        users = models.User.query.filter(and_(models.User.age >= min_age, models.User.age <= max_age, models.User.date_searchable))
    else:
        users = models.User.query.filter(and_(models.User.latitude >= lat_min,  models.User.latitude <= lat_max, models.User.age >= min_age, models.User.age <= max_age, models.User.date_searchable))

    print users.all()

    for u in users:

        if u.username is not current_user.username and not current_user.is_matched(u) and not current_user.is_rejected(u) and not u.is_rejected(current_user) and u.gender_id == desired_gender:

            distance = abs(haversine((latitude, longitude),(u.latitude, u.longitude),miles=True))

            u.status = 'onsite'
            u.type = 'date'
            u.distance = int(distance)

            if radius == 101:
                matches.append(u)
            elif distance <= radius:
                matches.append(u)

    if len(matches) > 3:
        matches = random.sample(matches, 3)

    if len(matches) == 0:
        matches = None

    return render_template('results.html',matches=matches)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/accept', methods=['POST', 'GET'])
@login_required
def accept():
    user = current_user
    match_username = request.form['username']

    if models.User.query.filter_by(username=match_username).first():
        match_user = models.User.query.filter_by(username=match_username).first()

        if user.is_matched(match_user):
            print 'Already matched'

        else:
            m = user.match(match_user)
            db.session.add(m)
            db.session.commit()

    return 'success'

@app.route('/reject', methods=['POST', 'GET'])
@login_required
def reject():
    user = current_user
    unmatch_username = request.form['username']

    if models.User.query.filter_by(username=unmatch_username).first():
        reject_user = models.User.query.filter_by(username=unmatch_username).first()

        print reject_user

        user.reject(reject_user)
        db.session.commit()


    return 'success'

@app.route('/get_username')
@login_required
def get_username():
    if current_user.is_authenticated and current_user.username is not None:
        return jsonify({
            'username':current_user.username
        })
    else:
        return False

@app.route('/get_messages')
@login_required
def get_messages():
    username = request.args.get('username', None)

    if username is None:
        return 'no_username'

    else:
        if models.User.query.filter_by(username=username):

            to_user = models.User.query.filter_by(username=username).first()
            to_id = to_user.id

            if current_user.is_matched(to_user) and to_user.is_matched(current_user):

                messages_list = []

                if models.Message.query.filter_by(from_id=current_user.id, to_id=to_id):

                    messages =  models.Message.query.filter_by(from_id=current_user.id,to_id=to_id).all()

                    for m in messages:
                        message = {}

                        message_object = {
                            'to':m.to.username,
                            'from':m.author.username,
                            'content':m.content
                        }

                        message[str(m.time_sent)] = message_object

                        messages_list.append(message)

                if models.Message.query.filter_by(to_id=current_user.id, from_id=to_id):

                    messages =  models.Message.query.filter_by(to_id=current_user.id,from_id=to_id).all()

                    for m in messages:
                        message = {}

                        message_object = {
                            'to':m.to.username,
                            'from':m.author.username,
                            'content':m.content
                        }

                        message[str(m.time_sent)] = message_object

                        messages_list.append(message)

                messages_list.sort()

                if not messages_list:
                    return 'no_messages'
                else:
                    return jsonify(results = messages_list)

            elif current_user.is_matched(to_user) and not to_user.is_matched(current_user):
                return "unconfirmed"
            else:
                return "request"

@app.route('/get_avatar')
@login_required
def get_avatar():
    if current_user.is_authenticated:
        username = request.args.get('username', None)
        size = request.args.get('size', None)

        if username is not None and models.User.query.filter_by(username=username).first():
            user = models.User.query.filter_by(username=username).first()

            if size is not None:
                avatar = user.avatar(int(size))

            else:
                avatar = user.avatar(300)

        return avatar

@app.route('/is_online')
@login_required
def is_online():
    if current_user.is_authenticated:
        username = request.args.get('username')

        if models.User.query.filter_by(username=username).first():
            user = models.User.query.filter_by(username=username).first()

            if user.is_online:
                return 'true'
            else:
                return 'false'

        else:
            return 'false'

@app.route('/chat')
@app.route('/chat/<username>')
@login_required
def messages(username=None):
    if current_user.get_matches() or current_user.get_match_requests() > 0:
        return render_template('messages.html')

    else:
        return redirect(url_for('match'))

@app.route('/get_user_info')
@login_required
def get_user_info():
    if current_user.is_authenticated:

        username = request.args.get('username', None)

        if username is None:
            return 'false'

        if(models.User.query.filter_by(username=username).first()):

            user = models.User.query.filter_by(username=username).first()

            user_dict = {}

            user_dict['username'] = user.username
            user_dict['profile_photo_url'] = user.profile_photo_url
            user_dict['age'] = user.age
            user_dict['gender'] = str(user.gender).title()
            user_dict['location'] = user.location
            user_dict['latitude'] = user.latitude
            user_dict['longitude'] = user.longitude
            user_dict['bio'] = user.bio
            user_dict['avatar'] = str(user.avatar(100))

            fav_subs = user.favorited.all()
            fav_subs_list = []

            for sub in fav_subs:
                fav_subs_list.append(sub.name)

            user_dict['fav_subs'] = fav_subs_list

            pprint(user_dict)

        return jsonify(user_dict)

@app.route('/set_location')
@login_required
def set_location():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    current_user.latitude = latitude
    current_user.longitude = longitude

    db.session.add(current_user)
    db.session.commit()

    return 'true'

@socketio.on('connect')
def connect_handler():
    if current_user.is_authenticated:

        current_user.last_online = datetime.datetime.now()

        for room in rooms():
            leave_room(room)
        username = current_user.username
        join_room(username)
        emit('message response', {'msg': 'Joined room ' + username}, room=username)

        current_user.is_online = True
        db.session.commit()

        for room in rooms():
            print 'In room ' + room
    else:
        return False

@socketio.on('disconnect')
def disconnect_handler():
    if current_user.is_authenticated:

        current_user.is_online = False
        current_user.last_online = datetime.datetime.now()
        db.session.commit()
    else:
        return False

@socketio.on('message')
def message(data):
    from_user = models.User.query.filter_by(username=data['from']).first()
    to_user = models.User.query.filter_by(username=data['to']).first()

    if from_user.is_matched(to_user) and to_user.is_matched(from_user):
        emit('message response', {'msg': data['msg'], 'to': data['to'], 'from':data['from']}, room=data['to'])
        emit('message response', {'msg': data['msg'], 'to': data['to'], 'from':data['from']}, room=data['from'])
        m = models.Message(content=data['msg'],from_id=from_user.id,to_id=to_user.id,time_sent=datetime.datetime.now())
        db.session.add(m)
        db.session.commit()

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

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
