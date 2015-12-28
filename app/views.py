from flask import render_template, redirect, request, flash, url_for, g, jsonify, session
from flask.ext.login import LoginManager, current_user, login_user, login_required, logout_user
from app import app, db, lm, reddit_api, models, forms, socketio
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REDIRECT_URI, REDDIT_STATE
from flask_socketio import emit, send, join_room, leave_room, rooms
import praw, random, datetime, string, json, os
from sqlalchemy import func, and_
from haversine import haversine
from math import cos, pi

# TODO (secondary) refactor views.py

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('match'))
    return render_template('index.html', title='Reddimatch - Where redditors meet!', page_class='index_page')

@app.route('/authorize')
def authorize():
    # session['state'] = REDDIT_STATE
    url = reddit_api.generate_url(REDDIT_STATE, ['identity', 'history'], True)

    return redirect(url)

@app.route('/authorize_callback')
def authorize_callback():
    code = request.args.get('code', None)
    state = request.args.get('state', None).lower().strip()
    error = request.args.get('error', None)

    if error:
        if error == 'access_denied':
            return redirect(url_for('logout'))
        return redirect(url_for('index'))

    elif code:
        # if state == session['state']:
        return redirect(url_for('login', title='Reddimatch', code=request.args.get('code')))
    else:
        return redirect(url_for('index'))

@app.route('/login', methods=['GET','POST'])
def login():
    code = request.args.get('code', None)

    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if code:
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
    return render_template('register.html', title='Reddimatch - Register', form=form, page_class='register_page')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = forms.DashboardForm(request.form)
    user = current_user

    if request.method == 'POST' and form.validate():
        user.username = form.username.data

        if form.age.data:
            user.age = int(form.age.data)
        user.gender_id = int(form.gender.data)
        user.desired_gender_id = int(form.desired_gender.data)
        user.date_searchable = not form.searchable.data
        user.min_age = int(form.min_age.data)
        user.max_age = int(form.max_age.data)
        user.search_radius = int(form.radius.data)

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
                    return render_template('dashboard.html', title='Reddimatch - My Profile', form=form, page_class='dashboard_page')

                subreddit = models.Subreddit(name=sub)
                db.session.add(subreddit)

        db.session.commit()

        return render_template('dashboard.html', title='Reddimatch - My Profile', form=form, page_class='dashboard_page')

    if user.gender_id:
        print user.gender_id
        form.gender.default = user.gender_id
    else:
        form.gender.default = 1

    if user.desired_gender_id:
        print user.desired_gender_id
        form.desired_gender.default = user.desired_gender_id
    else:
        form.desired_gender.default = 2

    if user.min_age:
        print 'yo!'
        print user.min_age
        form.min_age.default = user.min_age
    else:
        form.min_age.default = 18

    if user.max_age:
        form.max_age.default = user.max_age
    else:
        form.max_age.default = 35

    if user.search_radius:
        form.radius.default = user.search_radius
    else:
        form.radius.default = 50

    if user.date_searchable is not None:
        form.searchable.default = not user.date_searchable
    else:
        form.searchable.default = False

    form.process()

    return render_template('dashboard.html', page_class='dashboard_page', title='Reddimatch - My Profile',form=form)

@app.route('/match')
@login_required
def match():
    return render_template('match.html', title='Reddimatch', page_class='match_page')

@app.route('/quick_match')
@login_required
def quick_match():
    #TODO use counter or similar to get people who are favorites of multiples of your favorites
    user = current_user

    favs = user.favorited_subs().all()

    matches = []

    for sub in favs:
        users = sub.favorited_users().all()

        for u in users:
            if u.username is not user.username and not user.is_matched(u, 'friend') and not user.is_rejected(u, 'friend') and not user.has_sent_match(u, 'friend'):

                u.status = 'onsite'
                u.type = 'friend'

                matches.append(u)

    if len(matches) > 3:
        matches = random.sample(matches, 3)

    if len(matches) == 0:
        matches = reddit_api.get_offsite_users(favs)

        if len(matches) == 0:
            matches = None

    return render_template('results.html', title='Reddimatch', page_class='results_page', matches=matches)

