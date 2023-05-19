import sqlite3 as sql


def getSellerRate(sellerEmail):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT rating FROM sellers WHERE userId = ?;',
        (sellerEmail,))
    result = cursor.fetchall()
    if result:
        return result[0][0]
    else:
        return 'No rate now'


def getSellerRateList(sellerEmail):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT Rating,Rating_Desc FROM ratings WHERE Seller_Email = ?;',
        (sellerEmail,))
    result = cursor.fetchall()
    return result


def getActiveProduct(sellerEmail):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM auctionList WHERE Status = 1 AND Seller_Email = ?;', (sellerEmail,))
    result = cursor.fetchall()
    return result


def getSoldProduct(sellerEmail):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM auctionList WHERE Status = 2 AND Seller_Email = ?;', (sellerEmail,))
    result = cursor.fetchall()
    return result


def getInactiveProduct(sellerEmail):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM auctionList WHERE Status = 0 AND Seller_Email = ?;', (sellerEmail,))
    result = cursor.fetchall()
    return result

def getProductDetail(sellerEmail,listId):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM auctionList WHERE Seller_Email = ? AND Listing_ID = ?;', (sellerEmail,listId))
    result = cursor.fetchall()
    return result

def updateProduct(sellerEmail,ListingID,Auction_Title,Product_Name,Product_Description,Quantity,Reserve_Price,Max_bids,Status,leaveReason):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT Current_Bids, Status '
        'FROM auctionList WHERE Seller_Email = ? AND Listing_ID = ?;', (sellerEmail, ListingID))
    result = cursor.fetchall()
    currentBid = int (result[0][0])
    currentStatus = int(result[0][1])
    if Status == 1 and currentStatus == 0 and Max_bids <= currentBid:
        # renew stoped bidding
        return False
    elif Status == 1 and currentStatus == 1 and Max_bids <= currentBid:
        return  False
    else:
        if Status == 1:
            leaveReason = 'N/A'
        if Status == 0:
            connection.execute('DELETE FROM promotions WHERE Seller_Email=? AND Listing_ID=?;',
                               (sellerEmail, ListingID))
        connection.execute('UPDATE auctionList '
                           'SET Auction_Title=?,Product_Name=?,Product_Description=?,Quantity=?,Reserve_Price=?,Max_bids=?,Status=?,Leave_Reason=? '
                           'WHERE Seller_Email = ? AND Listing_ID = ?;',
                           (Auction_Title,Product_Name,Product_Description,Quantity,Reserve_Price,Max_bids,Status,leaveReason,sellerEmail,ListingID))
        connection.commit()
        return True

def getBalance(sellerEmail):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT balance FROM sellers WHERE userId = ?;',
        (sellerEmail,))
    result = cursor.fetchall()
    if result:
        return result[0][0]
    else:
        return 'No balance now'


def updateProductCate(sellerEmail,listId,newCate):
    connection = sql.connect('database.db')
    try:
        connection.execute('UPDATE auctionList '
                                   'SET Category=?'
                                   'WHERE Seller_Email = ? AND Listing_ID = ?;',
                                   (newCate,sellerEmail,listId))
        connection.commit()
        return True
    except:
        return False


def addProduct(sellerEmail,cateGory,Auction_Title,Product_Name,Product_Description,Quantity,Reserve_Price,Max_bids):
    connection = sql.connect('database.db')


    cursor = connection.execute(
        'SELECT max(Listing_ID) FROM auctionList WHERE Seller_Email = ?;',
        (sellerEmail,))
    result = cursor.fetchall()
    try:
        Listing_ID = int(result[0][0])+1
    except:
        Listing_ID = 0
    connection.execute('INSERT INTO auctionList '
                       '(Seller_Email,Listing_ID,Category,Auction_Title,Product_Name,Product_Description,Quantity,Reserve_Price,Max_bids,Status,Current_Bids,Leave_Reason,Current_Price) '
                       'VALUES(?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (sellerEmail, Listing_ID,cateGory, Auction_Title,
                        Product_Name,
                        Product_Description, Quantity, Reserve_Price, Max_bids,
                        1, 0, 'N/A', 0))
    connection.commit()

