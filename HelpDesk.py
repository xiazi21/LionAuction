import sqlite3 as sql

def getUnassignList():
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM requests WHERE request_status = ? AND helpdesk_staff_email = ?;', (0,'helpdeskteam@lsu.edu'))
    result = cursor.fetchall()
    return result
def getAssignList():
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM requests WHERE request_status = ? AND helpdesk_staff_email <> ?;', (0, 'helpdeskteam@lsu.edu'))
    result = cursor.fetchall()
    return result

def getCompletedList():
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM requests WHERE request_status = ?;', (1,))
    result = cursor.fetchall()
    return result


def getStaffList():
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM HelpDesk WHERE userId <> "helpdeskteam@lsu.edu";')
    result = cursor.fetchall()
    return result

def assignStaff(request_id,comp_select_staff):
    connection = sql.connect('database.db')
    try:
        connection.execute('UPDATE requests '
                           'SET helpdesk_staff_email=?'
                           'WHERE request_id = ?;',
                           (comp_select_staff,request_id))
        connection.commit()
    except:
        return False
    return True

def getTodoList(userId):
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT * '
        'FROM requests WHERE request_status = ? AND helpdesk_staff_email = ?;', (0, userId))
    result = cursor.fetchall()
    return result

def updateStatusReq(request_id):
    connection = sql.connect('database.db')
    connection.execute('UPDATE requests '
                       'SET request_status=?'
                       'WHERE request_id = ?;',
                       (1, request_id))
    connection.commit()

def addNewCate(parentCate,cateName):
    connection = sql.connect('database.db')
    connection.execute('INSERT OR IGNORE INTO Categories (parent_category,category_name) VALUES(?, ?)',
                       (parentCate, cateName))
    connection.commit()

def addReq(sender_email,request_type,request_desc):
    connection = sql.connect('database.db')
    connection.execute(
        'INSERT OR IGNORE INTO requests (sender_email,helpdesk_staff_email,request_type,request_desc,request_status) VALUES(?,?,?,?,?)',
        (sender_email, 'helpdeskteam@lsu.edu', request_type, request_desc, 0))
    connection.commit()