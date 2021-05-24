class TunerAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_orders(self, id):
        query = f"SELECT * FROM record_orders \
            WHERE tuner_id = {id}"

        return self.db_manager.execute_query(query)
