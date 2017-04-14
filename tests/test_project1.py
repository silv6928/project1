import sqlite3
import project1
from project1 import project1


# Test the creation of the database to ensure it will be created
def test_db_create():
    project1.createdb()
    conn = sqlite3.connect('project1.db')
    cur = conn.cursor()
    assert cur


'''
Test to make sure the extracts of data lists are not empty
If they are not empty then the data was extracted
Also, these test to see if we were able to connect to the website
'''


def test_get_MagnaCarta():
    l = project1.getMagnaCarta()
    assert len(l) > 0


def test_get_Creeds():
    l = project1.getCreeds()
    assert len(l) > 0


def test_get_RomanEps():
    l = project1.getRomanEps()
    assert len(l) > 0


def test_get_Bonaventure():
    l = project1.getBonaventure()
    assert len(l) > 0


def test_get_Alfonsi():
    l = project1.getAlfonsi()
    assert len(l) > 0


def test_get_Novatian():
    l = project1.getNovatian()
    assert len(l) > 0


def test_get_GregMag():
    l = project1.getGregMag()
    assert len(l) > 0


'''
The following tests are tests of the population of the database.
Note: if the get functions above failed for a text (i.e. Magna Carta) then the
population of the database will also fail
'''


def test_pop_MagnaCarta():
    project1.insertMagnaCarta()
    conn = sqlite3.connect('project1.db')
    cur = conn.cursor()
    cur.execute('''select * from latin where title = 'Magna Carta';''')
    assert cur.fetchall()


def test_pop_Creeds():
    project1.insertCreeds()
    conn = sqlite3.connect('project1.db')
    cur = conn.cursor()
    cur.execute('''select * from latin where title = 'Early Christian Creeds';''')
    assert cur.fetchall()


def test_pop_RomanEps():
    project1.insertEpitaphs()
    conn = sqlite3.connect('project1.db')
    cur = conn.cursor()
    cur.execute('''select * from latin where title = 'ROMAN EPITAPHS';''')
    assert cur.fetchall()


def test_pop_Nov():
    project1.insertNovatian()
    conn = sqlite3.connect('project1.db')
    cur = conn.cursor()
    cur.execute('''select * from latin where title = 'Novatian';''')
    assert cur.fetchall()


def test_pop_Alfonsi():
    project1.insertAlfonsi()
    conn = sqlite3.connect('project1.db')
    cur = conn.cursor()
    cur.execute('''select * from latin where title = 'Peter Alfonsi: Disciplina clericalis';''')
    assert cur.fetchall()


def test_pop_Bonaventure():
    project1.insertBonaventure()
    conn = sqlite3.connect('project1.db')
    cur = conn.cursor()
    cur.execute('''select * from latin where title = 'ITINERARIUM MENTIS IN DEUM';''')
    assert cur.fetchall()


def test_pop_GregMag():
    project1.insertGregMag()
    conn = sqlite3.connect('project1.db')
    cur = conn.cursor()
    cur.execute('''select * from latin where title = 'Letter of Gregory the Great';''')
    assert cur.fetchall()

'''
Tests for the Translation Services
'''


# Need to test to see if dog == canis
def test_fts_pop():
    project1.create_fts_table()
    project1.populate_fts_table()
    conn = sqlite3.connect('project1.db')
    cur = conn.cursor()
    cur.execute('''select * from latin_fts;''')
    assert cur.fetchall()


def test_translation():
    phrase = project1.get_latin_translation("dog")
    assert phrase == "canis"


def test_fts_search():
    project1.create_fts_table()
    project1.populate_fts_table()
    conn = sqlite3.connect('project1.db')
    cur = conn.cursor()
    cur.execute('''select * from latin_fts WHERE passage MATCH 'Christus';''')
    assert cur.fetchall()
