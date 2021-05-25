import sqlite3
from os import listdir
from os.path import isfile, join


class DBManager:
    def __init__(self):
        # self.con = sqlite3.connect("rmdvbt.db")
        pass

    @staticmethod
    def setup_tables():
        con = sqlite3.connect("rmdvbt.db")
        cur = con.cursor()
        table_creates = [
            join("database/create/", f)
            for f in listdir("database/create/")
            if isfile(join("database/create/", f))
        ]
        for filename in table_creates:
            file = open(filename, mode="r")
            create_query = file.read()
            cur.execute(create_query)
            con.commit()
        con.close()
        file.close()

    @staticmethod
    def generate_data():
        con = sqlite3.connect("rmdvbt.db")
        cur = con.cursor()
        file = open("database/data/example_data", mode="r")
        create_query = file.readlines()
        for query in create_query:
            cur.execute(query)
            con.commit()
        con.close()
        file.close()

    def execute_query(self, query):
        con = sqlite3.connect("rmdvbt.db")
        cur = con.cursor()
        cur.execute(query)
        res = cur.fetchall()
        con.commit()
        cur.close()
        con.close
        return res
