from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3 as sql
import csv
import hashlib
import pandas as pd
import login
import cate
import productListing
import bid
import paymentHelp
import ratingHelp
import seller
import editProfileHelp
import HelpDesk

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'
app.secret_key = 'BAD_SECRET_KEY'

currentCategories = ''
currentUser = ''
currentUserType = ''


@app.route('/loginSuccess')
def successTemp():
    return render_template('loginSuccessTemp.html')


@app.route('/')
def index():
    # the backend of the index, the first page, after open the website and create different tables
    login.createAddr()
    cate.cate_create()
    productListing.auctionListCreate()
    paymentHelp.createCard()
    login.createUser()
    login.createHelpDesk()
    login.createBidder()
    login.createSeller()
    return render_template('index.html')


@app.route('/loginBidder', methods=['POST', 'GET'])
def loginBidder():
    # log in checker for bidders
    if request.method == 'POST':
        result = login.valid_login(request.form['userId'], request.form['password'], 1)
        if result:
            # if success user session to record the userId and user type
            session['userId'] = request.form['userId']
            session['userType'] = 'Bidder'
            return redirect(url_for('bidderMainPage'))
        else:
            error = 'User ID or Password incorrect'
            return render_template('loginBidder.html', error=error)
    return render_template('loginBidder.html')


@app.route('/loginSeller', methods=['POST', 'GET'])
def loginSeller():
    # log in checker for sellers
    if request.method == 'POST':
        result = login.valid_login(request.form['userId'], request.form['password'], 2)
        if result:
            # if success user session to record the userId and user type
            session['userId'] = request.form['userId']
            session['userType'] = 'Seller'
            return redirect(url_for('sellerMainPage'))
        else:
            error = 'User ID or Password incorrect'
            return render_template('loginSeller.html', error=error)
    return render_template('loginSeller.html')


@app.route('/loginHelpDesk', methods=['POST', 'GET'])
def loginHelpDesk():
    # log in checker for helpDesk
    if request.method == 'POST':
        result = login.valid_login(request.form['userId'], request.form['password'], 3)
        if result:
            # if success user session to record the userId and user type
            session['userId'] = request.form['userId']
            session['userType'] = 'HelpDesk'
            if session['userId'] == 'helpdeskteam@lsu.edu':
                # pseudo staff helpdeskteam@lsu.edu
                return redirect(url_for('HelpDeskMainPageHD'))
            else:
                return redirect(url_for('HelpDeskMainPageMem'))
        else:
            error = 'User ID or Password incorrect'
            return render_template('loginHelpDesk.html', error=error)
    return render_template('loginHelpDesk.html')


@app.route('/HelpDeskMainPageHD', methods=['POST', 'GET'])
def HelpDeskMainPageHD():
    # the main page for pseudo staff helpdeskteam@lsu.edu
    if request.method == 'POST':
        request_id = request.form['assignButton']
        comp_select_staff = request.form['comp_select_staff']
        # ger request id and the assign staff to assign a task to certain helpDesk staff
        if HelpDesk.assignStaff(request_id, comp_select_staff):
            # if the assign is successful
            # get the needed lists and flash message for notification
            unassignList = HelpDesk.getUnassignList()
            assignList = HelpDesk.getAssignList()
            completedList = HelpDesk.getCompletedList()
            staffList = HelpDesk.getStaffList()
            flash('The task assign successfully')
            return render_template('HelpDeskMainPageHD.html', staffList=staffList, currentUser=session['userId'],
                                   unassignList=unassignList,
                                   assignList=assignList, completedList=completedList)
        else:
            # get the needed lists and flash message for notification
            unassignList = HelpDesk.getUnassignList()
            assignList = HelpDesk.getAssignList()
            completedList = HelpDesk.getCompletedList()
            staffList = HelpDesk.getStaffList()
            flash('Fail to assign tasks')
            return render_template('HelpDeskMainPageHD.html', staffList=staffList, currentUser=session['userId'],
                                   unassignList=unassignList,
                                   assignList=assignList, completedList=completedList)
    elif request.method == 'GET':
        # get the needed lists
        unassignList = HelpDesk.getUnassignList()
        assignList = HelpDesk.getAssignList()
        completedList = HelpDesk.getCompletedList()
        staffList = HelpDesk.getStaffList()
        return render_template('HelpDeskMainPageHD.html', staffList=staffList, currentUser=session['userId'],
                               unassignList=unassignList, assignList=assignList, completedList=completedList)


@app.route('/HelpDeskMainPageMem', methods=['POST', 'GET'])
def HelpDeskMainPageMem():
    # for the staffs except helpdeskteam@lsu.edu
    if request.method == 'POST':
        request_id = request.form['logFinishButton']
        HelpDesk.updateStatusReq(request_id)  # log the request as finished
        cateList = cate.cate_find('Root')
        TodoList = HelpDesk.getTodoList(session['userId'])  # get the todo list
        return render_template('HelpDeskMainPageMem.html', cateList=cateList, currCate='Root',
                               currentUser=session['userId'], TodoList=TodoList)
    elif request.method == 'GET':
        TodoList = HelpDesk.getTodoList(session['userId'])  # get the todo list
        cateList = cate.cate_find('Root')
        return render_template('HelpDeskMainPageMem.html', cateList=cateList, currentUser=session['userId'],
                               TodoList=TodoList, currCate='Root')


