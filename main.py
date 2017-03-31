import project1
from project1 import project1


def main():

    # Create database and insert the data
    project1.createdb()
    project1.insertMagnaCarta()
    project1.insertCreeds()
    project1.insertEpitaphs()
    project1.insertNovatian()
    project1.insertAlfonsi()
    project1.insertBonaventure()
    project1.insertGregMag()

    # This is used for the sake of the grader to see the database is populated from the run.
    # This is a query that selects all records of the project1 database.
    project1.testSelect()

if __name__ == "__main__":
    main()
