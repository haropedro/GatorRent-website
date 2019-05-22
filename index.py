#!/usr/bin/env python3
from flask import Flask
import mysql.connector
from flask import url_for, redirect, Flask, request, render_template, flash, session, Markup, make_response
import json
from settings import *
import random, string
from flask_bcrypt import Bcrypt
from db_module import *

app = Flask(__name__)
app.secret_key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    # gets the lastest inserted listings on `listing_table`
    # only approved listings
    recentListings = get_data('SELECT * FROM `listing_table` WHERE `isApproved` = 1 ORDER BY `listing_id` DESC LIMIT 3')
    return render_template('home.html', latest=recentListings)

@app.route('/users')
def user_dump() -> str:
    return json.dumps({'users': get_users()})

@app.route('/about')
def about():
    return render_template('about.html')

# Base page
@app.route('/results', methods=['GET', 'POST'])
def results():
    allresults = get_data('SELECT * FROM gatorrent_db.listing_table')
    length = len(allresults)
    if length == 1:
        resultTag = "result"
    else:
        resultTag = "results"
    message = "Showing all {} {}.".format(length, resultTag)
    if request.method == "POST":
        filter = request.form.get('filter', None)

        if filter is None:
            varData = {}
            persistanceList = []

            # variables on the filter form
            vars1 = ['minprice', 'maxprice', 'city', 'postcode', 'mindistance', 'maxdistance']
            vars2 = ['room', 'apartment', 'house', 'shared', 'pets']

            # collect data from form fields
            for v in vars1:
                varData[v] = request.form[v]
                persistanceList.append(varData[v])

            # for fields that uses checkboxes
            for v in vars2:
                varData[v] = request.form.get(v, None)
                if varData[v] == 'on':
                    varData[v] = 1
                persistanceList.append(varData[v])

            # make db connection
            connection = mysql.connector.connect(**database)
            cursor = connection.cursor()

            # price range query
            priceRangeQ = ''
            if not varData['minprice'] and varData['maxprice']:
                priceRangeQ= 'price BETWEEN 0 AND ' + varData['maxprice']

            if varData['minprice'] and not varData['maxprice']:
                priceRangeQ = 'price BETWEEN ' + varData['minprice'] + ' AND ' + '1000000'

            if varData['minprice'] and varData['maxprice']:
                priceRangeQ = 'price BETWEEN ' + varData['minprice'] + ' AND ' + varData['maxprice']

            # location query
            locationQ = ''
            if varData['postcode'] and varData['city']:
                locationQ = "postcode LIKE '\%" + varData['postcode'] + "\%' AND city LIKE '\%" + varData['city'] + "\%'"

            if varData['city'] and not varData['postcode']:
                locationQ = "city LIKE '\%" + varData['city'] + "\%'"

            if varData['postcode'] and not varData['city']:
                locationQ = "postcode LIKE '%" + varData['postcode'] + "%'"

            # miles from campus query
            distanceQ = ''
            if not varData['mindistance'] and varData['maxdistance']:
                distanceQ = 'dist_from_campus BETWEEN 0 AND ' + varData['maxdistance']

            if varData['mindistance'] and not varData['maxdistance']:
                distanceQ = 'dist_from_campus BETWEEN ' + varData['mindistance'] + ' AND ' + '1000000000'

            if varData['mindistance'] and varData['maxdistance']:
                distanceQ = 'dist_from_campus BETWEEN ' + varData['mindistance'] + ' AND ' + varData['maxdistance']

            # property query
            roomQ = ''
            if varData['room']:
                roomQ = 'rent_type_id = 2'

            apartmentQ = ''
            if varData['apartment']:
                apartmentQ = 'rent_type_id = 1'

            houseQ = ''
            if varData['house']:
                houseQ = 'rent_type_id = 3'

            # living preferences query
            shareQ = ''
            if varData['shared']:
                shareQ = 'is_shared = 1'

            petsQ = ''
            if varData['pets']:
                petsQ = 'is_pet = 1'

            # to keep track on when to add "AND"
            count = 0

            # to query db
            filterQuery = 'SELECT * FROM gatorrent_db.listing_table'

            # db query string contruction
            for s in [priceRangeQ, locationQ, distanceQ, roomQ, apartmentQ, houseQ, shareQ, petsQ]:

                if s != '':
                    if count == 0:
                        filterQuery += ' WHERE ' + s
                        count += 1
                    else:
                        filterQuery += ' AND ' + s

            cursor.execute(filterQuery)
            return render_template('results.html', listings=cursor.fetchall(), persistence=persistanceList)

        else:
            search = request.form['search'].lower()
            if search == "room" or search == "apartment" or search == "house":
                tempSearch = search
                if search == "room": filter = "2"
                elif search == "apartment": filter = "1"
                elif search == "house": filter = "3"
                search = ""
            else:
                tempSearch = ""
            if filter != "All properties":
                filterToString = ""
                if filter == "2": filterToString = "rooms"
                elif filter == "1": filterToString = "apartments"
                elif filter == "3": filterToString = "houses"
                searchresults = get_data("SELECT * FROM gatorrent_db.listing_table WHERE CONCAT_WS('', street, city, state, country, postcode) LIKE '%{}%' AND rent_type_id = {}".format(search, filter))
                length = len(searchresults)
                if length == 1:
                    resultTag = "listing"
                else:
                    resultTag = "listings"
                if search == "":
                    message = "Showing {} {} in {}".format(length, resultTag, filterToString)
                    search == tempSearch
                elif search == "house" or search == "room" or search == "apartment":
                    message = "test"
                else:
                    message = "Showing {} {} for '{}' in {}".format(length, resultTag, search, filterToString)
                if tempSearch != "":
                    search = tempSearch
                return render_template('results.html', listings=searchresults, filter=filter, search=search, message=message, persistence=None)
            else:

                searchresults = get_data("SELECT * FROM gatorrent_db.listing_table WHERE CONCAT_WS('', street, city, state, country, postcode) LIKE '%{}%'".format(search))

                length = len(searchresults)
                if length == 1:
                    resultTag = "result"
                else:
                    resultTag = "results"
                if search == "":
                    message = "Showing all {} {}.".format(length, resultTag)
                else:
                    message = "Showing {} {} for '{}'".format(length, resultTag, search)
                if tempSearch != "":
                    search = tempSearch
                return render_template('results.html', listings=searchresults, message=message, search=search, persistence=None)
    return render_template('results.html', listings=allresults, message=message, persistence=None)

# Auth pages
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # removes leading, trailing and all whitespace in between
        username = "".join(str(username).split())

        success, pw_hash, loginid, error = loginCheck(username, password)

        if not success:
            flash(error)
            persistenceList = [username, password]
            return render_template('/login.html', persistence=persistenceList)
        else:
            # pw_hash is a cursor type
            if bcrypt.check_password_hash(pw_hash, str(password)):
                session['username'] = username
                session['loginid'] = loginid

                if request.cookies.get('rent-type'):
                    return redirect(url_for('post'))

                flash('Login successful!')
                return redirect(url_for('user_messages'))
            else:
                flash('Invalid password.')
                persistenceList = [username]
            return render_template('/login.html', persistence=persistenceList)

    return render_template('/login.html', persistence=None)

#confirmation page after a message is successfully sent
@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form['username']

        # removes leading, trailing and all whitespace in between
        username = "".join(str(username).split())

        password = request.form['password']
        email = request.form['email']
        agree = request.form.get('agree', None)

        persistenceList = [password,email,agree]

        # if username is not unique
        if not isUsernameUnique(username):
            flash('Username ' + "'%s'" % username + ' already taken!')
            return render_template('register.html', persistence=persistenceList)
        else:
            # hash password
            password = request.form['password']
            pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

            success, sqlerror = insertDB('user_table', ('user_name', 'password', 'email', 'user_type'), (username, pw_hash, email, 1))

            if not success:
                flash('ERROR: ' + sqlerror )
            else:
                session['username'] = username
                session['loginid'] = get_userID(username)

                if request.cookies.get('rent-type'):
                    return redirect(url_for('post'))

                flash('Welcome ' + username + ' to your Gatorrent dashboard!')
                return render_template('/user_messages.html')

    return render_template('register.html', persistence=None)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
        session.pop('loginid', None) #user's id
        flash('Successfully Logged out!')
        return render_template('home.html')
    else:
        flash(Markup('You are not logged in, please click <a href="/login" class="alert-link">here</a> to login 🖥️'))
        return render_template('error.html')

