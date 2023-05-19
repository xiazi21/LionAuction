import sqlite3 as sql
import hashlib
import pandas as pd
import paymentHelp

userBool = 0  # find whether the user table have been created, refresh every new run
bidderBool = 0 # find whether the bidder table have been created, refresh every new run
helpDeskBool = 0 # find whether the helpDesk table have been created, refresh every new run
sellerBool = 0 # find whether the seller table have been created, refresh every new run
addrBool = 0


def createAddr():
    global addrBool
    if addrBool != 1:
        connection = sql.connect('database.db')
        connection.execute('CREATE TABLE IF NOT EXISTS zipcode('
                           'zipcode TEXT PRIMARY KEY NOT NULL, city TEXT, state INTEGER);')
        contents = pd.read_csv('Zipcode_Info.csv', engine='python')
        for row in contents.iterrows():
            connection.execute('INSERT OR IGNORE INTO zipcode (zipcode,city,state) VALUES(?, ?, ?)',
                               (row[1].zipcode, row[1].city, row[1].state))

        connection.execute('CREATE TABLE IF NOT EXISTS address('
                           'address_id TEXT PRIMARY KEY NOT NULL, '
                           'zipcode TEXT, '
                           'street_num INTEGER, '
                           'street_name TEXT,'
                           'FOREIGN KEY (zipcode) '
                           ' REFERENCES zipcode (zipcode)'
                           ');')
        contents = pd.read_csv('Address.csv', engine='python')
        for row in contents.iterrows():
            connection.execute('INSERT OR IGNORE INTO address (address_id,zipcode,street_num,street_name) VALUES(?, ?, ?, ?)',
                               (row[1].address_id, row[1].zipcode, row[1].street_num, row[1].street_name))
        connection.commit()  # submit change in database


def createUser():
    global userBool
    if userBool != 1:
        connection = sql.connect('database.db')
        connection.execute('CREATE TABLE IF NOT EXISTS users(userId TEXT PRIMARY KEY NOT NULL, password TEXT );')
        contents = pd.read_csv('Users.csv', engine='python')
        for row in contents.iterrows():
            connection.execute('INSERT OR IGNORE INTO users (userId,password) VALUES(?, ?)',
                               (row[1].email, str((hashlib.sha256(row[1].password.encode())).hexdigest())))
        connection.commit()  # submit change in database
        userBool = 1


def createBidder():
    global bidderBool
    if bidderBool!=1:
        connection = sql.connect('database.db')
        connection.execute('CREATE TABLE IF NOT EXISTS bidders'
                           '(userId TEXT PRIMARY KEY NOT NULL, '
                           'first_name TEXT,'
                           'last_name TEXT,'
                           'gender TEXT,'
                           'age INTEGER,'
                           'home_address_id TEXT,'
                           'major TEXT,'
                           'FOREIGN KEY (userId) '
                           ' REFERENCES user (userId),'
                           'FOREIGN KEY (home_address_id) '
                           ' REFERENCES address (address_id)'
                           ');')
        contents = pd.read_csv('Bidders.csv', engine='python')
        for row in contents.iterrows():
            connection.execute('INSERT OR IGNORE INTO bidders '
                               '(userId,first_name,last_name,gender,age,home_address_id,major) '
                               'VALUES(?, ?, ?, ?, ?, ?, ?)',
                               (row[1].email, row[1].first_name, row[1].last_name, row[1].gender, row[1].age, row[1].home_address_id, row[1].major))
        connection.commit()  # submit change in database
        bidderBool = 1


