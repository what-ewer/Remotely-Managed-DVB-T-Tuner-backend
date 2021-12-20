from flask import Response
import json
from src.database.db_model import RecordInformation


class RecordedAPI:
    def __init__(self, db_manager, heartbeat_api):
        self.db_manager = db_manager
        self.heartbeat = heartbeat_api

    def get_recorded(self, id):
        query = """SELECT ri.order_id,
            ri.channel_name,
            ri.channel_id,
            ri.channel_number,
            ri.start,
            ri.stop,
            ri.title,
            ri.subtitle,
            ri.summary,
            ri.description,
            ri.genres,
            ri.record_size,
            ri.file_name
            FROM recorded_files as rf
            INNER JOIN record_information as ri
            ON rf.order_id = ri.order_id
            WHERE tuner_id = %s"""
        args = [id]

        result = self.db_manager.run_query(query, args)
        if result:
            recorded = [RecordInformation(*r) for r in result]
            return Response(
                json.dumps(recorded, default=lambda o: o.__dict__, indent=4),
                mimetype="json",
                status=200,
            )
        else:
            return Response("Something went wrong", status=500)

    def post_recorded(self, id, recorded):
        posted = []
        not_posted = []
        updated = []
        recorded_ids = [o.order_id for o in recorded]
        if not self.__remove_deleted_recorded(id, recorded_ids):
            return Response("Something went wrong", status=500)
        self.heartbeat.ask_for_information(id, "changed_settings")
        for o in recorded:
            if self.__order_with_id_exists(o.order_id):
                if not self.__recorded_exists(o.order_id):
                    if not self.__insert_recorded(id, o):
                        return Response("Something went wrong", status=500)
                    else:
                        posted.append(o.order_id)
                else:
                    if not self.__update_recorded(id, o):
                        return Response("Something went wrong", status=500)
                    else:
                        updated.append(o.order_id)

                if not self.__update_information(
                    o.order_id, o.record_size, o.file_name
                ):
                    return Response("Something went wrong", status=500)
            else:
                not_posted.append(o.order_id)
        return Response(
            json.dumps(
                {"posted_ids": posted, "not_posted": not_posted, "updated": updated}
            ),
            status=201,
        )

    def __remove_deleted_recorded(self, id, recorded_ids):
        query = """DELETE 
            FROM recorded_files 
            WHERE tuner_id = %s"""
        if recorded_ids:
            query += " AND ("
            query += "order_id != %s"
            for _ in recorded_ids[1:]:
                query += " AND order_id != %s"
            query += ")"
        args = [id, *recorded_ids]
        return self.db_manager.run_query(query, args, return_result=False)

    def __update_information(self, order_id, record_size, filename):
        query = """UPDATE record_information
            SET record_size = %s, file_name = %s
            WHERE order_id = %s"""
        args = [record_size, filename, order_id]

        return self.db_manager.run_query(query, args, return_result=False)

    def __order_with_id_exists(self, id):
        query = """SELECT *
            FROM record_orders
            WHERE id = %s"""
        args = [id]

        return self.db_manager.run_query(query, args)

    def __insert_recorded(self, id, o):
        query = """INSERT INTO recorded_files(order_id, tuner_id, channel_id, program_name, record_size, start, stop) 
            VALUES(%s, %s, %s, %s, %s, %s, %s)
            RETURNING order_id;"""
        args = [
            o.order_id,
            id,
            o.channel_id,
            o.program_name,
            o.record_size,
            o.start,
            o.stop,
        ]

        return self.db_manager.run_query(query, args, return_id=True)

    def __recorded_exists(self, id):
        query = """SELECT *
            FROM recorded_files
            WHERE order_id = %s"""
        args = [id]

        return self.db_manager.run_query(query, args)

    def __update_recorded(self, id, o):
        query = """UPDATE recorded_files
            SET tuner_id = %s, 
                channel_id = %s, 
                program_name = %s, 
                record_size = %s, 
                start = %s, 
                stop = %s
            WHERE order_id = %s"""
        args = [
            id,
            o.channel_id,
            o.program_name,
            o.record_size,
            o.start,
            o.stop,
            o.order_id,
        ]

        return self.db_manager.run_query(query, args, return_result=False)
