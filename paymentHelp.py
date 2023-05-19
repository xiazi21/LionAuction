import sqlite3 as sql
import pandas as pd
from datetime import date

cardBool = 0

def createCard():
    global cardBool
    if cardBool != 1:
        connection = sql.connect('database.db')
        # credit_card_num,card_type,expire_month,expire_year,security_code,Owner_email
        connection.execute('CREATE TABLE IF NOT EXISTS creditCards'
                           '(credit_card_num TEXT PRIMARY KEY NOT NULL, '
                           'card_type TEXTL,'
                           'expire_month TEXT,'
                           'expire_year TEXT,'
                           'security_code TEXT,'
                           'Owner_email TEXT,'
                           'FOREIGN KEY (Owner_email) '
                           ' REFERENCES bidders (userId)'
                           ');')
        contents = pd.read_csv('Credit_Cards.csv', engine='python')
        for row in contents.iterrows():
            connection.execute('INSERT OR IGNORE INTO creditCards '
                               '(credit_card_num,card_type,expire_month,expire_year,security_code,Owner_email) '
                               'VALUES(?, ?, ?, ?, ?, ?)',
                               (row[1].credit_card_num, row[1].card_type, row[1].expire_month, row[1].expire_year,
                                row[1].security_code,
                                row[1].Owner_email))

    #Transaction_ID,Seller_Email,Listing_ID,Bidder_Email,Date,Payment

        connection.execute('CREATE TABLE IF NOT EXISTS transactionTable'
                           '(Transaction_ID INTEGER PRIMARY KEY NOT NULL, '
                           'Seller_Email TEXT,'
                           'Listing_ID TEXT,'
                           'Bidder_Email TEXT,'
                           'Date TEXT,'
                           'Payment TEXT,'
                           'FOREIGN KEY (Bidder_Email) '
                           ' REFERENCES bidders (userId),'
                           'FOREIGN KEY (Seller_Email) '
                           ' REFERENCES auctionList (Seller_Email),'
                           'FOREIGN KEY (Listing_ID) '
                           ' REFERENCES auctionList (Listing_ID)'
                           ');')
        contents = pd.read_csv('Transactions.csv', engine='python')
        for row in contents.iterrows():
            connection.execute('INSERT OR IGNORE INTO transactionTable '
                               '(Transaction_ID, Seller_Email,Listing_ID,Bidder_Email,Date,Payment) '
                               'VALUES(?, ?, ?, ?, ?, ?)',
                               (row[1].Transaction_ID, row[1].Seller_Email, row[1].Listing_ID, row[1].Bidder_Email,
                                row[1].Date,
                                row[1].Payment))
        connection.commit()

        cardBool = 1


def getCardList(userId):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT  card_type,credit_card_num FROM creditCards WHERE Owner_email = ?;', (userId,))
    result = cursor.fetchall()
    return result


def getCardSecurityCode(cardNum):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT security_code  FROM creditCards WHERE credit_card_num = ?;', (str(cardNum),))
    result = cursor.fetchall()
    if result:
        return int(result[0][0])
    else:
        return None


def getCurrentPrice(selllerEmail,listId):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT Current_Price FROM auctionList WHERE Seller_Email = ? AND Listing_ID = ?;',
        (selllerEmail, listId))
    result = cursor.fetchall()
    return int(result[0][0])


def finishPay(selllerEmail,listId,bidderEmail):
    # ADD TUPLE OF TRANS AND add seller balance
    createCard()
    currPrice = getCurrentPrice(selllerEmail,listId)
    connection = sql.connect('database.db')
    todays_date = date.today()
    connection.execute('INSERT INTO transactionTable '
                       '(Seller_Email,Listing_ID,Bidder_Email,Date,Payment) '
                       'VALUES( ?, ?, ?, ?, ?)',
                       (selllerEmail, int(listId), bidderEmail,
                        str(todays_date.strftime('%m/%d/%y')),
                        currPrice))
    connection.execute('UPDATE sellers SET balance = (SELECT balance FROM sellers WHERE userId = ?) + ? WHERE userId = ?;',(selllerEmail,currPrice,selllerEmail))
    connection.commit()

def strProcess(stringL):
    stringL = stringL[1:]
    stringL = stringL[:-1]
    result = stringL.split(',')
    result[0] = result[0][1:-1]
    result[1] =result[1][2:-1]
    result[2] = int(result[2][2:-1])
    return result


