from flask import Response
import json


class StatusAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def post_status(self, id, status):
        try:
            query = f"""INSERT OR REPLACE INTO tuner_status(tuner_id, free_space, is_recording, current_recording_time, current_recording_size)
                        VALUES({id}, {status.free_space}, {status.is_recording}, {status.current_recording_time}, {status.current_recording_size})"""
        except:
            return Response("Wrong hearbeat list", status=400)
        else:
            try:
                self.db_manager.execute_query(query)
            except Exception as exc:
                return Response(str(exc), status=500)
        return Response("successfully posted status", status=200)

    def get_status(self, id):
        query = f"""SELECT free_space, is_recording, current_recording_time, current_recording_size FROM tuner_status
            WHERE tuner_id = {id}"""
        try:
            status = self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)
        return Response(json.dumps(status), status=200)