# allows lazy registration:
# unregistered user prompted to register/login after form submission
@app.route('/post', methods=['GET', 'POST'])
def post():

    if request.method == 'POST':

        varData = {}
        varlist = ['rent-type', 'size', 'price', 'address', 'city', 'state', 'pets', 'sharedroom', 'description', 'postcode', 'title']

        for v in varlist:
            # retrive by name attribute
            varData[v] = request.form[v]

        thumbnail = request.form.get('thumbnail', None)

        # images are not saved as cookies
        images = request.files.getlist('images')

        if 'username' in session and thumbnail:

            userID = get_userID(session['username'])

            success, sqlerror = insertDB('listing_table',
                                ('user_id', 'rent_type_id', 'price', 'is_pet', 'is_shared', 'title', 'street', 'city', 'state', 'postcode', 'description'),
                                (userID, varData['rent-type'], varData['price'], varData['pets'], varData['sharedroom'], varData['title'],
                                varData['address'], varData['city'], varData['state'], varData['postcode'], varData['description']
                                ))

            # save images in folder on server
            listingID = get_listingID(userID)
            success, sqlerror = uploadImages(images, userID, listingID, thumbnail)

            if not success:
                flash('Error: ' + sqlerror )
            else:

                flash(Markup("""<i class="far fa-check-circle"></i> Your listing is submitted for approval. It may take up to 24hrs."""))
                # show listing on the dashboard
                # redirect to user dashboard
                resp = redirect(url_for('user_listings'))

                # delete post form cookies
                if request.cookies.get('rent-type'):
                    for x in range(len(varlist)):
                        resp.set_cookie(varlist[x], varData[varlist[x]], max_age=0)

                return resp
        else:
            # if thumbnail == None
            if not thumbnail:
                flash(Markup("""<i class="far fa-image"></i> Thumbnail not selected. Please upload images and select a thumbnail."""))
                resp = redirect(url_for('post'))

            else:
                flash(Markup("""<center> <i class="fas fa-door-open"></i> <br/> <a href="/register" class="alert-link">Register</a> or <a href="/login" class="alert-link">Login</a> to post your listing <i class="far fa-edit"></i></center>"""))
                resp = make_response(render_template('error.html'))

            for x in range(len(varlist)):
                resp.set_cookie(varlist[x], varData[varlist[x]])

            return resp

    return render_template('/post.html')

#@app.route('/listing/<int:sender_id>/<int:listing_id>', methods=['GET', 'POST']')
@app.route('/<user_id>/listing-<int:listing_id>/')
def listing(user_id, listing_id):
    listingData = get_data('SELECT * FROM `listing_table` WHERE `listing_id` = 10')
    username = get_userName(user_id)
    paths = get_imagePaths(listing_id)
    return render_template('listing.html', listing=listingData, lister=username, path=paths)

