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
         "Novatian": "http://www.thelatinlibrary.com/novatian.html",
         "Alfonsi": "http://www.thelatinlibrary.com/alfonsi.disciplina.html",
         "Gregorius Magnus": "http://www.thelatinlibrary.com/greg.html",
         "Bonaventure": "http://www.thelatinlibrary.com/bonaventura.itinerarium.html"}

'''
Base Functions.
'''
# create the database to store the text
def createdb():
    # creates a connection to a db
    # if the db isn't already created it will create a new one.
    try:
        conn = sqlite3.connect('project1.db')
        conn.execute('''CREATE TABLE latin
        (title TEXT, book TEXT, language TEXT, author TEXT, dates TEXT, chapter TEXT, verse TEXT, passage TEXT, link TEXT)''')
        conn.commit()
        conn.close()
        return
    except:
        print("latin table already exists")
        return


# Test of the database.
def testSelect():
    conn = sqlite3.connect('project1.db')
    cursor = conn.cursor()
    cursor.execute('''select * from latin; ''')
    print(cursor.fetchall())
    conn.close()

# This will grab the HTML associated with the library
def getHTML(lib):
    global links
    link = links[lib]
    req = urllib.request.urlopen(link).read().decode('utf-8', "replace")
    s = BeautifulSoup(req, 'html.parser')
    return s

