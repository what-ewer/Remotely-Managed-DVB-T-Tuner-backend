from flask import Response
import json


class ClientAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def post_orders(self, id, orders):
        for o in orders:
            try:
                query = f"""INSERT INTO record_orders(tuner_id, channel_id, start, end) \
                    VALUES({id}, {o.channel_id}, {o.start}, {o.end})"""
            except:
                return Response("Wrong record orders list", status=400)
            else:
                try:
                    self.db_manager.execute_query(query)
                except Exception as exc:
                    return Response(str(exc), status=500)
        return Response("successfully posted orders", status=200)

    def get_tuner_info(self, query):
        try:
            res = self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)
        res = res[0][0]
        return Response(res, status=200)

    def get_channels(self, id):
        query = f"SELECT channels FROM tuners \
            WHERE id = {id}"
        return self.get_tuner_info(query)

    def get_epg(self, id):
        query = f"SELECT epg FROM tuners \
            WHERE id = {id}"
        return self.get_tuner_info(query)

    def get_status(self, id):
        query = f"""SELECT free_space, is_recording, current_recording_time, current_recording_size FROM tuner_status
            WHERE tuner_id = {id}"""
        try:
            status = self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)

        result = [
            {
                "free_space": str(s[0]),
                "is_recording": s[1],
                "current_recording_time": str(s[2]),
                "current_recording_size": str(s[3]),
            }
            for s in status
        ]
        return Response(json.dumps(result), status=200)

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
        return Response(json.dumps(result), status=200)

    def post_settings(self, id, settings):
        try:
            query = f"""INSERT OR REPLACE INTO settings(tuner_id, recording_location, tvh_username, tvh_password)
                        VALUES({id}, '{settings.recording_location}', '{settings.tvh_username}', '{settings.tvh_password}')"""
        except:
            return Response("Wrong settings list", status=400)
        else:
            try:
                self.db_manager.execute_query(query)
            except Exception as exc:
                return Response(str(exc), status=500)
        return Response("successfully posted settings", status=200)
