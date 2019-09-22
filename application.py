#!/usr/bin/python

__author__ = "Alexandru Andrei"
__copyright__ = '''
    Copyright 2019,
    Udacity Full Stack Developer NanoDegree Project
'''
__version__ = "1.0.1"
__email__ = "andreony.alex@gmail.com"
__status__ = "Production"

# -- flask imports
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    url_for,
    send_file,
    flash,
    session as login_session,
    make_response
)
# -- ORM imports
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from models import (
    engine,
    Base,
    User,
    Category,
    CatalogItem
)

# python packages

import random
import string
import requests
import json
import httplib2
from datetime import (
    datetime,
    timedelta
)

# Oath2 imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

app = Flask(__name__)

# Connect to Database and create database session
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read()
)['web']['client_id']

APPLICATION_NAME = "Catalog Items Application"

# ---- DEV STAGING APP
APP_DEV_STATUS = False
ADMIN_USER_ID = 1  # --- or use 9999999999
ADMIN_PIC = 'static/img/admin.png'
# ---------------------

SECRET_KEY = ''.join(
    random.choice(
        string.ascii_uppercase
        + string.digits
    ) for x in xrange(32)
)


# -- user handling
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).\
        filter_by(email=login_session['email']).first()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).\
        filter_by(id=user_id).first()
    return user


def getUserID(email):
    try:
        user = session.query(User).\
            filter_by(email=email).first()
        return user.id
    except Exception:
        return None


def grabCategoryId(category_name):
    try:
        category = session.query(Category).\
            filter_by(name=category_name).first()
        return category.id
    except Exception:
        return None


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase
            + string.digits
        ) for x in xrange(32)
    )
    login_session['state'] = state
    return render_template('auth/login.html', STATE=state)


'''
  ::::::::: Google Plus Auth Mechanism
'''
@app.route('/signin_button.png', methods=['GET'])
def signin_button():
    """
        Returns the button image for sign-in.
    """
    return send_file(
        "templates/auth/g-signin_button.png",
        mimetype='image/gif'
    )


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state', '') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # -- store the google response to the credentials variable
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError as e:
        print(e)
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps(
                'Current user is already connected.'
            ),
            200
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info from the google API
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']  # - changed from data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # -- check if the user is stored to the db using email lookup
    user_id_from_db = getUserID(login_session['email'])
    if not user_id_from_db:
        username = login_session['username']
        picture = login_session['picture']
        email = login_session['email']
        # -- add to db
        session.add(User(name=username, email=email, picture=picture))
        session.commit()
        # -- get the newly created user_id
        user_id_from_db = getUserID(login_session['email'])
    # -- store user_id to session
    login_session['user_id'] = user_id_from_db
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; \
      height: 300px;border-radius: 150px;\
      -webkit-border-radius: 150px;\
      -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'], 'success')
    print "done!"
    return output
    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    state = login_session.get('state')
    if state is None:
        print ('Access Token is None', login_session)
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['state']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['state']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


'''
  ::::::::: Facebook Auth Mechanism
'''
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?\
    grant_type=fb_exchange_token&client_id=%s\
    &client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?\
    access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = "'https://graph.facebook.com/v2.8/me/picture?"
    url += "access_token=%s&redirect=0&height=200&width=200'" % token

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;'
    output += "border-radius: 150px; -webkit-border-radius: 150px;"
    output += '-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?\
    access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/profile')
def viewProfile():
    return render_template('profile.html')


# -- user logout
# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.", 'success')
        return redirect(url_for('showCatalog'))
    # -- account for dev status
    elif APP_DEV_STATUS:
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash("Admin User Logged Out", 'warning')
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in", 'warning')
        return redirect(url_for('showCatalog'))


# JSON APIs to view Catalog Information
@app.route('/catalog/category/<int:category_id>/json')
def categoryJSON(category_id):
    serializer = {}
    category = session.query(Category).filter_by(id=category_id).first()
    if not category:
        return {}, 404
    items = session.query(CatalogItem).filter_by(cat_id=category.id).all()
    category_json = category.serialize
    category_json['items'] = [i.serialize for i in items]
    return jsonify(Category=category_json)


@app.route('/catalog/items/<int:item_id>/json')
def catalogItemJSON(item_id):
    item = session.query(CatalogItem).filter_by(id=item_id).first()
    if item:
        return jsonify(Item=item.serialize)
    return {}, 404


@app.route('/catalog.json')
def catalogJSON():
    categories = session.query(Category).all()
    categories_json = [r.serialize for r in categories]
    for i in range(len(categories_json)):
        cat_id = categories_json[i]['id']
        items = session.query(CatalogItem).filter(
            CatalogItem.cat_id == cat_id
        ).all()
        items_json = [x.serialize for x in items]
        categories_json[i]['item'] = items_json
    return jsonify(Categories=categories_json)


@app.route('/admin')
def adminLogin():
    #  ##### ONLY FOR DEVELOPMENT #####
    if APP_DEV_STATUS:
        login_session['state'] = request.args.get('state', '')
        login_session['username'] = __author__
        login_session['email'] = __email__
        login_session['picture'] = ADMIN_PIC
        login_session['is_superuser'] = True
        flash("Welcome Admin User!", 'success')
        return redirect(url_for('showCatalog'))
    return('<h2>Not Found</h2>', 404)
    #  ################################


