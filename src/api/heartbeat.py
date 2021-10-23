from flask import Response
import json


class HeartbeatAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager