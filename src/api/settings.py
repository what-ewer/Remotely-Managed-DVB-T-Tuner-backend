from flask import Response
import json
from src.database.db_model import Settings


class SettingsAPI:
    def __init__(self, db_manager, heartbeat_api):
        self.db_manager = db_manager
        self.heartbeat = heartbeat_api

    def get_settings(self, id):
        query = """SELECT recording_location, free_space, tvh_username, tvh_password 
            FROM settings
            WHERE tuner_id = %s"""
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

    def post_settings(self, id, settings):
        query = """INSERT INTO settings(tuner_id, recording_location, free_space, tvh_username, tvh_password)
            VALUES(%s, %s, %s, %s, %s)
            ON CONFLICT(tuner_id)
            DO
                UPDATE SET (recording_location, free_space, tvh_username, tvh_password)
                = (EXCLUDED.recording_location, EXCLUDED.free_space, EXCLUDED.tvh_username, EXCLUDED.tvh_password)"""
        args = [
            id,
            settings.recording_location,
            settings.free_space,
            settings.tvh_username,
            settings.tvh_password,
        ]

        if self.db_manager.run_query(query, args, return_result=False):
            self.heartbeat.provide_information(id, "changed_settings")
            return Response("Successfully updated Settings", status=201)
        else:
            return Response("Something went wrong", status=500)
