from flask import Response
import json


class ChannelsAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_tuner_info(self, query, return_list=False):
        try:
            res = self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)
        res = res[0][0]
        return Response(res, status=200, mimetype="json") if not return_list else res

    def get_channels(self, id, return_list=False):
        query = f"SELECT channels FROM tuners \
            WHERE id = {id}"
        return self.get_tuner_info(query, return_list)

    def post_channels(self, id, channels):

        query = f"""UPDATE tuners
        SET channels = '{json.dumps(channels)}'
        WHERE id = {id}"""

        try:
            self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)

        return Response("successfully updated channels", status=200)
