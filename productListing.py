import sqlite3 as sql
import hashlib
import pandas as pd
import cate
import seller

auctionListingBool = 0


def auctionListCreate():
    # create the bids and auction list, and match their data
    global auctionListingBool
    if auctionListingBool == 0:
        connection = sql.connect('database.db')
        connection.execute('CREATE TABLE IF NOT EXISTS auctionList'
                           '(Seller_Email TEXT NOT NULL, '
                           'Listing_ID INTEGER NOT NULL,'
                           'Category TEXT,'
                           'Auction_Title TEXT,'
                           'Product_Name TEXT,'
                           'Product_Description TEXT,'
                           'Quantity INTEGER,'
                           'Reserve_Price REAL,'
                           'Max_bids INTEGER,'
                           'Status INTEGER,'
                           'Current_Bids INTEGER,'
                           'Leave_Reason TEXT,'
                           'Current_Price REAL,'
                           'PRIMARY KEY(Seller_Email, Listing_ID)'
                           ');')

        connection.execute('CREATE TABLE IF NOT EXISTS promotions'
                           '(Seller_Email TEXT NOT NULL, '
                           'Listing_ID INTEGER NOT NULL,'
                           'Category TEXT,'
                           'Auction_Title TEXT,'
                           'Product_Name TEXT,'
                           'Product_Description TEXT,'
                           'Quantity INTEGER,'
                           'Reserve_Price REAL,'
                           'Max_bids INTEGER,'
                           'Status INTEGER,'
                           'Current_Bids INTEGER,'
                           'Leave_Reason TEXT,'
                           'Current_Price REAL,'
                           'PRIMARY KEY(Seller_Email, Listing_ID)'
                           ');')

        contents = pd.read_csv('Auction_Listings.csv', engine='python')
        for row in contents.iterrows():
            connection.execute('INSERT OR IGNORE INTO auctionList '
                               '(Seller_Email,Listing_ID,Category,Auction_Title,Product_Name,Product_Description,Quantity,Reserve_Price,Max_bids,Status,Current_Bids,Leave_Reason,Current_Price) '
                               'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                               (row[1].Seller_Email, row[1].Listing_ID, row[1].Category, row[1].Auction_Title,
                                row[1].Product_Name,
                                row[1].Product_Description, row[1].Quantity,
                                ((row[1].Reserve_Price)[1:]).replace(',', ''), row[1].Max_bids, row[1].Status, 0, 'N/A',
                                0))

        connection.execute('CREATE TABLE IF NOT EXISTS Bids'
                           '(Bid_ID INTEGER PRIMARY KEY NOT NULL,'
                           'Seller_Email TEXT,'
                           'Listing_ID TEXT,'
                           'Bidder_Email TEXT,'
                           'Bid_Price REAL'
                           ');')
        contents = pd.read_csv('Bids.csv', engine='python')
        for row in contents.iterrows():
            connection.execute('INSERT OR IGNORE INTO Bids '
                               '(Bid_ID,Seller_Email,Listing_ID,Bidder_Email,Bid_Price) '
                               'VALUES(?, ?, ?, ?, ?)',
                               (row[1].Bid_ID, row[1].Seller_Email, row[1].Listing_ID, row[1].Bidder_Email,
                                row[1].Bid_Price))

        connection.execute('CREATE TABLE IF NOT EXISTS noteForLoser'
                           '(Note_ID INTEGER PRIMARY KEY NOT NULL,'
                           'Seller_Email TEXT,'
                           'Listing_ID TEXT,'
                           'Bidder_Email TEXT'
                           ');')

        connection.commit()  # submit change in database

        cursor = connection.execute(
            'SELECT Seller_Email,Listing_ID,COUNT(*),MAX(Bid_Price) FROM Bids GROUP BY Seller_Email, Listing_ID;')
        result = cursor.fetchall()
        for i in result:
            cursor = connection.execute(
                'SELECT Current_Bids, Current_Price FROM auctionList WHERE Seller_Email = ? AND Listing_ID = ?;',
                (i[0], i[1]))
            temp = cursor.fetchall()
            if temp[0][0] < i[2]:
                # Find whether the version in database is old , which means have bids but time in db is 0
                connection.execute('UPDATE auctionList SET Current_Bids = ? WHERE Seller_Email = ? AND Listing_ID = ?;',
                                   (i[2], i[0], i[1]))
                connection.commit()
            if temp[0][1] < i[3]:
                # bid price matching
                connection.execute(
                    'UPDATE auctionList SET Current_Price = ? WHERE Seller_Email = ? AND Listing_ID = ?;',
                    (i[3], i[0], i[1]))
                connection.commit()
        auctionListingBool = 1