@app.route('/HelpDeskMainPageMemCate', methods=['POST', 'GET'])
def HelpDeskMainPageMemCate():
    # add a new category
    if request.method == 'POST':
        op = request.args.get('op')
        currCate = request.args.get('currCate')
        comp_select_edit = request.form['comp_select_edit']
        cateName = request.form['cateName']
        if op == '0':
            # go deep, confirm
            currCate = comp_select_edit
            cateList = cate.cate_find(currCate)
        elif op == '1':
            # go back level
            parentCate = cate.cateFindParent(currCate)[0]
            cateList = cate.cate_find(parentCate)
            currCate = parentCate
        else:
            # submit
            HelpDesk.addNewCate(currCate, cateName)
            currCate = 'Root'
            cateList = cate.cate_find(currCate)
            flash('New category is added!')

        TodoList = HelpDesk.getTodoList(session['userId'])
        return render_template('HelpDeskMainPageMem.html', currCate=currCate, currentUser=session['userId'],
                               TodoList=TodoList, cateList=cateList)

    elif request.method == 'GET':
        TodoList = HelpDesk.getTodoList(session['userId'])
        cateList = cate.cate_find('Root')
        return render_template('HelpDeskMainPageMem.html', cateList=cateList, currentUser=session['userId'],
                               TodoList=TodoList, currCate='Root')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('userId', None)
    session.pop('userType', None)
    return redirect('/')


@app.route('/bidderViewSellerMainPage', methods=['GET'])
def bidderViewSellerMainPage():
    # the back of the seller mainpage for bidder, bidder can view the seller's page for view and bid the products of certain seller
    sellerEmail = request.args.get('sellerEmail')
    productList = productListing.selectProductBySeller(sellerEmail)
    overallRate = seller.getSellerRate(sellerEmail)
    rateList = seller.getSellerRateList(sellerEmail)
    return render_template('bidderSellerPage.html', sellerEmail=sellerEmail, overallRate=overallRate,
                           productList=productList, currentUser=session['userId'], rateList=rateList)


@app.route('/bidderMainPage', methods=['POST', 'GET'])
def bidderMainPage():
    cate.cate_create()
    productListing.auctionListCreate()
    # make sure the tables are created
    currentCateList = cate.cate_find('Root')
    global currentCategories
    currentCategories = 'Root'
    cateInfo = 'ALL'
    productList = productListing.selectProduct(currentCategories)
    promotionList = productListing.selectPromotion()
    if request.method == 'POST':
        # if want to bid, go to bid confirm page
        temp = bid.stringProcess(list(request.form['submit_button']))
        return redirect(url_for('bidConfirm', selllerEmail=temp[0], listId=temp[1]))
    elif request.method == 'GET':
        temp = productListing.checkNote(session['userId'])  # check whether current user have some losing bids
        if temp != []:
            for i in temp:
                flash('You fail the bidding for ' + str(i[0]))
        return render_template('bidderMainPage.html', promotionList=promotionList, cateList=currentCateList,
                               cateInfo=cateInfo, productList=productList, currentUser=session['userId'])


@app.route('/categoriesChange', methods=['POST', 'GET'])
def categoriesChange():
    # for go to sublevel of category and confirm choice
    if request.method == 'GET':
        return redirect(url_for('bidderMainPage'))
    cate.cate_create()
    productListing.auctionListCreate()
    # make sure the categories is created
    global currentCategories
    select = request.form.get('comp_select')
    currentCateList = cate.cate_find(str(select))
    currentCategories = str(select)
    cateInfo = currentCategories
    productListing.auctionListCreate()
    productList = productListing.selectProduct(currentCategories)
    promotionList = productListing.selectPromotion()
    return render_template('bidderMainPage.html', promotionList=promotionList, cateList=currentCateList,
                           cateInfo=cateInfo, productList=productList, currentUser=session['userId'])


@app.route('/bidMainPageSearch', methods=['POST', 'GET'])
def bidMainPageSearch():
    # search products for bidders
    if request.method == 'GET':
        return redirect(url_for('bidderMainPage'))
    global currentCategories
    currentCategories = 'Root'
    cateInfo = 'ALL'
    productListing.auctionListCreate()
    currentCateList = cate.cate_find('Root')
    searchBox = request.form['searchBox']
    promotionList = productListing.selectPromotion()
    productList = productListing.selectProductSearch(searchBox)
    return render_template('bidderMainPage.html', promotionList=promotionList, cateList=currentCateList,
                           cateInfo=cateInfo, productList=productList, currentUser=session['userId'])


@app.route('/findParent', methods=['POST', 'GET'])
def findParentCate():
    # for go back to upper level of category
    if request.method == 'GET':
        return redirect(url_for('bidderMainPage'))
    cate.cate_create()
    productListing.auctionListCreate()
    # make sure the categories is created
    global currentCategories
    try:
        currentCategories = cate.cateFindParent(currentCategories)[0]
    except:
        return redirect(url_for('bidderMainPage'))
    currentCateList = cate.cate_find(currentCategories)
    if currentCategories == 'Root':
        cateInfo = 'ALL'
    else:
        cateInfo = currentCategories
    productListing.auctionListCreate()
    productList = productListing.selectProduct(currentCategories)
    promotionList = productListing.selectPromotion()
    if request.method == 'POST':
        return render_template('bidderMainPage.html', promotionList=promotionList, cateList=currentCateList,
                               cateInfo=cateInfo, productList=productList, currentUser=session['userId'])
    elif request.method == 'GET':
        return render_template('bidderMainPage.html', promotionList=promotionList, cateList=currentCateList,
                               cateInfo=cateInfo, productList=productList, currentUser=session['userId'])