# Show catalog
@app.route('/')
@app.route('/catalog')
def showCatalog():
    today = datetime.now()
    categories = session.query(Category).order_by(asc(Category.name)) or None
    # --- grab recently added items -- last week
    items = session.query(CatalogItem).filter(
            CatalogItem.created_date >= today - timedelta(days=7)
    ).all()
    # if 'username' in login_session:
    return render_template('index.html', categories=categories, items=items)


# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    # -- reserved for admin || DEV Testing On
    if not APP_DEV_STATUS:
        return('<h2>Not Found</h2>', 404)
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        flash(
            'New Category %s Successfully Created' % newCategory.name,
            'success'
        )
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newCategory.html')


# list category items
@app.route('/catalog/<category_name>/')
@app.route('/catalog/<category_name>/Items/')
def showItems(category_name):
    this_category = session.query(Category).\
        filter_by(name=category_name).first()
    categories = session.query(Category).\
        order_by(asc(Category.name)).all()
    try:
        items = session.query(CatalogItem).\
            filter_by(cat_id=this_category.id).all()
    except Exception as e:
        print(e)
        items = []
    # creator = getUserInfo(category.user_id)
    return render_template(
      # 'publicItems.html',
      'Items.html',
      items=items,
      category=this_category,
      categories=categories
    )


# Create a new catalog item
@app.route('/catalog/Item/new/', methods=['GET', 'POST'])
def newCatalogItem():
    if 'username' not in login_session and not APP_DEV_STATUS:
        return redirect(url_for('showLogin'))
    else:
        user = session.query(User).\
            filter_by(name=login_session['username']).first()
    # -- check if app is in dev status
    if not user and APP_DEV_STATUS:
        user_id = ADMIN_USER_ID
    else:
        user_id = user.id
    categories = session.query(Category).all()
    # -- post request
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category_id = request.form['catalog-category']
        # ---validate form
        if title and description and category_id:
            # -- check if item already exists
            if session.query(CatalogItem).filter_by(title=title).first():
                flash(
                    '''Item %s already exists! Please chose a \
                    different title for your item''' % title, 'warning'
                )
                return render_template(
                    'newCatalogItem.html',
                    categories=categories
                )
            category = session.query(Category)\
                .filter_by(id=category_id).first()
            newItem = CatalogItem(
                title=title,
                description=description,
                cat_id=category.id,
                user_id=user_id
                )
            session.add(newItem)
            session.commit()
            flash(
             'New Menu %s Item Successfully Created' % (newItem.title),
             'success'
            )
            return redirect(
                url_for('showItems', category_name=category.name)
            )
    # -- get request
    else:
        return render_template('newCatalogItem.html', categories=categories)


# Edit a catalog item
@app.route(
    '/catalog/<category_name>/<item_title>/edit',
    methods=['GET', 'POST']
)
def editCatalogItem(category_name, item_title):
    # -- redirect unauth users
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    # -- get db objects
    editedItem = session.query(CatalogItem).\
        filter_by(title=item_title).\
        first()
    '''
        -- reuse query_set
    '''
    categories_qs = session.query(Category).order_by(asc(Category.name))
    # -- get category and category list from query set
    category = categories_qs.filter_by(name=category_name).first()
    categories = categories_qs.all()
    # -------------------
    # -- check if the user is the owner of the item
    if login_session['username'] != editedItem.item_user_name:
        return('<h2>Bad Request!</h2>', 400)
    # --
    if request.method == 'POST':
        if request.form['title']:
            editedItem.name = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Catalog Item Successfully Edited', 'success')
        return redirect(url_for('showItems', category_name=category.name))
    else:
        return render_template(
            'editCatalogItem.html',
            category_name=category.name,
            item_title=editedItem.title,
            item=editedItem,
            categories=categories
        )


# Delete a catalog item
@app.route('/catalog/<item_title>/delete', methods=['GET', 'POST'])
def deleteCatalogItem(item_title):
    # -- redirect unauth users
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    # -- get db objects
    deletedItem = session.query(CatalogItem).\
        filter_by(title=item_title).\
        first()
    # -- check if the user is the owner of the item
    if login_session['username'] != deletedItem.item_user_name:
        return('<h2>Bad Request!</h2>', 400)
    # -- gracefull exit
    if not deletedItem:
        return('<h2>Not Found!</h2>', 404)
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash('Menu Item Successfully Deleted', 'success')
        return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'deleteCatalogItem.html',
            item=deletedItem
        )


@app.route('/catalog/<category_name>/<item_title>/')
def detailViewCatalogItem(category_name, item_title):
    if 'username' not in login_session and not APP_DEV_STATUS:
        return redirect(url_for('showLogin'))
    category = session.query(Category).\
        filter_by(name=category_name).\
        first()
    item = session.query(CatalogItem).\
        filter_by(title=item_title).\
        first()
    return render_template(
        'item_detail_view.html',
        item=item,
        category=category
    )


if __name__ == '__main__':
    app.config['SECRET_KEY'] = ''.join(
        random.choice(
            string.ascii_uppercase
            + string.digits
        ) for x in xrange(32)
    )
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
