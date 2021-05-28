from flask import Response
import json, datetime
import datetime


class TunerAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_orders(self, id):
        query = f"SELECT channel_id, start, end FROM record_orders \
            WHERE tuner_id = {id}"

        ts = datetime.datetime.now().timestamp()
        try:
            orders = self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)

        result = [
            {"channel_id": str(o[0]), "start": o[1], "end": o[2]}
            for o in orders
            if o[1] > ts
        ]

        return Response(json.dumps(result), status=200)

    def get_settings(self, id):
        query = f"""SELECT recording_location, tvh_username, tvh_password FROM settings
            WHERE tuner_id = {id}"""
        try:
            settings = self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)

        result = [
            {"recording_location": s[0], "tvh_username": s[1], "tvh_password": s[2]}
            for s in settings
        ]
        return Response(json.dumps(result), status=200)

    def post_channels(self, id, channels):

        query = f"""UPDATE tuners
        SET channels = "{channels}"
        WHERE id = {id}"""

        try:
            self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)

        return Response("successfully updated channels", status=200)

    def post_epg(self, id, epg):

        query = f"""UPDATE tuners
        SET epg = "{epg}"
        WHERE id = {id}"""

        try:
            self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)

        return Response("successfully updated epg", status=200)

    def post_recorded(self, id, recorded):
        for o in recorded:
            try:
                query = f"""INSERT INTO recorded_files(tuner_id, program_name, record_size) \
                    VALUES({id}, '{o.program_name}', {o.record_size})"""
            except:
                return Response("Wrong record recorded list", status=400)
            else:
                try:
                    self.db_manager.execute_query(query)
                except Exception as exc:
                    return Response(str(exc), status=500)
        return Response("successfully posted recorded", status=200)

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
