#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import urllib.request
import os
import random

# Links to Text
links = {"Magna Carta": "http://www.thelatinlibrary.com/magnacarta.html",
         "Creeds": "http://www.thelatinlibrary.com/creeds.html"}


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
