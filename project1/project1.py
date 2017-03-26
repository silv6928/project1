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

'''
Base Functions.
'''
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


# Test of the database.
def testSelect():
    conn = sqlite3.connect('project1.db')
    cursor = conn.cursor()
    cursor.execute('''select * from latinText; ''')
    print(cursor.fetchall())
    conn.close()

'''
Data Capturing from HTML scraping.


'''

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


# Get the data from the Early Christian Creeds and insert it into a list.
# Assume a new creed is a new book, only 1 chapter for each book, and each new line given
# from the HTML is a new verse.
def getCreeds():
    global links
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


# Gets the Roman Epitaphs data from the HTML
# Assume "B" is a book, the number next to it is the chapter
# and a new line is the verse of the chapter.
def getRomanEps():
    global links
    schema = []
    link = links["Roman Epitaphs"]
    req = urllib.request.urlopen(link).read().decode('utf-8', "replace")
    s = BeautifulSoup(req, 'html.parser')
    title = s.title.text.strip()
    author = ""  # unknown
    dates = ""   # unknown
    verse = 1
    chapter = ""
    doc = str(s.get_text())
    for i in doc.splitlines():
        if re.search(r'The', i) or re.search(r'Christian', i) or re.search(r'\t', i) or re.search(r'ROMAN', i):
            continue
        if re.search(r'B', i):
            book = "B"
            verse = 1
            m = re.match(r'(B)\s(.*)', i)
            if m:
                chapter = m.group(2)
            continue
        if re.search(r'CIL', i):
            book = "CIL"
            verse = 1
            m = re.match(r'(CIL)\s(.*)', i)
            if m:
                chapter = m.group(2)
            continue
        if i == '':
            continue
        else:
            insert = [title, book, "LATIN", author, dates, chapter, str(verse), i, link]
            schema.append(insert)
            verse += 1
    return schema


# Insert the Epitaph data into the database
def insertEpitaphs():
    conn = sqlite3.connect('project1.db')
    data = getRomanEps()
    conn.executemany('''INSERT INTO latinText(title, book, language, author, dates, chapter, verse, passage, link)
    VALUES(?,?,?,?,?,?,?,?,?)''', data)
    conn.commit()
    conn.close()


# Get the Augustine data from Latin Library
def getAugustine():
    global links
    schema = []
    link = links["Augustine"]
    req = urllib.request.urlopen(link).read().decode('utf-8', "replace")
    s = BeautifulSoup(req, 'html.parser')
    title = "AUGUSTINE OF HIPPO"
    author = s.title.text.strip()
    dates = "354-430 A.D."
    prefix = "http://www.thelatinlibrary.com/"
    book = ""
    bookNum = 1
    chapter = ""
    verse = ""
    verseNum = ""
    tables = s.find_all('table', class_="")
    for i in tables:
        print(i.text)
        if re.search(r'CONFESS', i.text) or re.search(r'DE CIVITATE', i.text):
            text = i.text.replace('\n', '')
            title = text
            bookNum = 1
            continue
        if i.text == "" or re.search(r'Christian|The|de|SERMONES|Regula|CONTRA|DE TRINITATE|IULIANI', i.text):
            continue
        textLink = i.find_all("a")
        for j in textLink:
            total = prefix + j.get("href")
            t = urllib.request.urlopen(total).read().decode('utf-8', "replace")
            s2 = BeautifulSoup(t, 'html.parser')
            doc = s2.get_text()
            for z in doc.splitlines():
                if re.search(r'The|Augustine|AUGUSTINI|commentary|LIBER|PROLOG', z) or re.search(r'Christian', z) or re.search(r'\t', z) or re.search(r'ROMAN', z):
                    continue
                if z == '' or z == ' ' or z == '<' or z == '"' or z == '>':
                    continue
                m = re.match(r'(\d{1,3})\.(\d{1,3})\.(\d{1,3})', z)
                if m:
                    book = m.group(1)
                    chapter = m.group(2)
                    verse = m.group(3)
                    bookNum = int(book)
                    verseNum = int(verse)
                    continue
                m = re.match(r'(\s?\[.*\s?.*?\])\s(.*)\s?', z)
                content = z
                if m:
                    content = m.group(2)
                    verseNum = 1
                    chapter = m.group(1)
                insert = [title, str(bookNum), "LATIN", author, dates, str(chapter), str(verseNum), content, total]
                verseNum += 1
                print(insert)
            bookNum += 1
    return schema


def cleanUp(text):
    temp = re.sub(r'^\s*', '', text)
    temp = re.sub(r'\n', ' ', text)
    return temp


def getAugustine2():
    global links
    schema = []
    link = links["Augustine"]
    req = urllib.request.urlopen(link).read().decode('utf-8', "replace")
    s = BeautifulSoup(req, 'html.parser')
    title = "AUGUSTINE OF HIPPO"
    author = s.title.text.strip()
    dates = "354-430 A.D."
    prefix = "http://www.thelatinlibrary.com/"
    book = ""
    bookNum = 1
    chapter = ""
    verse = ""
    verseNum = ""
    tables = s.find_all('table', class_="")
    for i in tables:
        if re.search(r'CONFESS', i.text) or re.search(r'DE CIVITATE', i.text):
            text = i.text.replace('\n', '')
            title = text
            bookNum = 1
            continue
        if i.text == "" or re.search(r'Christian|The|de|SERMONES|Regula|CONTRA|DE TRINITATE|IULIANI', i.text):
            continue
        textLink = i.find_all("a")
        for j in textLink:
            total = prefix + j.get("href")
            t = urllib.request.urlopen(total).read().decode('utf-8', "replace")
            s2 = BeautifulSoup(t, 'html.parser')
            doc = s2.find_all('p', class_="")
            for z in doc:
                text = cleanUp(z.text)
                if re.search(r'Augustine|Christian|The', z.text) or z.text == " " or z.text == "\n":
                    continue
                print(title)
getAugustine2()