@app.route('/bidConfirm', methods=['POST', 'GET'])
def bidConfirm():
    # the back of the bidding confirm page
    if request.method == 'GET':
        # if get, show the product detail, and the seller's id
        selllerEmail = request.args.get('selllerEmail')
        listId = int(request.args.get('listId'))
        productDetail = bid.bidConfirmCatchInfo(selllerEmail, listId)
        return render_template('bidConfirm.html', currentUser=session['userId'], productDetail=productDetail)
    elif request.method == 'POST':
        newPrice = request.form['bidPrice']
        temp = bid.stringProcess(list(request.form['submitBidBtn']))
        selllerEmail = temp[0]
        listId = temp[1]
        productDetail = bid.bidConfirmCatchInfo(selllerEmail, listId)
        try:
            # check whether the price that bidder inputted is a number
            newPrice = float(newPrice)
        except:
            return render_template('bidConfirm.html', currentUser=session['userId'], productDetail=productDetail,
                                   errorMessage='Please input a number as new price .')
        if bid.findCurrentBidder(selllerEmail, listId, session['userId']):
            # find the current bidder whther is the current winner bidder
            flash("Your are the current winner bidder")
            return redirect(url_for('bidderMainPage'))
        if (newPrice - productDetail[8]) < 1:
            # find whether the new price is at least one dollar than the current price
            return render_template('bidConfirm.html', currentUser=session['userId'], productDetail=productDetail,
                                   errorMessage='Please input a new price at least $1 higher than current one.')
        else:
            if bid.lastBid(selllerEmail, listId):
                # if this is the last bid
                bid.addNoteLoser(selllerEmail, listId)
                if bid.checkSuccess(selllerEmail, listId, newPrice):
                    bid.addBidRecord(selllerEmail, listId, session['userId'], newPrice, 0)
                    return redirect(url_for('payment', selllerEmail=selllerEmail, listId=listId))
                else:
                    bid.addBidRecord(selllerEmail, listId, session['userId'], newPrice, 1)
                    bid.updateFailBid(selllerEmail, listId)

                    flash(
                        "Your bid submit successfully, But the price is less than reserved price, the bidding is closed.")
                    return redirect(url_for('bidderMainPage'))
            else:
                # if it is not the last bid
                bid.addBidRecord(selllerEmail, listId, session['userId'], newPrice, 1)
                flash("Your bid submit successfully, Please wait patiently for auction finished")
                return redirect(url_for('bidderMainPage'))


@app.route('/payment', methods=['POST', 'GET'])
def payment():
    # after the bidder input the new price
    paymentHelp.createCard()  # make sure the credit card
    selllerEmail = request.args.get('selllerEmail')
    listId = request.args.get('listId')
    if request.method == 'GET':
        cardList = paymentHelp.getCardList(session['userId'])
        return render_template('payment.html', currentUser=session['userId'], cardList=cardList,
                               selllerEmail=selllerEmail, listId=listId)
    elif request.method == 'POST':
        temp = paymentHelp.strProcess(request.form['submit_button_chooseCard'])
        cardNum = temp[0]
        listId = temp[1]
        selllerEmail = temp[2]
        return redirect(url_for('paymentConfirm', cardNum=cardNum, selllerEmail=selllerEmail, listId=listId))


@app.route('/paymentConfirm', methods=['POST', 'GET'])
def paymentConfirm():
    paymentHelp.createCard()
    cardNum = request.args.get('cardNum')
    listId = request.args.get('listId')
    selllerEmail = request.args.get('selllerEmail')
    cardList = paymentHelp.getCardList(session['userId'])
    if request.method == 'GET':
        return render_template('paymentConfirm.html', currentUser=session['userId'], cardList=cardList, cardNum=cardNum,
                               listId=listId, selllerEmail=selllerEmail)
    elif request.method == 'POST':
        cardSec = request.form['cardSec']
        temp = paymentHelp.strProcess(request.form['submit_button_submitSc'])
        cardNum = temp[0]
        listId = temp[2]
        selllerEmail = temp[1]
        dbSecCode = paymentHelp.getCardSecurityCode(cardNum)
        if int(cardSec) != dbSecCode:
            return render_template('paymentConfirm.html', currentUser=session['userId'], cardList=cardList,
                                   errorCode='Security Code incorrect', cardNum=cardNum)
        else:
            # payment successful
            # Transcation
            paymentHelp.finishPay(selllerEmail, listId, session['userId'])
            return redirect(url_for('rating', selllerEmail=selllerEmail, listId=listId))


@app.route('/rating', methods=['POST', 'GET'])
def rating():
    listId = request.args.get('listId')
    selllerEmail = request.args.get('selllerEmail')
    if request.method == 'GET':
        sucCon = ratingHelp.getInfo(selllerEmail, listId)
        return render_template('ratingTp.html', currentUser=session['userId'], proInfomation=sucCon,
                               selllerEmail=selllerEmail)
    elif request.method == 'POST':
        rate = request.form['ratingSel']
        try:
            selllerEmail = request.form['submit_button_rating']
        except:
            selllerEmail = 'error!'
        rateDes = request.form['rateDes']
        ratingHelp.createAndUpdateRates(selllerEmail, session['userId'], int(rate), rateDes)
        return redirect(url_for('bidderMainPage'))


@app.route('/sellerMainPage', methods=['GET'])
def sellerMainPage():
    cate.cate_create()
    productListing.auctionListCreate()
    # make sure the categories is created
    rate = seller.getSellerRate(session['userId'])
    productListActive = seller.getActiveProduct(session['userId'])
    promotionListActive = seller.getActivePromotion(session['userId'])
    productListSold = seller.getSoldProduct(session['userId'])
    productListInactive = seller.getInactiveProduct(session['userId'])
    currBalance = seller.getBalance(session['userId'])
    rateList = seller.getSellerRateList(session['userId'])
    return render_template('sellerMainPage.html', promotionListActive=promotionListActive, rateList=rateList, rate=rate,
                           productListActive=productListActive, productListSold=productListSold,
                           productListInactive=productListInactive, currentUser=session['userId'],
                           currBalance=currBalance)


