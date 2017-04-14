import project1
from project1 import project1


def main():

    # Create database and insert the data
    project1.createdb()
    # Insert all of the data
    project1.insertMagnaCarta()
    project1.insertCreeds()
    project1.insertEpitaphs()
    project1.insertNovatian()
    project1.insertAlfonsi()
    project1.insertBonaventure()
    project1.insertGregMag()
    # Creates FTS Table to search from
    project1.create_fts_table()
    project1.populate_fts_table()

    project1.user_interface()

if __name__ == "__main__":
    main()
