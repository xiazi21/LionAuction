import sqlite3 as sql
import pandas as pd

# this is the file for category processing

cateBool = 0


def cate_create():
    cateCreateHelp()
    global cateBool
    cateBool = 1


def cateCreateHelp():
    if cateBool == 0:
        connection = sql.connect('database.db')
        connection.execute('CREATE TABLE IF NOT EXISTS Categories('
                           'parent_category TEXT , category_name TEXT PRIMARY KEY NOT NULL);')
        contents = pd.read_csv('Categories.csv', engine='python')
        for row in contents.iterrows():
            connection.execute('INSERT OR IGNORE INTO Categories (parent_category,category_name) VALUES(?, ?)',
                               (row[1].parent_category, row[1].category_name))
        connection.commit()  # submit change in database


def cate_find(parent):
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT category_name FROM Categories WHERE parent_category = ?;', (parent,))
    result = cursor.fetchall()
    for i in range(len(result)):
        result[i] = result[i][0]
    if not result:
        result = [parent]
        # result = cate_find(result[0])
        # result = changeCateOrder(result, parent)
    return result


def cateFindParent(children):
    if children == 'Root':
        return [children]
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT parent_category FROM Categories WHERE category_name = ?;', (children,))
    result = cursor.fetchall()
    for i in range(len(result)):
        result[i] = result[i][0]
    return result


def changeCateOrder(listTarget, listHead):
    listTarget.remove(listHead)
    listTarget.insert(0, listHead)
    return listTarget