@app.route('/date', methods = ['GET', 'POST'])
@login_required
def date():
    form = forms.DateRegistrationForm(request.form)

    if request.method == 'POST' and form.validate():

        # check for no lat and long

        # get form data
        current_user.age = int(form.age.data)
        current_user.gender_id = int(form.gender.data)
        current_user.desired_gender_id = int(form.desired_gender.data)
        current_user.date_searchable = not form.searchable.data
        current_user.min_age = int(form.min_age.data)
        current_user.max_age = int(form.max_age.data)
        current_user.search_radius = int(form.radius.data)
        radius = int(form.radius.data)

        db.session.add(current_user)
        db.session.commit()


        if radius > 100:
            radius = None

        if current_user.latitude and current_user.longitude:

            # get matches, favorite subs disregarded
            if radius:
                # distance stuff
                deltaLat = float(radius/69.174 + 2)
                lat_min = current_user.latitude - deltaLat
                lat_max = current_user.latitude + deltaLat

                users = models.User.query.filter(and_(models.User.latitude >= lat_min,  models.User.latitude <= lat_max, models.User.age >= current_user.min_age, models.User.age <= current_user.max_age, models.User.date_searchable, models.User.username != current_user.username, models.User.gender_id == current_user.desired_gender_id, models.User.desired_gender_id == current_user.gender_id))
            else:
                users = models.User.query.filter(and_(models.User.age >= current_user.min_age, models.User.age <= current_user.max_age, models.User.date_searchable, models.User.username != current_user.username, models.User.gender_id == current_user.desired_gender_id, models.User.desired_gender_id == current_user.gender_id))
        else:
            distance = None
            if not radius:
                users = models.User.query.filter(and_(models.User.age >= current_user.min_age, models.User.age <= current_user.max_age, models.User.date_searchable, models.User.username != current_user.username, models.User.gender_id == current_user.desired_gender_id, models.User.desired_gender_id == current_user.gender_id))
            else:
                users = []

        mutual_sub_matches = []
        matches = []
        secondary_matches = []

        print 1

        print 2
        # get matches that also have a similiar favorite sub
        # for sub in current_user.favorited_subs().all():
        #     print 2.5
        #
        #     for u in users:
        #         favs = u.favorited_subs().all()
        #
        #         for f in favs:
        #             if f in current_user.favorited_subs().all():
        #                 mutual_sub_matches.append(u)


        print 3
        # get rid of dupes caused by multiple favorite subs
        # mutual_sub_matches = list(set(mutual_sub_matches))
        #
        # if len(mutual_sub_matches) > 0:
        #     for u in mutual_sub_matches:
        #         if not current_user.is_matched(u, 'date') and not current_user.is_rejected(u, 'date') and not current_user.has_sent_match(u, 'date'):
        #
        #             if u.latitude and u.longitude:
        #                 distance = abs(haversine((current_user.latitude, current_user.longitude),(u.latitude,u.longitude),miles=True))
        #                 u.distance = int(distance)
        #
        #             u.status = 'onsite'
        #             u.type = 'date'
        #
        #             if radius:
        #                 if distance:
        #                     if distance <= radius:
        #                         matches.append(u)
        #             else:
        #                 matches.append(u)
        # print 4

        if len(matches) > 0 and len(matches) < 3 or len(matches) == 0:

            for u in users:

                if not current_user.is_matched(u, 'date') and not current_user.is_rejected(u, 'date') and not current_user.has_sent_match(u, 'date'):
                    if u.latitude and u.longitude and current_user.latitude and current_user.longitude:
                        distance = abs(haversine((current_user.latitude, current_user.longitude),(u.latitude,u.longitude),miles=True))
                        u.distance = int(distance)
                    u.status = 'onsite'
                    u.type = 'date'

                    if radius:
                        if distance:
                            if distance <= radius:
                                secondary_matches.append(u)
                    else:
                        secondary_matches.append(u)

            matches.extend(secondary_matches)

            matches = list(set(matches))

        print 5

        if len(matches) > 3:
            matches = random.sample(matches, 3)

        if len(matches) == 0:
            matches = None

        print 6

        return render_template('results.html',title='Reddimatch', page_class='results_page',matches=matches)

    if current_user.gender_id:
        print current_user.gender_id
        form.gender.default = current_user.gender_id
    else:
        form.gender.default = 1

    if current_user.desired_gender_id:
        print current_user.desired_gender_id
        form.desired_gender.default = current_user.desired_gender_id
    else:
        form.desired_gender.default = 2

    if current_user.min_age:
        form.min_age.default = current_user.min_age
    else:
        form.min_age.default = 18

    if current_user.max_age:
        form.max_age.default = current_user.max_age
    else:
        form.max_age.default = 35

    if current_user.search_radius:
        form.radius.default = current_user.search_radius
    else:
        form.radius.default = 50

    if current_user.date_searchable is not None:
        form.searchable.default = not current_user.date_searchable
    else:
        form.searchable.default = False

    form.process()

    return render_template('date.html', title='Reddimatch', page_class='match_page date_page',form=form);

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/accept', methods=['POST', 'GET'])
@login_required
def accept():
    print -1
    user = current_user
    match_username = request.form['username']
    match_type = request.form['match_type']


    print match_username
    print 0

    if models.User.query.filter_by(username=match_username).first():
        match_user = models.User.query.filter_by(username=match_username).first()
        print 1

        if not user.is_matched(match_user, match_type):
            print 2
            m = user.send_match_request(match_user, match_type)
            db.session.add(m)
            db.session.commit()

    print 3
    return 'success'

