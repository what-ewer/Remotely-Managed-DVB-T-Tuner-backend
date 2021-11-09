import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class DBManager:
    def __init__(self, username, password, host):
        self.conn = self.connect(username, password, host)

    def connect(self, username, password, host):
        try:
            conn = psycopg2.connect(
                user=username,
                host=host,
                password=password,
                database="rmdvbt",
            )
        except psycopg2.OperationalError:
            conn = psycopg2.connect(
                user=username,
                host=host,
                password=password,
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            cursor = conn.cursor()
            create_db_query = """
                CREATE DATABASE rmdvbt
            """
            cursor.execute(create_db_query)
            return conn

        return conn

    def _drop_database(self):
        file = open("src/database/utility/drop_all", mode="r")
        drop_query = file.readlines()
        file.close()
        self.execute_multiple_queries(drop_query)

    def _setup_tables(self):
        filename = "src/database/create/create_all"
        file = open(filename, mode="r")
        query = file.read()
        file.close()
        self.execute_query(query)

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
                query, get_inserted_id=return_id, return_result=return_result, args=args
            )
        except Exception as exc:
            if print_error:
                self.conn.rollback()
                print(f"QUERY: {query}\n EXCEPTION: {exc}")
            return return_on_error
        return query_result if return_result else return_on_success

    def execute_query(self, query, get_inserted_id=False, return_result=True, args=()):
        cur = self.conn.cursor()
        cur.execute(query, args)
        res = ""

        if get_inserted_id:
            res = cur.fetchall()[0][0]
        elif return_result:        
            try:
                res = cur.fetchall()
            except:
                res = ""

        self.conn.commit()
        cur.close()
        return res

    def execute_multiple_queries(self, queries):
        res = [self.execute_query(query) for query in queries]
        return res
