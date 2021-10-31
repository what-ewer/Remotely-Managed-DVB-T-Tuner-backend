from flask import Response
import json


class RecordedAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_recorded(self, id):
        query = f"""SELECT program_name, record_size FROM recorded_files
                WHERE tuner_id = {id}"""
        try:
            recorded = self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)

        result = [
            {"program_name": str(r[0]), "record_size": str(r[1])} for r in recorded
        ]
        return Response(json.dumps(result), status=200, mimetype="json")

    def post_recorded(self, id, recorded):
        for o in recorded:
            if self.__order_with_id_exists(o.order_id):
                try:
                    query = f"""INSERT INTO recorded_files(order_id, tuner_id, channel_id, program_name, record_size, start, end) \
                        VALUES({o.order_id}, {id}, '{o.channel_id}', '{o.program_name}', {o.record_size}, {o.start}, {o.end})"""
                except:
                    return Response("Wrong record recorded list", status=400)
                else:
                    try:
                        self.db_manager.execute_query(query)
                        self.__update_information(o.order_id, o.record_size, o.file_name)
                    except Exception as exc:
                        return Response(str(exc), status=500)
            else:
                return Response("order with that id doesnt exist", status=400)
        return Response("successfully posted recorded", status=200)

    def __update_information(self, order_id, record_size, filename):
        query = f"""UPDATE record_information
            SET record_size = {record_size}, file_name = '{filename}'
            WHERE order_id = {order_id}"""

        try:
            self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)

        return Response("successfully updated channels", status=200)

    def __order_with_id_exists(self, id):
        query = f"""SELECT *
            FROM record_orders
            WHERE order_id = {id}"""

        try:
            res = self.db_manager.execute_query(query)
        except Exception as exc:
            return False

        return res