@app.route('/reject', methods=['POST', 'GET'])
@login_required
def reject():
    user = current_user
    unmatch_username = request.form['username']
    match_type = request.form['match_type']

    if models.User.query.filter_by(username=unmatch_username).first():
        reject_user = models.User.query.filter_by(username=unmatch_username).first()

        user.unmatch(reject_user, match_type)

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
    match_type = request.args.get('match_type', None)
    print match_type
    if username is None:
        return 'no_username'

    else:
        if models.User.query.filter_by(username=username):

            to_user = models.User.query.filter_by(username=username).first()
            to_id = to_user.id

            if current_user.is_matched(to_user, match_type):
                messages_list = []

                if models.Message.query.filter_by(from_id=current_user.id, to_id=to_id, match_type=match_type).count > 0:

                    messages = models.Message.query.filter_by(from_id=current_user.id, to_id=to_id, match_type=match_type).all()

                    for m in messages:
                        message = {}

                        message_object = {
                            'to':m.to.username,
                            'from':m.author.username,
                            'content':m.content,
                            'match_type':m.match_type
                        }

                        message[str(m.time_sent)] = message_object

                        messages_list.append(message)

                if models.Message.query.filter_by(to_id=current_user.id, from_id=to_id, match_type=match_type):

                    messages =  models.Message.query.filter_by(to_id=current_user.id,from_id=to_id, match_type=match_type).all()

                    for m in messages:
                        message = {}

                        message_object = {
                            'to':m.to.username,
                            'from':m.author.username,
                            'content':m.content,
                            'match_type':m.match_type
                        }

                        message[str(m.time_sent)] = message_object

                        messages_list.append(message)

                messages_list.sort()

                if not messages_list:
                    return 'no_messages'
                else:
                    return jsonify(results = messages_list)

            elif current_user.has_received_match(to_user, match_type) and not current_user.is_rejected(to_user, match_type):
                return "request"
            elif current_user.has_sent_match(to_user, match_type) and not current_user.is_rejected(to_user, match_type):
                return "unconfirmed"

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

@app.route('/is_online', methods=['POST','GET'])
@login_required
def is_online():
    if current_user.is_authenticated:
        users = request.json
        user_dict = {}

        for username in users:
            if models.User.query.filter_by(username=username).first():
                user = models.User.query.filter_by(username=username).first()
                user_dict[user.username] = user.is_online

        return jsonify(user_dict)

@app.route('/chat')
@app.route('/chat/<username>')
@login_required
def messages(username=None):
    if current_user.get_matches() or current_user.get_match_requests() > 0 or current_user.get_pending_matches():
        return render_template('messages.html',title='Reddimatch - Messages',page_class='messages_page')

    else:
        return redirect(url_for('match'))

@app.route('/get_user_info')
@login_required
def get_user_info():
    if current_user.is_authenticated:

        username = request.args.get('username', None)
        match_type = request.args.get('match_type', None)

        if username is None or match_type is None:
            return 'false'

        if(models.User.query.filter_by(username=username).first()):

            user = models.User.query.filter_by(username=username).first()

            if current_user.is_matched(user, match_type) or current_user.has_received_match(user, match_type) or current_user.has_sent_match(user, match_type) and not current_user.is_rejected(user, match_type):

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
                user_dict['match_type'] = match_type

                fav_subs = user.favorited.all()
                fav_subs_list = []

                for sub in fav_subs:
                    fav_subs_list.append(sub.name)

                user_dict['fav_subs'] = fav_subs_list

                return jsonify(user_dict)

@app.route('/set_location')
@login_required
def set_location():
    latitude = float(request.args.get('latitude'))
    longitude = float(request.args.get('longitude'))

    current_user.latitude = latitude
    current_user.longitude = longitude

    db.session.add(current_user)
    db.session.commit()

    return 'true'

# @app.route('/get_user')
# @login_required
# def get_info():
#     username = request.args.get('username', None)
#
#     if username == current_user.username:
#         u = models.User.query.filter_by(username=username).first()
#         return jsonify(u)

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

    print 34

    if from_user.is_matched(to_user, data['match_type']):
        emit('message response', {'msg': data['msg'], 'to': data['to'], 'from':data['from'], 'match_type': data['match_type']}, room=data['to'])
        emit('message response', {'msg': data['msg'], 'to': data['to'], 'from':data['from'], 'match_type': data['match_type']}, room=data['from'])
        m = models.Message(content=data['msg'],from_id=from_user.id,to_id=to_user.id,time_sent=datetime.datetime.now(), match_type=data['match_type'])
        db.session.add(m)
        db.session.commit()

@app.route('/privacy')
def privacy():
    return render_template('privacy.html', title="Reddimatch - Privacy", page_class="privacy_page")

@lm.user_loader
def load_user(id):
    return models.User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html',title='These are not the droids you\'re looking for.',page_class='404_page'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html',title='Something went wrong.',page_class='500_page'), 500
