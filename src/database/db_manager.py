import sqlite3
from os import listdir
from os.path import isfile, join


class DBManager:
    def _drop_database(self):
        file = open("src/database/utility/drop_all", mode="r")
        drop_query = file.readlines()
        file.close()
        self.execute_multiple_queries(drop_query)

    def _setup_tables(self):
        table_creates = [
            join("src/database/create/", f)
            for f in listdir("src/database/create/")
            if isfile(join("src/database/create/", f))
        ]
        queries = []
        for filename in table_creates:
            file = open(filename, mode="r")
            queries.append(file.read())
            file.close()

        self.execute_multiple_queries(queries)

    def _generate_data(self):
        file = open("src/database/utility/example_data", mode="r")
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

    def run_query(
        self,
        query,
        args,
        return_id=False,
        return_result=True,
        return_on_success=True,
        return_on_error=False,
        print_error=True,
    ):
        try:
            query_result = self.execute_query(
                query, get_inserted_id=return_id, args=args
            )
        except Exception as exc:
            if print_error:
                print(exc)
            return return_on_error
        return query_result if return_result else return_on_success

    def execute_query(self, query, get_inserted_id=False, args=[]):
        con = sqlite3.connect("rmdvbt.db")
        cur = con.cursor()
        cur.execute(query, args)
        res = cur.fetchall()
        if get_inserted_id:
            res = cur.lastrowid
        con.commit()
        cur.close()
        con.close
        return res

    def execute_multiple_queries(self, queries):
        res = [self.execute_query(query) for query in queries]
        return res