def updatePromotion():
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT promotions.Seller_Email,promotions.Listing_ID '
                                'FROM promotions INNER JOIN auctionList '
                                'ON promotions.Listing_ID = auctionList.Listing_ID AND promotions.Seller_Email = auctionList.Seller_Email '
                                'WHERE promotions.Status <> auctionList.Status '
                                'OR promotions.cateGory <> auctionList.cateGory '
                                'OR promotions.Auction_Title <> auctionList.Auction_Title '
                                'OR promotions.Product_Name <> auctionList.Product_Name '
                                'OR promotions.Product_Description <> auctionList.Product_Description '
                                'OR promotions.Quantity <> auctionList.Quantity '
                                'OR promotions.Reserve_Price <> auctionList.Reserve_Price '
                                'OR promotions.Max_bids <> auctionList.Max_bids '
                                'OR promotions.Current_Bids <> auctionList.Current_Bids '
                                'OR promotions.Leave_Reason <> auctionList.Leave_Reason '
                                'OR promotions.Current_Price <> auctionList.Current_Price;')
    result = cursor.fetchall()
    if result:
        for row in result:
            connection.execute('DELETE FROM promotions WHERE Seller_Email=? AND Listing_ID=?;',
                               (row[0],row[1]))
            connection.commit()
            cursor = connection.execute('SELECT * '
                                'FROM auctionList '
                                'WHERE Seller_Email=? AND Listing_ID=?;',(row[0],row[1]))
            temp = cursor.fetchall()
            for (sellerEmail, Listing_ID, cateGory, Auction_Title,
                                    Product_Name,
                                    Product_Description, Quantity, Reserve_Price, Max_bids,
                                    Status, Current_Bids, Leave_Reason, Current_Price) in temp:
                connection.execute('INSERT INTO promotions '
                                   '(Seller_Email,Listing_ID,Category,Auction_Title,Product_Name,Product_Description,Quantity,Reserve_Price,Max_bids,Status,Current_Bids,Leave_Reason,Current_Price) '
                                   'VALUES(?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                   (sellerEmail, Listing_ID, cateGory, Auction_Title,
                                    Product_Name,
                                    Product_Description, Quantity, Reserve_Price, Max_bids,
                                    Status, Current_Bids, Leave_Reason, Current_Price))
        connection.commit()



def addPromotion(sellerEmail,Listing_ID):
    updatePromotion()
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT count(*) FROM promotions WHERE Status = 1;')
    tempReservePrice = 0
    result = cursor.fetchall()
    try:
        accountPro = int(result[0][0])
    except:
        accountPro = 0
    if accountPro <= 5:
        cursor = connection.execute('SELECT * '
                                    'FROM auctionList '
                                    'WHERE Seller_Email=? AND Listing_ID=?;', (sellerEmail, Listing_ID))
        temp = cursor.fetchall()
        for (sellerEmail, Listing_ID, cateGory, Auction_Title,
             Product_Name,
             Product_Description, Quantity, Reserve_Price, Max_bids,
             Status, Current_Bids, Leave_Reason, Current_Price) in temp:
            tempReservePrice = Reserve_Price
            connection.execute('INSERT INTO promotions '
                               '(Seller_Email,Listing_ID,Category,Auction_Title,Product_Name,Product_Description,Quantity,Reserve_Price,Max_bids,Status,Current_Bids,Leave_Reason,Current_Price) '
                               'VALUES(?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                               (sellerEmail, Listing_ID, cateGory, Auction_Title,
                                Product_Name,
                                Product_Description, Quantity, Reserve_Price, Max_bids,
                                Status, Current_Bids, Leave_Reason, Current_Price))
        connection.commit()

        connection.execute(
            'UPDATE sellers SET balance = (SELECT balance FROM sellers WHERE userId = ?) - ? WHERE userId = ?;',
            (sellerEmail, tempReservePrice*0.05, sellerEmail))
        connection.commit()
        return True
    else:
        return False


def getActivePromotion(userId):
    updatePromotion()
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM promotions WHERE Status = 1 AND Seller_Email = ?;', (userId,))
    result = cursor.fetchall()
    return result

def checkPromotion(sellerEmail,Listing_ID):
    updatePromotion()
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * '
                               'FROM promotions '
                               'WHERE Seller_Email=? AND Listing_ID=?;', (sellerEmail, Listing_ID))
    result = cursor.fetchall()
    if result:
        return True
    else:
        return False



def checkMoneyPro(sellerEmail,listId):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT Reserve_Price '
                                'FROM auctionList '
                                'WHERE Seller_Email=? AND Listing_ID=?;', (sellerEmail, listId))
    result = cursor.fetchall()

    try:
        print(result)
        result = float(result[0][0])

        print('val', getBalance(sellerEmail))
        currBal = float(getBalance(sellerEmail))

    except:
        return False
    if result*0.05 >= currBal:
        return False
    else:
        return True

