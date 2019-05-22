from settings import *
import mysql.connector
from typing import List, Dict
from werkzeug.utils import secure_filename
from PIL import Image

SITE_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'
#authorizes communication between our application backend and the reCaptcha server
#allows verification of user response
SITE_SECRET = '6LfSCaMUAAAAAKIYOj8dNZDm68ww5CAcKYw46_c8'

# get all user_table data
def get_users() -> List[Dict]:
    connection = mysql.connector.connect(**database)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM gatorrent_db.user_table')
    rv = cursor.fetchall()
    payload = []
    for r in rv:
        results = {'id': r[0], 'username': r[1], 'email': r[3], 'user-type': r[4] }
        payload.append(results)
        results = {}
    cursor.close()
    connection.close()

    return payload

# get all data based on query
def get_data(query):
    connection = mysql.connector.connect(**database)
    cursor = connection.cursor()
    # Perform query
    cursor.execute(query)
    result = cursor.fetchall()
    # Close and return
    cursor.close()
    connection.close()
    return result
    
# gets the username when provided with the userID
def get_userName(senderIDName):
    connection = mysql.connector.connect(**database)
    cursor = connection.cursor()
    query = "SELECT `user_name` FROM `user_table` WHERE `user_id` = %s" % senderIDName

    cursor.execute(query)
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result
# return user_id from user_table where username matches parameter
def get_userID(username):
    connection = mysql.connector.connect(**database)
    cursor = connection.cursor()
    query = "SELECT `user_id` FROM `user_table` WHERE `user_name` = " + "'%s'" % username

    cursor.execute(query)
    result = cursor.fetchone()

    cursor.close()
    connection.close()
    # tuple
    return result[0]

# return (latest) listing_id from listing_table where user_id matches parameter
def get_listingID(userID):
    connection = mysql.connector.connect(**database)
    cursor = connection.cursor()
    query = "SELECT `listing_id` FROM `listing_table` WHERE `user_id` = %d ORDER BY `listing_id` DESC" % userID

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    connection.close()
    # list of tuples
    return result[0][0]


# returns true if no row entries contain the param username
def isUsernameUnique(username):
    query = "SELECT * FROM gatorrent_db.user_table WHERE user_name = " + "'%s'" % username
    connection = mysql.connector.connect(**database)
    cursor = connection.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        # there is a row that contains the username, hence not unique
        cursor.close()
        return False

    cursor.close()
    return True

# retrieves all messages that were sent to the user that is currently logged in
def getAllMessages(loginuserid, results):
    connection = mysql.connector.connect(**database)
    cursor = connection.cursor()
    try:
        sql = 'SELECT * FROM gatorrent_db.message_table WHERE reciever_user_id = '+ "'%i'" % loginuserid
        cursor.execute(sql)
        print("Messages:")
        results = cursor.fetchall()
        print(results)
        return results
        #for r in results:
        #    print(r)
    except mysql.connector.Error as err:
        error = str(err)
        return False, error + " sql statement: " + sql
    finally:
        connection.commit()
        cursor.close()
        connection.close()
    return results

# adds an entry to a table in gatorrent_db
# columns and values as tuples
def insertDB(tablename, columns, values):

    connection = mysql.connector.connect(**database)
    cursor = connection.cursor()

    success, error = checkTableExists(connection, tablename)
    if not success:
        return False, error

    try:
        col = '(' + ', '.join(columns) + ')'
        val = '(' + ', '.join( '"' + str(v) + '"' for v in values) + ')'

        sql = 'INSERT INTO ' + tablename + ' ' + col+ ' VALUES ' + val
        cursor.execute(sql)
        connection.commit()

    except mysql.connector.Error as err:
        error = str(err)
        return False, error + " sql statement: " + sql

    finally:
        cursor.close()

    return True, None