def createSeller():
    global sellerBool
    if sellerBool != 1:
        connection = sql.connect('database.db')
        connection.execute('CREATE TABLE IF NOT EXISTS sellers'
                           '(userId TEXT PRIMARY KEY NOT NULL, '
                           'bank_routing_number TEXT,'
                           'bank_account_number TEXT,'
                           'balance REAL,'
                           'rating REAL,'
                           'FOREIGN KEY (userId) '
                           ' REFERENCES user (userId)'
                           '     ON UPDATE CASCADE'
                           ');')

        # Bidder_Email, Seller_Email, Date, Rating, Rating_Desc
        connection.execute('CREATE TABLE IF NOT EXISTS ratings'
                           '(rateId INTEGER,'
                           'Bidder_Email TEXT , '
                           'Seller_Email TEXT ,'
                           'Date TEXT,'
                           'Rating REAL,'            
                           'Rating_Desc TEXT,'
                           'PRIMARY KEY(rateId)'
                           ');')

        contents = pd.read_csv('Sellers.csv', engine='python')
        for row in contents.iterrows():
            connection.execute('INSERT OR IGNORE INTO sellers (userId,bank_routing_number,bank_account_number,balance,rating) VALUES(?, ?, ?, ?, ?)',
                               (row[1].email, row[1].bank_routing_number, row[1].bank_account_number, row[1].balance, 0))

        contentsrating = pd.read_csv('Ratings.csv', engine='python')
        for row in contentsrating.iterrows():
            connection.execute('INSERT OR IGNORE INTO ratings (Bidder_Email,Seller_Email,Date,Rating,Rating_Desc) VALUES(?, ?, ?, ?,?)',
                               (row[1].Bidder_Email, row[1].Seller_Email, row[1].Date, row[1].Rating, row[1].Rating_Desc))
        connection.commit()

        # match seller and seller rating
        for row in contents.iterrows():
            connection.execute('UPDATE sellers '
                               'SET rating = '
                               '(SELECT sum(Rating)/count(Rating) AS overAllRating '
                               'FROM ratings '
                               'WHERE Seller_Email = ?)'
                               'WHERE userId = ?',(row[1].email,row[1].email))



        connection.execute('CREATE TABLE IF NOT EXISTS Local_Vendors'
                           '(userId TEXT PRIMARY KEY NOT NULL, '
                           'Business_Name TEXT,'
                           'Business_Address_ID TEXT,'
                           'Customer_Service_Phone_Number TEXT,'
                           'FOREIGN KEY (userId) '
                           ' REFERENCES sellers (userId)'
                           '     ON UPDATE CASCADE,'
                           'FOREIGN KEY (Business_Address_ID) '
                           ' REFERENCES address (address_id)'
                           ');')
        contents = pd.read_csv('Local_Vendors.csv', engine='python')
        for row in contents.iterrows():
            connection.execute('INSERT OR IGNORE INTO Local_Vendors '
                               '(userId,Business_Name,Business_Address_ID,Customer_Service_Phone_Number) '
                               'VALUES(?, ?, ?,?)',
                               (row[1].Email, row[1].Business_Name, row[1].Business_Address_ID,row[1].Customer_Service_Phone_Number))
        connection.commit()  # submit change in database
        sellerBool = 1


def createHelpDesk():
    global helpDeskBool
    if helpDeskBool != 1:
        connection = sql.connect('database.db')
        connection.execute('CREATE TABLE IF NOT EXISTS Helpdesk'
                           '(userId TEXT PRIMARY KEY NOT NULL, '
                           'position TEXT,'
                           'FOREIGN KEY (userId) '
                           ' REFERENCES user (userId)'
                           ');')
        contents = pd.read_csv('Helpdesk.csv', engine='python')
        for row in contents.iterrows():
            connection.execute('INSERT OR IGNORE INTO Helpdesk (userId,position) VALUES(?, ?)',
                               (row[1].email, row[1].Position))
        connection.execute('INSERT OR IGNORE INTO users (userId,password) VALUES(?, ?)',
                           ('helpdeskteam@lsu.edu',str((hashlib.sha256('helpdeskteam@lsu.edu'.encode())).hexdigest())))
        connection.execute('CREATE TABLE IF NOT EXISTS requests'
                           '(request_id INTEGER PRIMARY KEY NOT NULL, '
                           'sender_email TEXT,'
                           'helpdesk_staff_email TEXT,'
                           'request_type TEXT,'
                           'request_desc TEXT,'
                           'request_status TEXT'
                           ');')
        contents = pd.read_csv('Requests.csv', engine='python')
        for row in contents.iterrows():
            connection.execute('INSERT OR IGNORE INTO requests (request_id,sender_email,helpdesk_staff_email,request_type,request_desc,request_status) VALUES(?, ?,?,?,?,?)',
                               (row[1].request_id,row[1].sender_email,row[1].helpdesk_staff_email,row[1].request_type,row[1].request_desc,row[1].request_status))
        connection.commit()  # submit change in database
        helpDeskBool = 1


