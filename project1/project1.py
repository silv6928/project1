#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import urllib.request
import sqlite3
import re
import requests
import sys
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
# Assume "B" and "CIL are books, the number next to it is the chapter
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
# New paragraph is a new chapter
# Use Regex to find verses in the paragraph
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


# Assume there is one title, and one book.
# Assume that a new chapter is designated by bold header.
# Assume that a new verse begins with a number followed by a period.
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

'''
Begin Phase 2 of Project 1
Parts C and D
Translation Services
and UI
'''


# Create the Full Test Search Table
def create_fts_table():
    # creates a connection to a db
    # if the db isn't already created it will create a new one.
    try:
        conn = sqlite3.connect('project1.db')
        conn.execute('''CREATE VIRTUAL TABLE latin_fts USING fts4 (title, book,
        language, author, dates, chapter, verse, passage, link)''')
        conn.commit()
        conn.close()
        return
    except:
        print("latin_fts table already exists")
        return


# Populate the FTS table with the content from the latin table
def populate_fts_table():
    conn = sqlite3.connect('project1.db')
    conn.execute('''INSERT INTO latin_fts(title, book, language, author, dates, chapter, verse, passage, link)
    select * from latin;''')
    conn.commit()
    conn.close()


def get_latin_translation(phrase):
    parameters = {"q": phrase, "langpair": "en|lat"}
    data = requests.get("http://api.mymemory.translated.net/get", params=parameters)
    return data.json()["responseData"]["translatedText"]


# Search the Database for the Latin search term
def search_db_latin(phrase):
    conn = sqlite3.connect('project1.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM latin_fts WHERE passage MATCH ? ;''', phrase)
    data = cursor.fetchall()
    conn.close()
    return data


# Perform the query search of the database depending on what the user selects
def get_phrase(num):
    print("Please enter your search/translation term:")
    phrase = str(input())
    if num == 1:
        print("Here are your search results")
        data = search_db_latin(phrase)
        print(data)
    elif num == 2:
        print("Here is your translation:")
        data = get_latin_translation(phrase)
        print(data)
        print("Here are your search results")
        data = search_db_latin(data)
        print(data)
    else:
        print("Here is your graph")


def user_interface():
    print("Welcome to the Application")
    print("This application allows you to do multiple things with the Latin Library ")
    print("Enter 1 for a Latin Search of the Database")
    print("Enter 2 for a English to Latin Translation and a Search of the Database")
    print("Enter 3 for a visualization of a search term")
    print("Enter 0 to exit application")
    num = 99
    while num != 0:
        num = int(str(input()))
        if num == 1:
            print("You selected Latin Search")
            get_phrase(num)
        elif num == 2:
            print("You selected English to Latin Translation and Search")
            get_phrase(num)
        elif num == 3:
            print("You selected a visualization of a search term")
            get_phrase(num)
        if num == 0:
            print("You selected to exit the application")
