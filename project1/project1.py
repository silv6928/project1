#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import urllib.request
import sqlite3
import re
import os
import random

# Links to Text
links = {"Magna Carta": "http://www.thelatinlibrary.com/magnacarta.html",
         "Creeds": "http://www.thelatinlibrary.com/creeds.html",
         "Roman Epitaphs": "http://www.thelatinlibrary.com/epitaphs.html",
         "Augustine": "http://www.thelatinlibrary.com/august.html",
         "Novatian": "http://www.thelatinlibrary.com/novatian.html",
         "Alfonsi": "http://www.thelatinlibrary.com/alfonsi.disciplina.html"}


# create the database to store the text
def createdb():
    # creates a connection to a db
    # if the db isn't already created it will create a new one.
    try:
        conn = sqlite3.connect('project1.db')
        conn.execute('''CREATE TABLE latinText
        (title TEXT, book TEXT, language TEXT, author TEXT, dates TEXT, chapter TEXT, verse TEXT, passage TEXT, link TEXT)''')
        conn.commit()
        conn.close()
        return
    except:
        print("latinText table already exists")
        return


# Will get the Magna Carta from the Latin Library
# Assume there is 1 chapter in the document. Each new paragraph is a "verse"
def getMagnaCarta():
    global links
    verses = []
    schema = []
    link = links["Magna Carta"]
    req = urllib.request.urlopen(link).read().decode('utf-8', "replace")
    s = BeautifulSoup(req, 'html.parser')
    title = s.title.text.strip()
    author = "John, King of England"
    dates = "1215"
    chapter = "1"
    doc = str(s.get_text())
    for i in doc.splitlines():
        if re.search(r'The', i) or re.search(r'Transcribed', i) or re.search(r'Medieval Latin', i):
            continue
        if i == '':
            continue
        else:
            verses.append(i)
    verses = verses[3:]
    j = 0
    for i in verses:
        j += 1
        inserts = [title, '', "LATIN", author, dates, chapter, str(j), i, link]
        schema.append(inserts)
    return schema


# Insert the Magna Carta data into the database.
# Takes the list generated from getMagnaCarta() and executes many into the database
def insertMagnaCarta():
    conn = sqlite3.connect('project1.db')
    data = getMagnaCarta()
    conn.executemany('''INSERT INTO latinText(title, book, language, author, dates, chapter, verse, passage, link)
    VALUES(?,?,?,?,?,?,?,?,?)''', data)
    conn.commit()
    conn.close()


# Test of the database.
def testSelect():
    conn = sqlite3.connect('project1.db')
    cursor = conn.cursor()
    cursor.execute('''select * from latinText where title = 'Early Christian Creeds' ''')
    print(cursor.fetchall())
    conn.close()


# Get the data from the Early Christian Creeds and insert it into a list.
# Assume a new creed is a new book, only 1 chapter for each book, and each new line given
# from the HTML is a new verse.
def getCreeds():
    global links
    verses = []
    schema = []
    books = []
    link = links["Creeds"]
    req = urllib.request.urlopen(link).read().decode('utf-8', "replace")
    s = BeautifulSoup(req, 'html.parser')
    title = s.title.text.strip()
    chapter = "1"
    author = ""
    dates = ""

    # Get the names of the "books" for the Creeds
    bookName = s.find_all("p", class_="pagehead")
    for i in bookName:
        books.append(i.text.replace('\n', ''))
    doc = str(s.get_text())
    j = 0
    verse = 0
    for i in doc.splitlines():
        if re.search(r'The', i) or re.search(r'Christian', i) or re.search(r'\t', i):
            continue
        if i in books:
            j = i
            verse = 1
            continue
        if i == '':
            continue
        else:
            inserts = [title, j, "LATIN", author, dates, chapter, str(verse), i, link]
            schema.append(inserts)
            verse += 1
    return schema


# Insert Creeds data into the database
# Takes a list of the data provided from the Creeds text and inserts it into the database
def insertCreeds():
    conn = sqlite3.connect('project1.db')
    data = getCreeds()
    conn.executemany('''INSERT INTO latinText(title, book, language, author, dates, chapter, verse, passage, link)
    VALUES(?,?,?,?,?,?,?,?,?)''', data)
    conn.commit()
    conn.close()


