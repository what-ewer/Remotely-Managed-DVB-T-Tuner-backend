import sqlite3
from os import listdir
from os.path import isfile, join


class DBManager:
    def _drop_database(self):
        file = open("database/utility/drop_all", mode="r")
        drop_query = file.readlines()
        file.close()
        self.execute_multiple_queries(drop_query)

    def _setup_tables(self):
        table_creates = [
            join("database/create/", f)
            for f in listdir("database/create/")
            if isfile(join("database/create/", f))
        ]
        queries = []
        for filename in table_creates:
            file = open(filename, mode="r")
            queries.append(file.read())
            file.close()

        self.execute_multiple_queries(queries)

    def _generate_data(self):
        file = open("database/utility/example_data", mode="r")
        create_query = file.readlines()
        self.execute_multiple_queries(create_query)
        file.close()

    def generate_db_with_data(self):
        self._drop_database()
        self._setup_tables()
        self._generate_data()

    def generate_db_without_data(self):
        self._drop_database()
        self._setup_tables()

    def execute_query(self, query):
        con = sqlite3.connect("rmdvbt.db")
        cur = con.cursor()
        cur.execute(query)
        res = cur.fetchall()
        con.commit()
        cur.close()
        con.close
        return res

    def execute_multiple_queries(self, queries):
        res = [self.execute_query(query) for query in queries]
        return res
