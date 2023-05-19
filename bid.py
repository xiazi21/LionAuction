import sqlite3 as sql



def stringProcess(strIng):
    count = 0
    cont = 0
    result1=[]
    result2=[]
    result = []
    for i in strIng:
        if i == "'":
            count += 1
        elif count < 2 and i != '(':
            result1.append(i)
        elif i == ',':
            cont+=1
        elif cont == 1 and i != ')':
            result2.append(i)
    result.append(''.join(result1))
    result.append(int(''.join(result2)))
    return result


def bidConfirmCatchInfo(email,id):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT Seller_Email,Listing_ID, Auction_Title, Product_Name, Product_Description, Quantity, Max_bids, Current_Bids,Current_Price '
        'FROM auctionList WHERE Status = 1 AND Seller_Email = ? AND Listing_ID = ?;', (email,id))
    result = cursor.fetchall()
    result = list(result[0])

    return result


def lastBid(selllerEmail,listId):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT Max_bids, Current_Bids FROM auctionList WHERE Status = 1 AND Seller_Email = ? AND Listing_ID = ?;', (selllerEmail, listId))
    result = cursor.fetchall()
    try:
        result = list(result[0])
    except:
        return False
    if result[0] - result[1] == 1:
        return True
    else:
        return False

def checkSuccess(sellerEmail, listId,newPrice):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT Reserve_Price FROM auctionList WHERE Seller_Email = ? AND Listing_ID = ?;',
        (sellerEmail, listId))
    result = cursor.fetchall()
    result = float(result[0][0])
    if result <= newPrice:
        return True
    else:
        return False

def updateFailBid(selllerEmail, listId):
    connection = sql.connect('database.db')
    connection.execute('UPDATE auctionList '
                       'SET Status = ?'
                       'WHERE Seller_Email = ? AND Listing_ID = ?;',
                       (0,selllerEmail, listId))
    connection.commit()

def addBidRecord(selllerEmail, listId, bidderId, bidPrice, op):
    # op = 0 last bid; op = 1 not last bid
    connection = sql.connect('database.db')
    connection.execute('INSERT OR IGNORE INTO Bids '
                       '(Seller_Email,Listing_ID,Bidder_Email,Bid_Price) '
                       'VALUES(?, ?, ?, ?)',
                       (selllerEmail, listId, bidderId, bidPrice))
    connection.commit()

    if op == 0:
        # last bid
        cursor = connection.execute(
            'SELECT Current_Bids FROM auctionList WHERE Seller_Email = ? AND Listing_ID = ?;',
            (selllerEmail, listId))
        result = cursor.fetchall()
        result = list(result[0])
        connection.execute('UPDATE auctionList '
                           'SET Current_Bids = ?, Status = ?,Current_Price = ? '
                           'WHERE Seller_Email = ? AND Listing_ID = ?;',
                           (result[0]+1, 2, bidPrice, selllerEmail, listId))

    else:
        cursor = connection.execute(
            'SELECT Current_Bids FROM auctionList WHERE Seller_Email = ? AND Listing_ID = ?;',
            (selllerEmail, listId))
        result = cursor.fetchall()
        result = list(result[0])
        connection.execute(
            'UPDATE auctionList SET Current_Bids = ?,Current_Price = ? WHERE Seller_Email = ? AND Listing_ID = ?;',
            (result[0] + 1, bidPrice ,selllerEmail, listId))
    connection.commit()


def findCurrentBidder(selllerEmail,listId,userId):
    # check whtehre it is current winner
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT Bidder_Email, MAX(Bid_Price) '
        'FROM Bids '
        'WHERE  Seller_Email = ? AND Listing_ID = ? '
        'GROUP BY Seller_Email, Listing_ID;',
        (selllerEmail, listId))
    result = cursor.fetchall()
    if not result:
        return False
    result = list(result[0])
    if result[0] == userId:
        return True
    else:
        return False

def addNoteLoser(selllerEmail,listId):
    # add who need notetification for those loser of bids
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT Bidder_Email '
        'FROM Bids '
        'WHERE  Seller_Email = ? AND Listing_ID = ? ',
        (selllerEmail, listId))
    result = cursor.fetchall()
    for i in result:
        connection.execute('INSERT OR IGNORE INTO noteForLoser '
                           '(Seller_Email,Listing_ID,Bidder_Email) '
                           'VALUES(?, ?, ?)',
                           (selllerEmail, listId,i[0]))
    connection.commit()