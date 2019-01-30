from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from camdatabase import Base, UserData, Brand, ModelName
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import random
import string
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Digital Camera world Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///camcatalog.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
# Render to login page


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# GConnect


@app.route('/gconnect', methods=['POST'])
def gconnect():
    ''' Validate state token'''
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials objects
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # Error in the access token info and ABORTED
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Access token is valid for this Application
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Access tokens are stored
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'
            ), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user information.
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    # data=json.loads(answer.txt)
    # User information and provider
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    # output += login_session['user_id']
    output += login_session['username']
    output += '!</h2>'
    output += '<img src=" '
    output += login_session['picture']
    output += ' " style = "width: 225px; height: 250px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


def createUser(login_session):
    newUser = UserData(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(UserData).filter_by(
                                            email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(UserData).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(UserData).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/logout')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    print(access_token)
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        response = redirect(url_for('showBrands'))
        flash('Successfully Logged Out')
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# JSON END API's
# returns all models of particular brand as
# JSON object and Model as JSON object.
# Same brandmodelsjson in Both Files(Brand and ModelName)


@app.route('/brand/<int:brand_id>/model/<int:model_id>/JSON')
def brandsModelsItemJSON(brand_id, model_id):
    session = DBSession()
    brand = session.query(Brand).filter_by(id=brand_id).all()
    model = session.query(ModelName).filter_by(id=model_id).all()
    session.close()
    return jsonify(brand=[i.serialize for i in brand],
                   model=[i.serialize for i in model])


@app.route('/brand/<int:brand_id>/JSON')
def BrandModelsJSON(brand_id):
    session = DBSession()
    brand = session.query(Brand).filter_by(id=brand_id).all()
    model = session.query(ModelName).filter_by(brand_id=brand_id).all()
    session.close()
    return jsonify(brand=[i.serialize for i in brand],
                   model=[i.serialize for i in model])


@app.route('/brand/JSON')
def BrandJSON():
    session = DBSession()
    brand = session.query(Brand)
    session.close()
    return jsonify(brand=[i.serialize for i in brand])


# To See All Brands and Users Created


@app.route('/')
def showBrands():
    session = DBSession()
    brands = session.query(Brand)
    return render_template(
        'showbrands.html', brands=brands,
        cur_user=login_session)


@app.route('/brand')
def showBrand():
    try:
        session = DBSession()
        brands = session.query(Brand).order_by(asc(Brand.name)).all()
        if not brands:
            # flash message
            flash("No Brands to show.")
        session.close()
        return render_template(
            'show_Brand.html',
            brands=brands,
            cur_user=login_session)
    except Exception as E:
        print(E)

# To Add New Brand
# localhost:5000/brand/new


@app.route('/brand/new', methods=['GET', 'POST'])
def newBrand():
    if 'username' in login_session:
        if request.method == 'POST':
            newBrd = Brand(
                name=request.form['name'],
                user_id=login_session['user_id'])
            session = DBSession()
            session.add(newBrd)
            session.commit()
            '''flash message'''
            flash(newBrd.name + "Brand successfully added.")
            session.close()
            return redirect('/')
        else:
            return render_template('NBrand.html', cur_user=login_session)
    else:
        # flash message
        flash("Login to Proceed !")
        return redirect('/login')

# To Edit Brand
# localhost:5000/brand/brand_id/edit


@app.route('/brand/<int:brand_id>/edit', methods=['GET', 'POST'])
def editBrand(brand_id):
    session = DBSession()
    editBrd = session.query(Brand).filter_by(id=brand_id).one()
    if 'username' in login_session:
        if login_session['user_id'] == editBrd.user_id:
            before = editBrd.name
            if request.method == 'POST':
                editBrd.name = request.form['name']
                session.add(editBrd)
                session.commit()
                # Print message
                flash(
                    before + " Brand successfully changed as " + editBrd.name)
                session.close()
                return redirect('/')
            else:
                return render_template(
                    'EBrand.html',
                    br=editBrd,
                    cur_user=login_session)
        else:
            # Print message
            flash("Permissions deniend !,U Do not Edit Brand")
            return redirect('/')
    else:
        # Print message
        flash("Login to Proceed !")
        return redirect('/login')


# To Delete Particular Brand
# localhost:5000/brand/brand_id/delete
@app.route('/brand/<int:brand_id>/delete', methods=['GET', 'POST'])
def deleteBrand(brand_id):
    session = DBSession()
    deleteBrd = session.query(Brand).filter_by(id=brand_id).one()
    if 'username' in login_session:
        if login_session['user_id'] == deleteBrd.user_id:
            deleteMoDU = session.query(ModelName).filter_by(
                                                           brand_id=brand_id
                                                           ).all()
            if request.method == 'POST':
                for i in deleteMoDU:
                    print("deleting ", i.id)
                    session.delete(i)
                    session.commit()
                session.delete(deleteBrd)
                session.commit()
                # Print message
                flash(deleteBrd.name + " Brand, successfully deleted.")
                session.close()
                return redirect('/')
            else:
                return render_template(
                    'DBrand.html',
                    br=deleteBrd,
                    cur_user=login_session)
        else:
            # flash message
            flash("Permissions deniend !,U Do not Delete Brand")
            return redirect('/')
    else:
        # flash message....
        flash("Login to Proceed !")
        return redirect('/login')


# To See All Models
# localhost:5000/brand/brand_id/model/
# localhost:5000/brand/brand_id/

@app.route('/brand/<int:brand_id>/model')
def showModel(brand_id):
        session = DBSession()
        brand = session.query(Brand).filter_by(id=brand_id).one()
        model = session.query(ModelName).filter_by(brand_id=brand.id)
        return render_template(
            'showModelsforuser.html', brand=brand,
            model=model, cur_user=login_session)
# Show models for users data


@app.route('/brand/<int:brand_id>/')
def showModels(brand_id):
    try:
        session = DBSession()
        brand = session.query(Brand).filter_by(id=brand_id).one()

        if not model:
            # flash message
            flash("No Models to show.")
        session.close()
        return render_template(
            'showModelsforuser.html',
            brand=brand,
            model=model,
            cur_user=login_session)
    except Exception as E:
        return "<h4>I am coming to here</h4>"


# Models data for New Models
@app.route('/brand/<int:brand_id>/model/new', methods=['GET', 'POST'])
def newModel(brand_id):
    if 'username' in login_session:
        session = DBSession()
        brand = session.query(Brand).filter_by(id=brand_id).one()
        if login_session['user_id'] == brand.user_id:
            if request.method == 'POST':
                brand = session.query(Brand).filter_by(id=brand_id).one()
                newMo = ModelName(
                    brand_id=brand.id,
                    user_id=login_session['user_id'],
                    modelnumber=request.form['modelnumber'],
                    colors=request.form['colors'],
                    price=request.form['price'],
                    description=request.form['des'])
                session.add(newMo)
                # To store data in Permanently
                session.commit()
                # flash message
                flash(" Model, successfully added to %s" % brand.name)
                session.close()
                return redirect(url_for('showModel', brand_id=brand_id))
            else:
                return render_template(
                    'NModel.html',
                    brand=brand,
                    cur_user=login_session)
        else:
            # flash message
            flash("Permissions deniend !,U Do not Create Model")
            return redirect('/')
    else:
        # flash message
        flash("Login to Proceed !")
        return redirect('/login')


# To Edit Model
# localhost:5000/brand/brand_id/model/model_id/edit


@app.route(
    '/brand/<int:brand_id>/model/<int:model_id>/edit',
    methods=['GET', 'POST'])
def editModel(brand_id, model_id):
    if 'username' in login_session:
        session = DBSession()
        brand = session.query(Brand).filter_by(id=brand_id).one()
        editMod = session.query(ModelName).filter_by(id=model_id).one()
        if login_session['user_id'] == brand.user_id:
            if request.method == 'POST':
                editMod.modelnumber = request.form['modelnumber']
                editMod.colors = request.form['colors']
                editMod.brand_id = brand_id
                editMod.price = request.form['price']
                editMod.description = request.form['description']
                session.add(editMod)
                session.commit()
                # flash message
                flash("Successfully Changes have done!")
                session.close()
                return redirect(url_for('showModel', brand_id=brand_id))
            else:
                return render_template(
                    'EModel.html', brand_id=brand_id,
                    model_id=model_id, edit=editMod,
                    cur_user=login_session)
        else:
            # flash message
            flash("Permissions deniend !,U Do not Edit Model")
            return redirect('/')
    else:
        # flash message
        flash("Login to Proceed !")
        return redirect('/login')


# To Delete Model
# localhost:5000/brand/brand_id/model/model_id/delete

@app.route(
    '/brand/<int:brand_id>/model/<int:model_id>/delete',
    methods=['POST', 'GET'])
def deleteModel(brand_id, model_id):
    if 'username' in login_session:
        session = DBSession()
        deleteMod = session.query(ModelName).filter_by(id=model_id).one()
        # print(deleteMod.name)
        if login_session['user_id'] == deleteMod.user_id:
            if request.method == 'POST':
                session.delete(deleteMod)
                session.commit()
                flash(" Model Successfully deleted.")
                return redirect(url_for('showModel', brand_id=brand_id))

            else:
                return render_template(
                    'DModel.html', brand_id=brand_id,
                    model=deleteMod, cur_user=login_session)
                session.close()
        else:
            # flash message
            flash("Permissions deniend !,U Do not Delete Model")
            return redirect('/')
    else:
        # flash message
        flash("Login to Proceed !")
        return redirect('/login')
# default constructor
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5001)