'''
Part A for Project 1 Phase 1
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


# Assume title is Novatian
# Assume book is NOVATIANI DE TRINITATE
def getNovatian():
    s = getHTML("Novatian")
    title = s.title.text.strip()
    global links
    link = links["Novatian"]
    author = title
    dates = ""  # couldn't find dates on the page.
    book = s.find("p", class_="pagehead")
    book = re.sub(r'\n', '', book.text)
    chapterNum = 0
    schema = []
    # Only pull the paragraphs with no class.
    # contains the chapters.
    chapters = s.find_all("p", class_="")
    # Remove the links from the bottom of the page
    chapters = chapters[:-1]
    for i in chapters:
        chapterNum += 1
        data = re.sub(r'\xa0', ' ', i.text)
        data = re.sub(r'\n', ' ', data)
        data = re.split(r' \d{1,3}\. ', data)
        data = data[1:]
        verseNum = 1
        for j in data:
            insert = [title, book, "LATIN", author, dates, str(chapterNum), str(verseNum), j, link]
            schema.append(insert)
            verseNum += 1
    return schema


# Get Alfonsi data
# Assume one book, each bold title is a new chapter
# And every new paragraph under the bold title is a verse
def getAlfonsi():
    schema = []
    global links
    link = links["Alfonsi"]
    s = getHTML("Alfonsi")
    title = s.title.text.strip()
    title = re.sub(r'\n', '', title)
    book = "Disciplina clericalis"
    author = "Peter Alfonsi"
    dates = ""
    chapters = s.find_all("b", class_="")
    chapterNum = 0
    verseNum = 1
    chapters2 = []
    for i in chapters:
        chapters2.append("\n" + i.text + ". " + "\n")
    chapters = chapters2
    verses = s.find_all("p", class_="")
    verses = verses[:-1]
    for i in verses:
        if i.text in chapters:
            chapterNum += 1
            verseNum = 1
            continue
        data = re.sub(r'\n', ' ', i.text)
        insert = [title, book, "LATIN", author, dates, str(chapterNum), str(verseNum), data, link]
        schema.append(insert)
        verseNum += 1
    return schema


# Assume, one title and one book.
# Assume, a chapter is a new paragraph
# Assume, a sentence is a verse.
def getGregMag():
    schema = []
    global links
    link = links["Gregorius Magnus"]
    s = getHTML("Gregorius Magnus")
    title = s.title.text.strip()
    book = s.find("p", class_="pagehead")
    book = re.sub(r'\n', '', book.text)
    author = "Gregorius Magnus"
    dates = ""
    chapters = s.find_all("p", class_="")
    chapters = chapters[:-1]
    chapterNum = 1
    for i in chapters:
        data = re.sub(r'\n', '', i.text)
        data = data.split(". ")
        verseNum = 1
        for j in data:
            insert = [title, book, "LATIN", author, dates, str(chapterNum), str(verseNum), j, link]
            schema.append(insert)
            verseNum += 1
        chapterNum += 1
    return schema


def getBonaventure():
    schema = []
    global links
    link = links["Bonaventure"]
    s = getHTML("Bonaventure")
    author = s.title.text.strip()
    dates = "1221-1274"
    title = s.find_all("p", class_="pagehead")
    title = re.sub(r'\n', "", title[1].text)
    book = title
    chapters = s.find_all("b")
    verses = s.find_all("p", class_="")
    verses = verses[:-1]
    chapterNum = 0
    verseNum = 1
    chapters2 = []
    for i in verses:
        data = re.sub(r'\n', '', i.text)
        if data.isupper():
            continue
        if re.search(r'1\.', data):
            chapterNum += 1
            verseNum = 1
        data = re.sub(r'\s?\d{1,3}\.\s', '', data)
        data = re.sub(r'^\s\s?', '', data)
        insert = [title, book, "LATIN", author, dates, str(chapterNum), str(verseNum), data, link]
        schema.append(insert)
        verseNum += 1
    return schema


'''
Part B of Phase 1
Inserting all of the data from the Lists
'''


# Insert the Magna Carta data into the database.
# Takes the list generated from getMagnaCarta() and executes many into the database
def insertMagnaCarta():
    conn = sqlite3.connect('project1.db')
    data = getMagnaCarta()
    conn.executemany('''INSERT INTO latin(title, book, language, author, dates, chapter, verse, passage, link)
    VALUES(?,?,?,?,?,?,?,?,?)''', data)
    conn.commit()
    conn.close()


# Insert Creeds data into the database
# Takes a list of the data provided from the Creeds text and inserts it into the database
def insertCreeds():
    conn = sqlite3.connect('project1.db')
    data = getCreeds()
    conn.executemany('''INSERT INTO latin(title, book, language, author, dates, chapter, verse, passage, link)
    VALUES(?,?,?,?,?,?,?,?,?)''', data)
    conn.commit()
    conn.close()


# Insert the Epitaph data into the database
def insertEpitaphs():
    conn = sqlite3.connect('project1.db')
    data = getRomanEps()
    conn.executemany('''INSERT INTO latin(title, book, language, author, dates, chapter, verse, passage, link)
    VALUES(?,?,?,?,?,?,?,?,?)''', data)
    conn.commit()
    conn.close()


# Insert the data from Novatian library
def insertNovatian():
    conn = sqlite3.connect('project1.db')
    data = getNovatian()
    conn.executemany('''INSERT INTO latin(title, book, language, author, dates, chapter, verse, passage, link)
        VALUES(?,?,?,?,?,?,?,?,?)''', data)
    conn.commit()
    conn.close()


# Insert the data from the Alfonsi library
def insertAlfonsi():
    conn = sqlite3.connect('project1.db')
    data = getAlfonsi()
    conn.executemany('''INSERT INTO latin(title, book, language, author, dates, chapter, verse, passage, link)
            VALUES(?,?,?,?,?,?,?,?,?)''', data)
    conn.commit()
    conn.close()


def insertGregMag():
    conn = sqlite3.connect('project1.db')
    data = getGregMag()
    conn.executemany('''INSERT INTO latin(title, book, language, author, dates, chapter, verse, passage, link)
                VALUES(?,?,?,?,?,?,?,?,?)''', data)
    conn.commit()
    conn.close()


def insertBonaventure():
    conn = sqlite3.connect('project1.db')
    data = getBonaventure()
    conn.executemany('''INSERT INTO latin(title, book, language, author, dates, chapter, verse, passage, link)
                VALUES(?,?,?,?,?,?,?,?,?)''', data)
    conn.commit()
    conn.close()