def valid_login(userId, password,op):
    # I use op code to notify three function,add,delete and only read
    if userBool != 1: # check whether user is existed
        createUser()
    if op == 1:
        if bidderBool != 1:
            # check whether bidder is existed in db
            createBidder()
            createAddr()
            createSeller()
        connection = sql.connect('database.db')
        cursor = connection.execute('SELECT userId FROM bidders WHERE userId = ?;', (userId,))
        result = cursor.fetchall()
        if not result:
            return False
        else:
            cursor = connection.execute('SELECT password FROM users WHERE userId = ?;', (userId,))
            result = cursor.fetchall()
            if result:
                tmp = str(hashlib.sha256(password.encode()).hexdigest())
                return tmp == result[0][0]
            else:
                return False
    elif op == 2:
        if sellerBool != 1:
            # check whether bidder is existed in db
            createSeller()

        connection = sql.connect('database.db')
        cursor = connection.execute('SELECT userId FROM sellers WHERE userId = ?;', (userId,))
        result = cursor.fetchall()
        if not result:
            return False
        else:
            cursor = connection.execute('SELECT password FROM users WHERE userId = ?;', (userId,))
            result = cursor.fetchall()
            if result:
                tmp = str(hashlib.sha256(password.encode()).hexdigest())
                return tmp == result[0][0]
            else:
                return False

    elif op == 3:
        if helpDeskBool != 1:
            # check whether bidder is existed in db
            createHelpDesk()

        connection = sql.connect('database.db')
        cursor = connection.execute('SELECT userId FROM Helpdesk WHERE userId = ?;', (userId,))
        result = cursor.fetchall()
        if not result:
            return False
        else:
            cursor = connection.execute('SELECT password FROM users WHERE userId = ?;', (userId,))
            result = cursor.fetchall()
            if result:
                tmp = str(hashlib.sha256(password.encode()).hexdigest())
                return tmp == result[0][0]
            else:
                return False
    else:
        return False
    return False

def createAccountBidder(userId
                        , first_name
                        , last_name
                        , gender
                        , age
                        , major
                        , editPassword
                        , credit_card_num
                        , card_type
                        , expire_month
                        , expire_year
                        , security_code
                        , street_num
                        , street_name
                        , zipcode):
    createBidder()
    createAddr()
    createUser()
    createSeller()

    paymentHelp.createCard()
    connection = sql.connect('database.db')
    addressId=str(hashlib.sha1((str(street_num)+street_name+str(zipcode)).encode()).hexdigest())
    connection.execute('INSERT OR IGNORE INTO address (address_id,zipcode,street_num,street_name) VALUES(?, ?, ?, ?)',
                       (addressId, zipcode, street_num, street_name))
    connection.execute('INSERT OR IGNORE INTO users (userId,password) VALUES(?, ?)',
                       (userId, str((hashlib.sha256(editPassword.encode())).hexdigest())))
    connection.execute('INSERT OR IGNORE INTO bidders '
                       '(userId,first_name,last_name,gender,age,home_address_id,major) '
                       'VALUES(?, ?, ?, ?, ?, ?, ?)',
                       (userId, first_name, last_name, gender, age,
                        addressId, major))
    connection.execute('INSERT OR IGNORE INTO creditCards '
                       '(credit_card_num,card_type,expire_month,expire_year,security_code,Owner_email) '
                       'VALUES(?, ?, ?, ?, ?, ?)',
                       (credit_card_num, card_type, expire_month, expire_year,
                        security_code,
                        userId))

    connection.commit()

def createAccountSeller(userId, editPassword, bank_account_number, bank_routing_number):
    createUser()
    createSeller()
    connection = sql.connect('database.db')
    connection.execute('INSERT OR IGNORE INTO users (userId,password) VALUES(?, ?)',
                       (userId, str((hashlib.sha256(editPassword.encode())).hexdigest())))
    connection.execute(
        'INSERT OR IGNORE INTO sellers (userId,bank_routing_number,bank_account_number,balance,rating) VALUES(?, ?, ?, ?, ?)',
        (userId, bank_routing_number, bank_account_number, 0, 0))
    connection.commit()
