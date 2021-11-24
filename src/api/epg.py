from flask import Response
import json
from src.database.db_model import JsonConverter, EPG


class EpgAPI:
    def __init__(self, db_manager, heartbeat_api):
        self.db_manager = db_manager
        self.heartbeat = heartbeat_api

    def get_epg(self, id):
        query = """SELECT epg FROM tuners 
            WHERE id = %s"""
        args = [id]

        result = self.db_manager.run_query(query, args)
        if result:
            try:
                epg = JsonConverter.convert_any(result[0][0], EPG)
            except:
                return Response(
                    json.dumps([], default=lambda o: o.__dict__, indent=4),
                    mimetype="json",
                    status=200,
                )
            else:
                return Response(
                    json.dumps(epg, default=lambda o: o.__dict__, indent=4),
                    mimetype="json",
                    status=200,
                )
        else:
            return Response("Something went wrong", status=500)

    def post_epg(self, id, epg):
        epg_dumped = json.dumps(epg).replace("'", "''")
        query = """UPDATE tuners
            SET epg = %s
            WHERE id = %s"""
        args = [epg_dumped, id]

        if self.db_manager.run_query(query, args, return_result=False):
            self.heartbeat.provide_information(id, "need_epg")
            return Response("Successfully updated EPG", status=201)
        else:
            return Response("Something went wrong", status=500)
