import sqlite3
from os import listdir, stat
from os.path import isfile, join

class DBManager:
    def __init__(self):
        self.con = sqlite3.connect("rmdvbt.db")

    @staticmethod
    def setup_tables():            
        con = sqlite3.connect('rmdvbt.db')
        cur = con.cursor()
        table_creates = [join("database/create/",f) for f in listdir("database/create/") if isfile(join("database/create/", f))]
        for filename in table_creates:
            file = open(filename, mode='r')
            create_query = file.read()
            cur.execute(create_query)
            con.commit()
        con.close()
        file.close()

    def execute_query(self, query):
        cur = self.con.cursor()
        cur.execute(query)
        res = cur.fetchall()
        cur.commit()
        cur.close()
        return res