@app.route('/editProduct', methods=['GET', 'POST'])
def editProduct():
    listId = int(request.form['submit_button_gotoEdit'])
    sellerProductDetail = seller.getProductDetail(session['userId'], listId)
    return render_template('editProduct.html', sellerProductDetail=sellerProductDetail,
                           currentUser=session['userId'])


@app.route('/addPromotion', methods=['GET', 'POST'])
def addPromotion():
    listId = int(request.form['submit_button_gotoEdit'])
    if not seller.checkPromotion(session['userId'], listId):

        if seller.checkMoneyPro(session['userId'], listId):
            if seller.addPromotion(session['userId'], listId):
                flash("Congratulations! Your Product already in promotion now!")
                return redirect(url_for('sellerMainPage'))
            else:
                flash("Sorry! Your Product is not in promotion because the promotion list is full now!")
                return redirect(url_for('sellerMainPage'))
        else:
            flash("Sorry! Your balance is not enough for this promotion!")
            return redirect(url_for('sellerMainPage'))
    else:
        flash("Do not promote a product repeatedly!")
        return redirect(url_for('sellerMainPage'))


@app.route('/editProductConfirm', methods=['POST', 'GET'])
def editProductConfirm():
    ListingID = request.form['submit_button_edit']
    Auction_Title = request.form['Auction_Title']
    Product_Name = request.form['Product_Name']
    Product_Description = request.form['Product_Description']
    Quantity = request.form['Quantity']
    try:
        Quantity = int(Quantity)
        Reserve_Price = float(request.form['Reserve_Price'])
        Max_bids = int(request.form['Max_bids'])
        Status = int(request.form['Status'])
    except:
        flash("Update fail! Check the new information you input!")
        return redirect(url_for('sellerMainPage'))
    leaveReason = request.form['leaveReason']
    if not seller.updateProduct(session['userId'], ListingID, Auction_Title, Product_Name, Product_Description,
                                Quantity, Reserve_Price, Max_bids, Status, leaveReason):
        flash("Update fail! Check the new information you input!")
        return redirect(url_for('sellerMainPage'))
    else:
        flash("Congratulations! Your Product update successfully!")
        return redirect(url_for('sellerMainPage'))


@app.route('/changeCate', methods=['POST'])
def changeCate():
    listId = int(request.form['changeCateButton'])
    sellerProductDetail = seller.getProductDetail(session['userId'], listId)
    currentCateEdit = 'Root'
    cateList = cate.cate_find(currentCateEdit)
    return render_template('productChangeCate.html', sellerProductDetail=sellerProductDetail,
                           currentUser=session['userId'], cateList=cateList, currCate='ALL')


@app.route('/categoryGo', methods=['POST', 'GET'])
def categoryGo():
    listId = int(request.form['categoryGoChange'])
    sellerProductDetail = seller.getProductDetail(session['userId'], listId)
    select = request.form.get('comp_select_edit')
    cateList = cate.cate_find(str(select))
    return render_template('productChangeCate.html', sellerProductDetail=sellerProductDetail,
                           currentUser=session['userId'], cateList=cateList, currCate=str(select))


@app.route('/categoryEditBack', methods=['POST', 'GET'])
def categoryEditBack():
    listId = int(request.form['categoryBackChange'])
    currCate = request.args.get('currCate')
    sellerProductDetail = seller.getProductDetail(session['userId'], listId)
    try:
        parentCate = cate.cateFindParent(currCate)[0]
    except:
        parentCate = 'Root'
    cateList = cate.cate_find(parentCate)
    if parentCate == 'Root':
        parentCate = 'ALL'
    return render_template('productChangeCate.html', sellerProductDetail=sellerProductDetail,
                           currentUser=session['userId'], cateList=cateList, currCate=parentCate)


@app.route('/categorySubmitChange', methods=['POST', 'GET'])
def categorySubmitChange():
    listId = int(request.form['categorySubmitChange'])
    select = request.args.get('currCate')

    if str(select) == 'ALL' or str(select) == 'Root':
        flash("Update fail! The category cannot be ALL!")
        return redirect(url_for('sellerMainPage'))
    else:
        if seller.updateProductCate(session['userId'], listId, str(select)):
            flash("Congratulations! Your Product update successfully!")
            return redirect(url_for('sellerMainPage'))
        else:
            flash("Update fail! Check the new information you input!")
            return redirect(url_for('sellerMainPage'))


