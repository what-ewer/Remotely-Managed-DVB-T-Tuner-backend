from flask import Response
import json, requests
from src.api import heartbeat
from src.database.db_model import JsonConverter, EPG


class EpgAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_epg(self, id):
        query = """SELECT epg FROM tuners 
            WHERE id = ?"""
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

    def post_epg(self, id, username, password, epg):
        epg_dumped = json.dumps(epg).replace("'", "''")
        query = f"""UPDATE tuners
            SET epg = '{epg_dumped}'
            WHERE id = ?"""
        args = [id]

        if self.db_manager.run_query(query, args, return_result=False):
            # POST that we provided needed EPG information
            requests.post(
                url=f"{heartbeat.url}/provide",
                params={"id": id, "information": "need_epg"},
                auth=(username, password),
            )
            return Response("Successfully updated EPG", status=201)
        else:
            return Response("Something went wrong", status=500)
