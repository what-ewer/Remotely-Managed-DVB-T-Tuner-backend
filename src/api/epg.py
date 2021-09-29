from flask import Response
import json


class EpgAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_tuner_info(self, query, return_list=False):
        try:
            res = self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)
        res = res[0][0]
        return Response(res, status=200, mimetype="json") if not return_list else res

    def post_epg(self, id, epg):
        epg_dumped = json.dumps(epg)
        epg_dumped = epg_dumped.replace("'", "''")
        query = f"""UPDATE tuners
        SET epg = '{epg_dumped}'
        WHERE id = {id}"""

        try:
            self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)

        return Response("successfully updated epg", status=200)

    def get_epg(self, id):
        query = f"SELECT epg FROM tuners \
            WHERE id = {id}"
        return self.get_tuner_info(query)
