class ClientAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def post_orders(self, id, orders):
        for o in orders:
            query = f"SELECT INTO record_orders \
                ({id, o.channel_id, o.start, o.stop})"

            self.db_manager.execute_query(query)

    def get_channels(self, id):
        query = f"SELECT channels FROM tuners \
            WHERE id = {id}"

        return self.db_manager.execute_query(query)