@app.route('/addNewProduct', methods=['POST', 'GET'])
def addNewProduct():
    if request.method == 'GET':
        currCate = 'Root'
        cateList = cate.cate_find(currCate)
        return render_template('addNewProduct.html', currentUser=session['userId'], cateList=cateList, currCate='ALL')
    elif request.method == 'POST':
        cateGory = request.args.get('currCate')
        if cateGory == 'ALL':
            cateGory = 'Root'
        Auction_Title = request.form['Auction_Title']
        Product_Name = request.form['Product_Name']
        Product_Description = request.form['Product_Description']
        Quantity = request.form['Quantity']
        Reserve_Price = request.form['Reserve_Price']
        Max_bids = request.form['Max_bids']
        cateList = cate.cate_find(str(cateGory))
        errorQuan = ''
        errorResPrice = ''
        errorMaxBid = ''
        if cateGory == 'Root':
            return render_template('addNewProduct.html', currentUser=session['userId'], cateList=cateList,
                                   currCate=cateGory,
                                   Auction_Title=Auction_Title, Product_Name=Product_Name,
                                   Product_Description=Product_Description, Quantity=Quantity,
                                   Reserve_Price=Reserve_Price,
                                   Max_bids=Max_bids, errorQuan=errorQuan, errorResPrice=errorResPrice,
                                   errorMaxBid=errorMaxBid, errorCate='Category cannot be ALL')
        try:
            Quantity = int(Quantity)
        except:
            errorQuan = 'Quantity have to be a number'
        try:
            Reserve_Price = float(Reserve_Price)
        except:
            errorResPrice = 'Reserve Price have to be a number'
        try:
            Max_bids = int(Max_bids)
        except:
            errorMaxBid = 'Max bids have to be a number'
            return render_template('addNewProduct.html', currentUser=session['userId'], cateList=cateList,
                                   currCate=cateGory,
                                   Auction_Title=Auction_Title, Product_Name=Product_Name,
                                   Product_Description=Product_Description, Quantity=Quantity,
                                   Reserve_Price=Reserve_Price,
                                   Max_bids=Max_bids, errorQuan=errorQuan, errorResPrice=errorResPrice,
                                   errorMaxBid=errorMaxBid)
        if errorQuan != '' or errorResPrice != '':
            return render_template('addNewProduct.html', currentUser=session['userId'], cateList=cateList,
                                   currCate=cateGory,
                                   Auction_Title=Auction_Title, Product_Name=Product_Name,
                                   Product_Description=Product_Description, Quantity=Quantity,
                                   Reserve_Price=Reserve_Price,
                                   Max_bids=Max_bids, errorQuan=errorQuan, errorResPrice=errorResPrice,
                                   errorMaxBid=errorMaxBid)
        seller.addProduct(session['userId'], cateGory, Auction_Title, Product_Name, Product_Description, Quantity,
                          Reserve_Price, Max_bids)
        return redirect(url_for('sellerMainPage'))


@app.route('/addNewProductCateGo', methods=['POST'])
def addNewProductCateGo():
    cateGory = request.form.get('comp_select_add')
    Auction_Title = request.form['Auction_Title']
    Product_Name = request.form['Product_Name']
    Product_Description = request.form['Product_Description']
    Quantity = request.form['Quantity']
    Reserve_Price = request.form['Reserve_Price']
    Max_bids = request.form['Max_bids']
    cateList = cate.cate_find(str(cateGory))
    if str(cateGory) == 'Root':
        cateGory = 'ALL'
    return render_template('addNewProduct.html', currentUser=session['userId'], cateList=cateList, currCate=cateGory,
                           Auction_Title=Auction_Title, Product_Name=Product_Name,
                           Product_Description=Product_Description, Quantity=Quantity, Reserve_Price=Reserve_Price,
                           Max_bids=Max_bids)


@app.route('/addNewProductCateGoBack', methods=['POST'])
def addNewProductCateGoBack():
    cateGory = request.args.get('currCate')
    Auction_Title = request.form['Auction_Title']
    Product_Name = request.form['Product_Name']
    Product_Description = request.form['Product_Description']
    Quantity = request.form['Quantity']
    Reserve_Price = request.form['Reserve_Price']
    Max_bids = request.form['Max_bids']
    if cateGory == 'ALL':
        cateGory = 'Root'

    parentCate = cate.cateFindParent(cateGory)[0]
    cateList = cate.cate_find(parentCate)
    if parentCate == 'Root':
        parentCate = 'ALL'
    return render_template('addNewProduct.html', currentUser=session['userId'], cateList=cateList, currCate=parentCate,
                           Auction_Title=Auction_Title, Product_Name=Product_Name,
                           Product_Description=Product_Description, Quantity=Quantity, Reserve_Price=Reserve_Price,
                           Max_bids=Max_bids)