def cate_find_list(parent):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT category_name FROM Categories WHERE parent_category = ?;', (parent,))
    result = cursor.fetchall()
    for i in range(len(result)):
        result[i] = result[i][0]
    return result


def selectProduct(category):
    if category == 'Root':
        connection = sql.connect('database.db')
        cursor = connection.execute(
            'SELECT  Seller_Email,Listing_ID, Auction_Title, Product_Name, Product_Description, Quantity, Max_bids, Current_Bids,Current_Price FROM auctionList WHERE Status = 1;')
        result = cursor.fetchall()
        return result
    else:
        connection = sql.connect('database.db')
        cursor = connection.execute(
            'SELECT Seller_Email,Listing_ID, Auction_Title, Product_Name, Product_Description, Quantity, Max_bids, Current_Bids,Current_Price '
            'FROM auctionList WHERE Status = 1 AND Category = ?;', (category,))
        result = cursor.fetchall()
        # first search the product which directly under the parent category

        # start to find the children of the parent if existed
        if not cate_find_list(category):
            return result
        else:
            children = cate.cate_find(category)
            targetList = []
            i = 0
            while children:
                # a pop
                current = children[i]
                childList = cate_find_list(current)
                if childList:
                    targetList.append(current)
                    children.remove(current)
                    children = children + childList
                else:
                    targetList.append(current)
                    children.remove(current)
        for i in targetList:
            cursor = connection.execute(
                'SELECT Seller_Email,Listing_ID,Auction_Title, Product_Name, Product_Description, Quantity, Max_bids, Current_Bids,Current_Price '
                'FROM auctionList WHERE Status = 1 AND Category = ?;', (i,))
            temp = cursor.fetchall()
            result = result + temp
        return result


def selectPromotion():
    seller.updatePromotion()
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT Seller_Email,Listing_ID,Auction_Title, Product_Name, Product_Description, Quantity, Max_bids, Current_Bids,Current_Price '
        'FROM promotions WHERE Status = 1 ;')
    result = cursor.fetchall()
    return result


def selectProductBySeller(sellerEmail):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT Seller_Email,Listing_ID,Auction_Title, Product_Name, Product_Description, Quantity, Max_bids, Current_Bids,Current_Price '
        'FROM auctionList WHERE Status = 1 AND Seller_Email = ?;', (sellerEmail,))
    result = cursor.fetchall()
    return result


def checkNote(bidderEmail):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT  Seller_Email,Listing_ID FROM noteForLoser WHERE Bidder_Email = ?;', (bidderEmail,))
    result = cursor.fetchall()
    if not result:
        return []
    else:
        for i in result:
            cursor = connection.execute(
                'SELECT Product_Name '
                'FROM auctionList WHERE Seller_Email = ? AND Listing_ID = ?;', (i[0], i[1]))
            temp = cursor.fetchall()
            connection.execute('DELETE FROM noteForLoser WHERE Bidder_Email=?;', (bidderEmail,))
            connection.execute('DELETE FROM noteForLoser WHERE Bidder_Email=?;', (bidderEmail,))
            connection.commit()
            return temp


def selectProductSearch(searchInfo):
    searchInfo = '%' + searchInfo + '%'
    connection = sql.connect('database.db')
    cursor = connection.execute(
        "SELECT DISTINCT Seller_Email,Listing_ID, Auction_Title, Product_Name, Product_Description, Quantity, Max_bids, Current_Bids,Current_Price "
        "FROM auctionList WHERE Status = 1 AND ((Auction_Title LIKE ?) OR (Product_Name LIKE ?) OR (Product_Description LIKE ?)) ;",
        (searchInfo, searchInfo, searchInfo))
    result = cursor.fetchall()
    return result