#app route for the message button located on the /results page.
#required for user to be logged in
@app.route('/message/<int:sender_id>/<int:listing_id>', methods=['GET', 'POST'])
def message(sender_id, listing_id):
    if 'username' in session:
        if request.method =='POST':
            body = request.form['comment']
            connection = mysql.connector.connect(**database)
            cursor = connection.cursor()

            loginuserid = session["loginid"]
            #session['listingid'] = 'listing_id'

            senderid = sender_id
            if loginuserid == senderid:
                flash(Markup("""<center> Error. <i class="fas fa-exclamation-triangle"></i> You can't send a message to yourself. <br/> Click <a href="/results" class="alert-link">Here </a> to return back to the results page </i></center>"""))


                return render_template('error.html')
            else:
                insertDB('message_table', ('body', 'sender_user_id', 'reciever_user_id', 'listing_id'), (body, loginuserid, senderid, listing_id))

                connection.commit()
                cursor.close()
                connection.close()
                return redirect(url_for('confirmation'))

    else:
        flash(Markup("""<center> Opps <i class="fas fa-exclamation-triangle"></i> <br/> <a href="/login" class="alert-link">Login</a> to see your messages <i class="far fa-envelope"></i></center>"""))
        return render_template('error.html')

    return render_template('/message.html')

#app route for the message button on the more info page
#@app.route('/more_info_message/<int:sender_id>/<int:listing_id>', methods=['GET', 'POST'])
@app.route('/more_info_message', methods=['GET', 'POST'])

def more_info_message():
    if 'username' in session:
        if request.method =='POST':
            body = request.form['comment']
            connection = mysql.connector.connect(**database)
            cursor = connection.cursor()
            loginuserid = session["loginid"]
            #senderid = sender_id
            #listingid = session.get('listing_id')

            #insertDB('message_table', ('body', 'sender_user_id', 'reciever_user_id', 'listing_id'), (body, loginuserid, senderid, listing_id))
            insertDB('message_table', ('body', 'sender_user_id', 'reciever_user_id', 'listing_id'), (body, loginuserid, '4', '10'))

            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('confirmation'))

    else:
        flash(Markup('You are not logged in, please click <a href="/login" class="alert-link">here</a> to login 🖥️'))
        return render_template('error.html')
    return render_template('/more_info_message.html')

@app.route('/my-messages')
def user_messages():
    if 'username' in session:
        userID = get_userID(session['username'])
        userMessage = get_data('SELECT `message_id`, `body`, `sender_user_id`, `reciever_user_id`, `listing_id`, `timestamp` FROM `message_table` WHERE `reciever_user_id` = {}'.format(userID))
        senderID = get_data('SELECT `sender_user_id` from `message_table` WHERE `reciever_user_id` = {}'.format(userID))

        try:
            senderID=senderID[0]
            senderIDName=get_userName(senderID)

        except IndexError:
            senderIDName = 0
            return render_template('/user_messages.html')

        return render_template('/user_messages.html', results=userMessage,senderIDName = senderIDName)

    else:
        flash(Markup("""<center> Opps <i class="fas fa-exclamation-triangle"></i> <br/> <a href="/login" class="alert-link">Login</a> to see your messages <i class="far fa-envelope"></i></center>"""))
        return render_template('error.html')

    return render_template('/user_messages.html')

#allows a guest user to contact the admin team, provide any type of feedback, express concerns, etc.
@app.route('/contact-us', methods = ['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        body = request.form['comment']
        connection = mysql.connector.connect(**database)
        cursor = connection.cursor()
        insertDB('message_admin_table', ('body_admin', 'user_id'), (body, '7'))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('confirmation'))
    return render_template('contact_us.html')

@app.route('/my-listings')
def user_listings():
    if 'username' in session:

        userID = get_userID(session['username'])
        userListings = get_data('SELECT * FROM `listing_table` WHERE `user_id` = {}'.format(userID))

        return render_template('/user_listings.html', listings=userListings)
    else:
        flash(Markup("""<center> Opps <i class="fas fa-exclamation-triangle"></i> <br/> <a href="/login" class="alert-link">Login</a> to see your listings <i class="fas fa-clipboard-list"></i>"""))
        return render_template('error.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