@app.route('/editProfile', methods=['POST', 'GET'])
def editProfile():
    if request.method == 'GET':
        if session['userType'] == 'Bidder':
            # bidder edit profile
            bidderMessage = editProfileHelp.getBidderMessage(session['userId'])
            errorAge = ''
            errorPassword = ''
            return render_template('editProfileBidder.html', currentUser=session['userId'], bidderMessage=bidderMessage,
                                   errorPassword=errorPassword, errorAge=errorAge)
        elif session['userType'] == 'Seller':
            sellerMessage = editProfileHelp.getSellerMessage(session['userId'])
            if editProfileHelp.getLocalVendorMessage(session['userId']):
                vendorMessage = editProfileHelp.getLocalVendorMessage(session['userId'])
                return render_template('editProfileSeller.html', currentUser=session['userId'],
                                       sellerMessage=sellerMessage, vendorMessage=vendorMessage,
                                       localVendorBool=True)
            else:
                return render_template('editProfileSeller.html', currentUser=session['userId'],
                                       sellerMessage=sellerMessage,
                                       localVendorBool=False)
    elif request.method == 'POST':
        if session['userType'] == 'Bidder':
            errorAge = ''
            errorPassword = ''
            UpdatePass = None
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            gender = request.form['gender']
            age = request.form['age']
            major = request.form['major']
            home_address_id = request.form['submit_button_edit_profile']

            UpPassBool = request.args.get('op')
            if UpPassBool == '1':
                bidderMessage = [(session['userId'], first_name, last_name, gender, age, home_address_id, major)]
                return render_template('editProfileBidder.html', UpdatePass=1, currentUser=session['userId'],
                                       bidderMessage=bidderMessage, errorPassword=errorPassword, errorAge=errorAge)
            try:
                editPassword = request.form['editPassword']
                confirmPassword = request.form['confirmPassword']
                if editPassword != confirmPassword:
                    errorPassword = 'Your password not match'
                    UpdatePass = 1
            except:
                editPassword = False

            try:
                age = int(age)
            except:
                errorAge = 'Age have to be a number.'
            if errorAge != '' or errorPassword != '':
                bidderMessage = [(session['userId'], first_name, last_name, gender, age, home_address_id, major)]
                return render_template('editProfileBidder.html', UpdatePass=UpdatePass, currentUser=session['userId'],
                                       bidderMessage=bidderMessage, errorPassword=errorPassword, errorAge=errorAge)
            if not editPassword == False:
                # if need update password
                editProfileHelp.updatePassword(session['userId'], editPassword)
            editProfileHelp.updateBidder(session['userId'], first_name, last_name, gender, age, major)
            flash('Congratulations! Your profile update successfully!')
            return redirect(url_for('bidderMainPage'))

        elif session['userType'] == 'Seller':
            flashBool = False
            vendorBool = True
            try:
                Business_Name = request.form['Business_Name']
                Customer_Service_Phone_Number = request.form['Customer_Service_Phone_Number']
            except:
                vendorBool = False
            bank_routing_number = request.form['bank_routing_number']
            bank_account_number = request.form['bank_account_number']
            try:
                temp = bank_account_number
                bank_account_number = int(bank_account_number)
                bank_account_number = temp
            except:
                flashBool = True
            if bank_routing_number.count('-') != 2:
                flashBool = True
            else:
                carNum = bank_routing_number.split("-")
                carNum0 = carNum[0]
                carNum1 = carNum[1]
                carNum2 = carNum[2]
                try:
                    temp_carNum0 = carNum0
                    carNum0 = int(carNum0)
                    carNum0 = carNum0

                    temp_carNum1 = carNum1
                    carNum1 = int(carNum1)
                    carNum1 = carNum1

                    temp_carNum2 = carNum2
                    carNum2 = int(carNum2)
                    carNum2 = carNum2
                except:
                    flashBool = True
            if vendorBool:
                if Customer_Service_Phone_Number.count('-') != 2:
                    flashBool = True
                else:
                    carNum = Customer_Service_Phone_Number.split("-")
                    carNum0 = carNum[0]
                    carNum1 = carNum[1]
                    carNum2 = carNum[2]
                    try:
                        temp_carNum0 = carNum0
                        carNum0 = int(carNum0)
                        carNum0 = carNum0

                        temp_carNum1 = carNum1
                        carNum1 = int(carNum1)
                        carNum1 = carNum1

                        temp_carNum2 = carNum2
                        carNum2 = int(carNum2)
                        carNum2 = carNum2
                    except:
                        flashBool = True
        if flashBool:
            flash('Please Check your information')
            if editProfileHelp.getLocalVendorMessage(session['userId']):
                sellerMessage = [(session['userId'], bank_routing_number, bank_account_number, 1, 1)]
                vendorMessage = [(session['userId'], Business_Name, 1, Customer_Service_Phone_Number)]
                return render_template('editProfileSeller.html', currentUser=session['userId'],
                                       sellerMessage=sellerMessage, vendorMessage=vendorMessage,
                                       localVendorBool=True)
            else:
                sellerMessage = [(session['userId'], bank_routing_number, bank_account_number, 1, 1)]
                return render_template('editProfileSeller.html', currentUser=session['userId'],
                                       sellerMessage=sellerMessage,
                                       localVendorBool=False)
        else:
            flash('Congratulations! Your profile update successfully!')
            editProfileHelp.updateSeller(session['userId'], bank_routing_number, bank_account_number)
            if editProfileHelp.getLocalVendorMessage(session['userId']):
                editProfileHelp.updateVendor(session['userId'], Business_Name, Customer_Service_Phone_Number)

            return redirect(url_for('bidderMainPage'))


@app.route('/editProfileBidderAddress', methods=['POST', 'GET'])
def editProfileBidderAddress():
    if request.method == 'GET':
        if session['userType'] == 'Bidder':
            addressMessage = editProfileHelp.getBidderAddressMessage(session['userId'])
            return render_template('editProfileBidderAddress.html', currentUser=session['userId'],
                                   addressMessage=addressMessage, zipBool=None)
        elif session['userType'] == 'Seller':
            addressMessage = editProfileHelp.getSellerAddressMessage(session['userId'])
            return render_template('editProfileBidderAddress.html', currentUser=session['userId'],
                                   addressMessage=addressMessage, zipBool=None)
    elif request.method == 'POST':
        if session['userType'] == 'Bidder':
            errorStreetNum = ''
            errorZip = ''
            street_num = request.form['street_num']
            street_name = request.form['street_name']
            zipcode = request.form['zipcode']
            address_id = request.form['submit_button_edit_profile_address']
            try:
                city = request.form['city']
                state = request.form['state']
            except:
                city = None
                state = None
            try:
                street_num = int(street_num)
            except:
                errorStreetNum = 'Street Number have to be a number.'
            try:
                temp = zipcode
                zipcode = int(zipcode)
                zipcode = temp
            except:
                errorZip = 'Zipcode have to be a number.'
            if errorStreetNum != '' or errorZip != '':
                addressMessage = [(address_id, zipcode, street_num, street_name)]
                return render_template('editProfileBidderAddress.html', currentUser=session['userId'],
                                       addressMessage=addressMessage, zipBool=None, errorStreetNum=errorStreetNum,
                                       errorZip=errorZip)
            if not editProfileHelp.checkZip(zipcode):
                if not city:
                    addressMessage = [(address_id, zipcode, street_num, street_name)]
                    return render_template('editProfileBidderAddress.html', currentUser=session['userId'],
                                           addressMessage=addressMessage, zipBool=True)
                else:

                    editProfileHelp.updateZip(zipcode, city, state)
                    editProfileHelp.updateBidderAddress(session['userId'], zipcode, street_num, street_name)
                    flash('Congratulations! Your Address update successfully!')
                    return redirect(url_for('bidderMainPage'))
            else:
                editProfileHelp.updateBidderAddress(session['userId'], zipcode, street_num, street_name)
                flash('Congratulations! Your Address update successfully!')
                return redirect(url_for('bidderMainPage'))
        if session['userType'] == 'Seller':
            errorStreetNum = ''
            errorZip = ''
            street_num = request.form['street_num']
            street_name = request.form['street_name']
            zipcode = request.form['zipcode']
            address_id = request.form['submit_button_edit_profile_address']
            try:
                city = request.form['city']
                state = request.form['state']
            except:
                city = None
                state = None
            try:
                street_num = int(street_num)
            except:
                errorStreetNum = 'Street Number have to be a number.'
            try:
                temp = zipcode
                zipcode = int(zipcode)
                zipcode = temp
            except:
                errorZip = 'Zipcode have to be a number.'
            if errorStreetNum != '' or errorZip != '':
                addressMessage = [(address_id, zipcode, street_num, street_name)]
                return render_template('editProfileBidderAddress.html', currentUser=session['userId'],
                                       addressMessage=addressMessage, zipBool=None, errorStreetNum=errorStreetNum,
                                       errorZip=errorZip)
            if not editProfileHelp.checkZip(zipcode):
                if not city:
                    addressMessage = [(address_id, zipcode, street_num, street_name)]
                    return render_template('editProfileBidderAddress.html', currentUser=session['userId'],
                                           addressMessage=addressMessage, zipBool=True)
                else:

                    editProfileHelp.updateZip(zipcode, city, state)
                    editProfileHelp.updateSellerAddress(session['userId'], zipcode, street_num, street_name)
                    flash('Congratulations! Your Address update successfully!')
                    return redirect(url_for('sellerMainPage'))
            else:
                editProfileHelp.updateSellerAddress(session['userId'], zipcode, street_num, street_name)
                flash('Congratulations! Your Address update successfully!')
                return redirect(url_for('sellerMainPage'))


