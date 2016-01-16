from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Game, Genre, Console, User, Inventory
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Game Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///gameCatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
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

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Game Information
@app.route('/games/JSON')
def gamesJSON():
    games = session.query(Game).all()
    for g in games:
        print g.name
    return jsonify(games=[g.serialize for g in games])


# Show all Games
@app.route('/')
@app.route('/games/')
def showGames():
    games = session.query(Game).order_by(asc(Game.name))
    if 'username' not in login_session:
        return render_template('showGames.html', games=games)
    else:
        return render_template('showGames.html', games=games)

# Show Game Details page


@app.route('/games/<int:game_id>/')
@app.route('/games/<int:game_id>/details/')
def showGameDetails(game_id):
    game = session.query(Game).filter_by(id=game_id).one()
    inventory = session.query(Inventory).filter_by(game_id=game_id).all()
    creator = getUserInfo(game.user_id)
    if 'username' not in login_session or creator.id != login_session[
            'user_id']:
        return render_template(
            'PublicshowGameDetails.html',
            game_id=game.id,
            game=game,
            inventory=inventory,
            creator=creator)
    else:
        return render_template(
            'showGameDetails.html',
            game_id=game.id,
            game=game,
            inventory=inventory,
            creator=creator)


# Show Consoles page
@app.route('/games/consoles/', methods=['GET', 'POST'])
def showConsoles():
    consoles = session.query(Console).all()
    genres = session.query(Genre).all()
    if request.method == 'POST':
        con = request.form['console']
        inventory = session.query(Inventory).filter_by(console=con).all()
        return render_template(
            'showConsoles.html',
            consoleList=consoles,
            genreList=genres,
            gameConsoles=inventory)
    else:
        return render_template(
            'showConsoles.html',
            consoleList=consoles,
            genreList=genres)

# Show Genres page


@app.route('/games/genres/', methods=['GET', 'POST'])
def showGenres():
    consoles = session.query(Console).all()
    genres = session.query(Genre).all()
    if request.method == 'POST':
        gen = request.form['genre']
        inventory = session.query(Inventory).filter_by(genre=gen).all()
        return render_template(
            'showGenres.html',
            consoleList=consoles,
            genreList=genres,
            gameGenres=inventory)
    else:
        return render_template(
            'showGenres.html',
            consoleList=consoles,
            genreList=genres)

# show Age Rating
@app.route('/games/ageRating/', methods=['GET', 'POST'])
def showageRating():
    #games = session.query(Game).all()
    if request.method == 'POST':
        age = request.form['ageRating']
        gameAge = session.query(Game).filter_by(ageRating=age).all()
        return render_template(
            'showageRating.html',
            gameAges=gameAge)
    else:
        return render_template(
            'showageRating.html')


# Create a new Game
@app.route('/games/new/', methods=['GET', 'POST'])
def newGame():
    if 'username' not in login_session:
        return redirect('/login')
    consoles = session.query(Console).all()
    genres = session.query(Genre).all()

    if request.method == 'POST':
        newGame = Game(
            name=request.form['name'],
            user_id=login_session['user_id'],
            description=request.form['description'],
            ageRating=request.form['ageRating'],
            price=request.form['price'],
            image=request.form['image']
        )

        session.add(newGame)
        flash('New Game %s Successfully Created' % newGame.name)
        session.commit()
        gameObj = session.query(Game).order_by(Game.id.desc()).first()

        multiselect = request.form.getlist('console')

        for x in multiselect:
            newInventory = Inventory(
                name=request.form['name'],
                game_id=gameObj.id,
                console=x,
                genre=request.form['genre'],
                user_id=login_session['user_id']

            )
            session.add(newInventory)
            session.commit()

        return redirect(url_for('showGames'))
    else:
        return render_template(
            'newGame.html',
            consoleList=consoles,
            genreList=genres)


# Create a new Console
@app.route('/games/newConsole/', methods=['GET', 'POST'])
def newConsole():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newConsole = Console(
            name=request.form['name'],
        )
        if request.form['name'] != '':
            session.add(newConsole)
            flash('New Console %s Successfully Created' % newConsole.name)
            session.commit()
        return redirect(url_for('showGames'))
    else:
        return render_template('newConsole.html')

# Create a new Genre


@app.route('/games/newGenre/', methods=['GET', 'POST'])
def newGenre():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newGenre = Genre(
            name=request.form['name'],
        )
        if request.form['name'] != '':
            session.add(newGenre)
            flash('New Genre %s Successfully Created' % newGenre.name)
            session.commit()
        return redirect(url_for('showGames'))
    else:
        return render_template('newGenre.html')


# Edit a Game
@app.route('/games/<int:game_id>/edit/', methods=['GET', 'POST'])
def editGame(game_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedGame = session.query(Game).filter_by(id=game_id).one()
    consoles = session.query(Console).all()
    genres = session.query(Genre).all()
    games = session.query(Game).order_by(asc(Game.name))
    if editedGame.user_id != login_session['user_id']:
        flash('You are not authorized to Delete %s' % editedGame.name)
        return render_template('showGames.html', games=games)
    if request.method == 'POST':
        if request.form['name']:
            editedGame.name = request.form['name']
            user_id = login_session['user_id']
        if request.form['description']:
            editedGame.description = request.form['description']
        if request.form['price']:
            editedGame.price = request.form['price']
        if request.form['ageRating']:
            editedGame.ageRating = request.form['ageRating']

        session.add(editedGame)
        session.commit()

        flash('Game Successfully Edited %s' % editedGame.name)
        return redirect(
            url_for(
                'showGameDetails',
                game_id=editedGame.id,
                game=editedGame))
    else:
        return render_template(
            'editGame.html',
            game=editedGame,
            consoleList=consoles,
            genreList=genres)


# Delete a Game
@app.route('/games/<int:game_id>/delete/', methods=['GET', 'POST'])
def deleteGame(game_id):
    if 'username' not in login_session:
        return redirect('/login')
    gameToDelete = session.query(Game).filter_by(id=game_id).one()
    inventoryToDelete = session.query(
        Inventory).filter_by(game_id=game_id).all()
    games = session.query(Game).order_by(asc(Game.name))
    if gameToDelete.user_id != login_session['user_id']:
        flash('You are not authorized to Delete %s' % gameToDelete.name)
        return render_template('showGames.html', games=games)
    if request.method == 'POST':
        session.delete(gameToDelete)
        flash('%s Successfully Deleted' % gameToDelete.name)
        session.commit()
        for d in inventoryToDelete:
            session.delete(d)
        session.commit()
        return redirect(url_for('showGames', game_id=game_id))
    else:
        return render_template('deleteGame.html', game=gameToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showGames'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showGames'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = False
    app.run(host='0.0.0.0', port=8000)
