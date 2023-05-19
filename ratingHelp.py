import sqlite3 as sql
import pandas as pd
from datetime import date


def getInfo(selllerEmail,listId):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT Product_Name,Current_Price FROM auctionList WHERE Seller_Email = ? AND Listing_ID = ?;',
        (selllerEmail, listId))
    result = cursor.fetchall()
    return result

def createAndUpdateRates(selllerEmail,bidderEmail,rate,rateDes):
    connection = sql.connect('database.db')

    todays_date = date.today()
    connection.execute(
        'INSERT OR IGNORE INTO ratings (Bidder_Email,Seller_Email,Date,Rating,Rating_Desc) VALUES(?, ?, ?, ?,?)',
        (bidderEmail, selllerEmail, str(todays_date.strftime('%m/%d/%y')), rate, rateDes))
    connection.commit()
    connection.execute('UPDATE sellers '
                       'SET rating = '
                       '(SELECT sum(Rating)/count(Rating) AS overAllRating '
                       'FROM ratings '
                       'WHERE Seller_Email = ?)'
                       'WHERE userId = ?', (selllerEmail,selllerEmail))
    connection.commit()