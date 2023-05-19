import sqlite3 as sql
import hashlib

def getBidderMessage(userId):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM bidders WHERE userId = ?;', (userId,))
    result = cursor.fetchall()
    return result


def getBidderAddressMessage(userId):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT home_address_id '
        'FROM bidders WHERE userId = ?;', (userId,))
    result = cursor.fetchall()
    cursor = connection.execute(
        'SELECT * '
        'FROM address WHERE address_id = ?;', (result[0][0],))
    result = cursor.fetchall()
    return result


def getCardMessage(userId):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM creditCards WHERE Owner_email = ?;', (userId,))
    result = cursor.fetchall()
    return result


def updatePassword(userId,editPassword):
    connection = sql.connect('database.db')
    connection.execute('UPDATE users '
                           'SET password = ? '
                           'WHERE userId = ?;',
                           (str((hashlib.sha256(editPassword.encode())).hexdigest()),userId))
    connection.commit()


def updateBidder(userId, first_name, last_name, gender, age, major):
    connection = sql.connect('database.db')
    connection.execute('UPDATE bidders '
                       'SET first_name=?, last_name=?, gender=?, age=?, major=? '
                       'WHERE userId = ?;',
                       (first_name, last_name, gender, age, major,userId))
    connection.commit()





def checkZip(zipcode):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM zipcode WHERE zipcode = ?;', (zipcode,))
    result = cursor.fetchall()
    if result:
        return True
    else:
        return False

def updateZip(zipcode,city,state):
    connection = sql.connect('database.db')
    connection.execute('INSERT OR IGNORE INTO zipcode (zipcode,city,state) VALUES(?, ?, ?)',
                               (zipcode,city,state))
    connection.commit()


def updateBidderAddress(userId, zipcode, street_num, street_name):
    connection = sql.connect('database.db')
    connection.execute('UPDATE address '
                       'SET zipcode=?, street_num=?, street_name=? '
                       'WHERE address_id=(SELECT home_address_id FROM bidders WHERE userId = ?);',
                       (zipcode, street_num, street_name, userId))
    connection.commit()


def updateSellerAddress(userId, zipcode, street_num, street_name):
    connection = sql.connect('database.db')
    connection.execute('UPDATE address '
                       'SET zipcode=?, street_num=?, street_name=? '
                       'WHERE address_id=(SELECT Business_Address_ID FROM Local_Vendors WHERE userId = ?);',
                       (zipcode, street_num, street_name, userId))
    connection.commit()


def updateCard(credit_card_num, card_type, expire_month, expire_year, security_code, Owner_email):
    connection = sql.connect('database.db')
    connection.execute('DELETE FROM creditCards WHERE Owner_email=?;', (Owner_email,))
    connection.execute('INSERT OR IGNORE INTO creditCards '
                       '(credit_card_num, card_type, expire_month, expire_year, security_code, Owner_email) '
                       'VALUES(?, ?, ?, ?, ?, ?)',
                       (credit_card_num, card_type, expire_month, expire_year, security_code, Owner_email))
    connection.commit()


def getSellerMessage(userId):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM sellers WHERE userId = ?;', (userId,))
    result = cursor.fetchall()
    return result

def getLocalVendorMessage(userId):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM Local_Vendors WHERE userId = ?;', (userId,))
    result = cursor.fetchall()
    return result

def getSellerAddressMessage(userId):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT Business_Address_ID '
        'FROM Local_Vendors WHERE userId = ?;', (userId,))
    result = cursor.fetchall()
    result = result[0][0]
    cursor = connection.execute(
        'SELECT * '
        'FROM address WHERE address_id = ?;', (result,))
    result = cursor.fetchall()
    return result


def updateSeller(userId, bank_routing_number, bank_account_number):
    connection = sql.connect('database.db')
    connection.execute('UPDATE sellers '
                       'SET bank_routing_number=?, bank_account_number=?'
                       'WHERE userId = ?;',
                       (bank_routing_number, bank_account_number, userId))
    connection.commit()

def updateVendor(userId, Business_Name,Customer_Service_Phone_Number):
    connection = sql.connect('database.db')
    connection.execute('UPDATE Local_Vendors '
                       'SET Business_Name=?, Customer_Service_Phone_Number=?'
                       'WHERE userId = ?;',
                       (Business_Name, Customer_Service_Phone_Number, userId))
    connection.commit()