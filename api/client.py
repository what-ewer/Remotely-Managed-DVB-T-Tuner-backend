from flask import Response
import json


class ClientAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def post_orders(self, id, orders):
        json_orders = json.loads(orders)

        for o in json_orders:
            try:
                query = f"""INSERT INTO record_orders(tuner_id, channel_id, start, end) \
                    VALUES({id}, {o['channel_id']}, {o['start']}, {o['end']})"""
            except:
                return Response("Wrong record orders list", status=400)
            else:
                try:
                    self.db_manager.execute_query(query)
                except Exception as exc:
                    return Response(str(exc), status=500)
        return Response("successfully posted orders", status=200)

    def get_channels(self, id):
        query = f"SELECT channels FROM tuners \
            WHERE id = {id}"

        return self.db_manager.execute_query(query)