@app.route('/editProfileBidderCards', methods=['POST', 'GET'])
def editProfileBidderCards():
    if request.method == 'GET':
        if session['userType'] == 'Bidder':
            cardMessage = editProfileHelp.getCardMessage(session['userId'])
            carNum = cardMessage[0][0]
            carNum = carNum.split("-")
            carNum0 = carNum[0]
            carNum1 = carNum[1]
            carNum2 = carNum[2]
            carNum3 = carNum[3]
            return render_template('editProfileBIdderCards.html', currentUser=session['userId'],
                                   cardMessage=cardMessage, carNum0=carNum0, carNum1=carNum1, carNum2=carNum2,
                                   carNum3=carNum3)
    elif request.method == 'POST':
        if session['userType'] == 'Bidder':
            errorCardNum = ''
            flashWords = False
            credit_card_num = request.form['credit_card_num']
            card_type = request.form['card_type']
            expire_month = request.form['expire_month']
            expire_year = request.form['expire_year']
            security_code = request.form['security_code']
            try:
                temp_security_code = security_code
                security_code = int(security_code)
                security_code = temp_security_code
                expire_year = int(expire_year)
                expire_month = int(expire_month)
            except:
                flashWords = True

            if credit_card_num.count('-') != 3:
                errorCardNum = 'Check your new credit card number'
            else:
                carNum = credit_card_num.split("-")
                carNum0 = carNum[0]
                carNum1 = carNum[1]
                carNum2 = carNum[2]
                carNum3 = carNum[3]
                try:
                    temp_carNum0 = carNum0
                    carNum0 = int(carNum0)
                    carNum0 = carNum0

                    temp_carNum1 = carNum1
                    carNum1 = int(carNum1)
                    carNum1 = carNum1

                    temp_carNum2 = carNum2
                    carNum2 = int(carNum2)
                    carNum2 = carNum2

                    temp_carNum3 = carNum3
                    carNum3 = int(carNum3)
                    carNum3 = carNum3
                except:
                    errorCardNum = 'Check your new credit card number'

            if errorCardNum != '' or flashWords != False:
                cardMessage = [
                    (credit_card_num, card_type, expire_month, expire_year, security_code, session['userId'])]
                flash('Check Your new credit card information!')
                return render_template('editProfileBIdderCards.html', currentUser=session['userId'],
                                       cardMessage=cardMessage, errorCardNum=errorCardNum)
            else:
                editProfileHelp.updateCard(credit_card_num, card_type, expire_month, expire_year, security_code,
                                           session['userId'])
                flash('Congratulations! Your Credit Card update successfully!')
                return redirect(url_for('bidderMainPage'))


@app.route('/editProfileSellerPass', methods=['POST', 'GET'])
def editProfileSellerPass():
    if request.method == 'GET':
        return render_template('editSellerPass.html', currentUser=session['userId'])
    elif request.method == 'POST':
        password = request.form['password']
        passwordConfirm = request.form['passwordConfirm']
        if password == passwordConfirm:
            editProfileHelp.updatePassword(session['userId'], password)
            flash('Your password update successfully!')
            return redirect(url_for('sellerMainPage'))
        else:
            error = 'Password and Confirm Password are not match.'
            return render_template('editSellerPass.html', error=error)


