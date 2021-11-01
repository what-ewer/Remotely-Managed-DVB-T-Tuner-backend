from typing import Set
from flask import Response
import json, requests
from src.api import heartbeat
from src.database.db_model import Settings


class SettingsAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

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
            # POST that we provided needed Settings information
            requests.post(
                url=f"{heartbeat.url}/ask",
                params={"id": id, "information": "changed_settings"},
                auth=(username, password),
            )
            return Response("Successfully updated Settings", status=201)
        else:
            return Response("Something went wrong", status=500)
