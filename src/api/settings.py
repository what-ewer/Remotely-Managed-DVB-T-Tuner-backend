from flask import Response
import json


class SettingsAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

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
        return Response(json.dumps(result), status=200, mimetype="json")

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
