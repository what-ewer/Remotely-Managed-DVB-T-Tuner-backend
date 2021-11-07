from flask import Response
import json
from src.database.db_model import Settings


class SettingsAPI:
    def __init__(self, db_manager, heartbeat_api):
        self.db_manager = db_manager
        self.heartbeat = heartbeat_api

    def get_settings(self, id):
        query = """SELECT recording_location, tvh_username, tvh_password 
            FROM settings
            WHERE tuner_id = ?"""
        args = [id]

        result = self.db_manager.run_query(query, args)
        if result:
            settings = Settings(*result[0])
            return Response(
                json.dumps(settings, default=lambda o: o.__dict__, indent=4),
                mimetype="json",
                status=200,
            )
        else:
            return Response("Something went wrong", status=500)

    def post_settings(self, id, username, password, settings):
        query = """INSERT OR REPLACE INTO settings(tuner_id, recording_location, tvh_username, tvh_password)
            VALUES(?, ?, ?, ?)"""
        args = [
            id,
            settings.recording_location,
            settings.tvh_username,
            settings.tvh_password,
        ]

        if self.db_manager.run_query(query, args, return_result=False):
            self.heartbeat.provide_information(id, "changed_settings")
            return Response("Successfully updated Settings", status=201)
        else:
            return Response("Something went wrong", status=500)