# update an entry on a table
# columns and values as tuples
# whereClause as SQL logic
def updateDB(tablename, columns, values, whereClause):

    connection = mysql.connector.connect(**database)
    cursor = connection.cursor()

    success, error = checkTableExists(connection, tablename)
    if not success:
        return False, error

    try:
        sql = 'UPDATE ' + tablename + ' SET '

        for i in range(len(columns)):
            sql += columns[i] + ' = ' + "'" + str(values[i]) + "'"
            if i < len(columns) - 1:
                sql += ', '

        sql += " WHERE " + str(whereClause) + ";"

        cursor.execute(sql)
        connection.commit()

    except mysql.connector.Error as err:
        error = str(err)
        return False, error + " sql statement: " + sql

    finally:
        cursor.close()

    return True, None


# check if a table exists
# returns false if it does not exist
# do not close cursor here: cursor should be closed by calling function ( the caller e.g. insertDB() )
def checkTableExists(connection, tablename):
    cursor = connection.cursor()

    try:
        cursor.execute("""SELECT COUNT(*) FROM information_schema.tables WHERE TABLE_NAME = '{0}' """.format(tablename))

    # return the first row of the result
        if cursor.fetchone()[0] == 1:
            return True, None

    except mysql.connector.Error as e:
        error = str(e)
        pass

    return False, error

# Checks the requirements to login
# returns true if all requirements met
def loginCheck(username, pw_hash):

    # username must exist
    if not isUsernameUnique(username):

        try:
            connection = mysql.connector.connect(**database)
            cursor = connection.cursor()
            cursor.execute("""SELECT `password`, `user_id` FROM `user_table` WHERE `user_name` = '{0}' """.format(username))
            returneduser = cursor.fetchone()
            loginpassword = returneduser[0]
            loginid = returneduser[1]

            return True, loginpassword, loginid, "Returned username's password hash."

        except mysql.connector.Error as e:
            error = str(e)

        finally:
            cursor.close()

    else:
        return False, None, None, 'Username does not exist!'

# return (latest) image_id from image_table where image_path matches parameter
def get_ImageID(path):
    connection = mysql.connector.connect(**database)
    cursor = connection.cursor()
    query = "SELECT `image_id` FROM `image_table` WHERE `image_path` = '%s' ORDER BY `image_id` DESC" % path

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    connection.close()
    # list of tuples
    return result[0][0]

# saves uploaded image files to /web/static
# format e.g: web/static/gallery/user-{user_id}/listing-{listing_id}/some_image.png
#
# inserts path to image folder in `image_table`
# inserts thumbnail path in `listing_table`
def uploadImages(images, userID, listingID, thumbnail):

    # size of thumbnail
    size = (512,512)

    thumbDIR = '/web/static/gallery' + '/user-' + str(userID) + '/listing-'+ str(listingID) + '/thumbnail/'
    imgDIR = '/web/static/gallery' + '/user-' + str(userID) + '/listing-'+ str(listingID)

    if not os.path.exists(thumbDIR):
        os.makedirs(thumbDIR)

    for img in images:
        if img.filename == thumbnail:
            m = Image.open(img)
            m.thumbnail(size, Image.ANTIALIAS)
            m.save( thumbDIR + secure_filename(img.filename.replace(" ", "")))

        img.save( imgDIR + '/' + secure_filename(img.filename.replace(" ", "")))

    thumbnailPath = 'static/gallery' + '/user-' + str(userID) + '/listing-'+ str(listingID) + '/thumbnail/' + str(thumbnail).replace(" ", "")

    success, sqlerror = insertDB('image_table', ('image_path',), (imgDIR,))
    imageID = get_ImageID(imgDIR)

    success, sqlerror = updateDB('listing_table', ('thumbnail_path',), (thumbnailPath,), 'listing_id = {}'.format(listingID))
    success, sqlerror = updateDB('listing_table', ('image_id',), (imageID,), 'listing_id = {}'.format(listingID))

    return success, sqlerror

# returns the paths to images of a listing
def get_imagePaths(listingID):
    paths = []
    imageID = get_data('SELECT `image_id` FROM `listing_table` WHERE `listing_id` = {}'.format(listingID))[0][0]
    rootPath = get_data('SELECT `image_path` FROM `image_table` WHERE `image_id` = {}'.format(imageID))[0][0]

    relativePath = rootPath.replace('/web/static/','')

    for root, dirs, files in os.walk(rootPath):
        for file in files:
            paths.append(str(os.path.join(relativePath, file)))

    return paths
