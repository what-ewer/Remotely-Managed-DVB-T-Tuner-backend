from flask import Response
import json
from src.database.db_model import RecordInformation


class RecordedAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_recorded(self, id):
        query = f"""SELECT ri.order_id,
            ri.channel_name,
            ri.channel_id,
            ri.channel_number,
            ri.start,
            ri.stop,
            ri.title,
            ri.subtitle,
            ri.summary,
            ri.description,
            ri.record_size,
            ri.file_name
            FROM recorded_files as rf
            INNER JOIN record_information as ri
            ON rf.order_id = ri.order_id
            WHERE tuner_id = ?"""
        args = [id]

        result = self.db_manager.run_query(query, args)
        if result:
            tuner_status = RecordInformation(*result[0])
            return Response(
                json.dumps(tuner_status, default=lambda o: o.__dict__, indent=4),
                mimetype="json",
                status=200,
            )
        else:
            return Response("Something went wrong", status=500)

    def post_recorded(self, id, recorded):
        posted = []
        not_posted = []
        for o in recorded:
            if self.__order_with_id_exists(o.order_id):
                query = f"""INSERT INTO recorded_files(order_id, tuner_id, channel_id, program_name, record_size, start, end) \
                    VALUES(?, ?, ?, ?, ?, ?, ?)"""
                args = [o.order_id, id, o.channel_id, o.program_name, o.record_size, o.start, o.end]
               
                if self.db_manager.run_query(query, args, return_id=True):
                    if not self.__update_information(o.order_id, o.record_size, o.file_name):
                        return Response("Something went wrong", status=500)
                else:
                    return Response("Something went wrong", status=500)
                posted.append(o.order_id)
            else:
                not_posted.append(o.order_id)
        return Response(json.dumps({"posted_ids": posted, "not_posted": not_posted}), status=201)

    def __update_information(self, order_id, record_size, filename):
        query = """UPDATE record_information
            SET record_size = ?, file_name = ?
            WHERE order_id = ?"""
        args = [record_size, filename, order_id]

        return self.db_manager.run_query(query, args, return_result=False)

    def __order_with_id_exists(self, id):
        query = """SELECT *
            FROM record_orders
            WHERE id = ?"""
        args = [id]

        return self.db_manager.run_query(query, args)