@app.route('/bidderSign', methods=['POST', 'GET'])
def bidderSign():
    if request.method == 'GET':
        return render_template('bidderSign.html')
    elif request.method == 'POST':
        errorAge = ''
        errorPassword = ''
        userId = request.form['userId']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        age = request.form['age']
        major = request.form['major']

        editPassword = request.form['editPassword']
        confirmPassword = request.form['confirmPassword']

        errorCardNum = ''
        errorMonth = ''
        errorYear = ''
        errorSC = ''
        credit_card_num = request.form['credit_card_num']
        card_type = request.form['card_type']
        expire_month = request.form['expire_month']
        expire_year = request.form['expire_year']
        security_code = request.form['security_code']

        errorStreetNum = ''
        errorZip = ''
        street_num = request.form['street_num']
        street_name = request.form['street_name']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']

        if editPassword != confirmPassword:
            errorPassword = 'Your password not match'
        try:
            age = int(age)
        except:
            errorAge = 'Age have to be a number.'

        try:
            street_num = int(street_num)
        except:
            errorStreetNum = 'Street Number have to be a number.'
        try:
            temp = zipcode
            zipcode = int(zipcode)
            zipcode = temp
        except:
            errorZip = 'Zipcode have to be a number.'

        if not editProfileHelp.checkZip(zipcode) and errorZip == '':
            # check whether the zipcode exist in database
            editProfileHelp.updateZip(zipcode, city, state)

        try:
            temp_security_code = security_code
            security_code = int(security_code)
            security_code = temp_security_code
        except:
            errorSC = 'Check your security code'

        try:
            expire_year = int(expire_year)
        except:
            errorYear = 'Expire year have to be a number '

        try:
            expire_month = int(expire_month)
        except:
            errorMonth = 'Expire month have to be a number'

        if credit_card_num.count('-') != 3:
            errorCardNum = 'Check your new credit card number'
        else:
            carNum = credit_card_num.split("-")
            carNum0 = carNum[0]
            carNum1 = carNum[1]
            carNum2 = carNum[2]
            carNum3 = carNum[3]
            try:
                temp_carNum0 = carNum0
                carNum0 = int(carNum0)
                carNum0 = carNum0

                temp_carNum1 = carNum1
                carNum1 = int(carNum1)
                carNum1 = carNum1

                temp_carNum2 = carNum2
                carNum2 = int(carNum2)
                carNum2 = carNum2

                temp_carNum3 = carNum3
                carNum3 = int(carNum3)
                carNum3 = carNum3
            except:
                errorCardNum = 'Check your new credit card number'

        if errorAge != '' or errorPassword != '' or errorCardNum != '' or errorMonth != '' or errorYear != '' or errorSC != '' or errorStreetNum != '' or errorZip != '':
            return render_template('bidderSign.html'
                                   , errorAge=errorAge
                                   , errorPassword=errorPassword
                                   , userId=userId
                                   , first_name=first_name
                                   , last_name=last_name
                                   , gender=gender
                                   , age=age
                                   , major=major
                                   , editPassword=editPassword
                                   , confirmPassword=confirmPassword
                                   , errorCardNum=errorCardNum
                                   , errorMonth=errorMonth
                                   , errorYear=errorYear
                                   , errorSC=errorSC
                                   , credit_card_num=credit_card_num
                                   , card_type=card_type
                                   , expire_month=expire_month
                                   , expire_year=expire_year
                                   , security_code=security_code
                                   , errorStreetNum=errorStreetNum
                                   , errorZip=errorZip
                                   , street_num=street_num
                                   , street_name=street_name
                                   , zipcode=zipcode
                                   , city=city
                                   , state=state
                                   )
        else:
            login.createAccountBidder(userId
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
                                      , zipcode)
            flash('Your account create successfully!')
            return redirect(url_for('loginBidder'))


@app.route('/sellerSign', methods=['POST', 'GET'])
def sellerSign():
    if request.method == 'GET':
        return render_template('sellerSign.html')
    elif request.method == 'POST':
        errorPassword = ''
        userId = request.form['userId']
        editPassword = request.form['editPassword']
        confirmPassword = request.form['confirmPassword']
        if editPassword != confirmPassword:
            errorPassword = 'Your password not match'
        bank_routing_number = request.form['bank_routing_number']
        bank_account_number = request.form['bank_account_number']
        errorRout = ''
        errorAccountNum = ''
        try:
            temp = bank_account_number
            bank_account_number = int(bank_account_number)
            bank_account_number = temp
        except:
            errorAccountNum = 'Please check your back account number'

        if bank_routing_number.count('-') != 2:
            errorRout = 'Please check your back routing number'
        else:
            carNum = bank_routing_number.split("-")
            carNum0 = carNum[0]
            carNum1 = carNum[1]
            carNum2 = carNum[2]
            try:
                temp_carNum0 = carNum0
                carNum0 = int(carNum0)
                carNum0 = carNum0

                temp_carNum1 = carNum1
                carNum1 = int(carNum1)
                carNum1 = carNum1

                temp_carNum2 = carNum2
                carNum2 = int(carNum2)
                carNum2 = carNum2
            except:
                errorRout = 'Please check your back routing number'
        if errorRout != '' or errorPassword != '' or errorAccountNum != '':
            return render_template('sellerSign.html', bank_routing_number=bank_routing_number,
                                   bank_account_number=bank_account_number, userId=userId, errorPassword=errorPassword,
                                   errorAccountNum=errorAccountNum, errorRout=errorRout)
        else:
            login.createAccountSeller(userId
                                      , editPassword
                                      , bank_account_number
                                      , bank_routing_number)
            flash('Your account create successfully!')
            return redirect(url_for('loginSeller'))


@app.route('/requestGenerate', methods=['POST', 'GET'])
def requestGenerate():
    if request.method == 'GET':
        if session['userType'] == 'Bidder':
            mainPageUrl = 'bidderMainPage'
        else:
            mainPageUrl = 'sellerMainPage'
        return render_template('requestGenerate.html', currentUser=session['userId'], mainPageUrl=mainPageUrl)
    elif request.method == 'POST':
        request_type = request.form['request_type']
        request_desc = request.form['request_desc']
        HelpDesk.addReq(session['userId'], request_type, request_desc)
        flash('Congratulations! Your request have already been submitted. Please wait for processing!')
        if session['userType'] == 'Bidder':
            mainPageUrl = 'bidderMainPage'
        else:
            mainPageUrl = 'sellerMainPage'
        return redirect(url_for(mainPageUrl))


if __name__ == "__main__":
    app.run()
