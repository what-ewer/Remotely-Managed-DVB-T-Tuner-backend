from flask import Response
import json
from src.database.db_model import JsonConverter, Channel


class ChannelsAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_channels(self, id):
        query = """SELECT channels FROM tuners
            WHERE id = %s"""
        args = [id]

        result = self.db_manager.run_query(query, args)
        if result:
            try:
                channels = JsonConverter.convert_any(result[0][0], Channel)
            except:
                return Response(
                    json.dumps([], default=lambda o: o.__dict__, indent=4),
                    mimetype="json",
                    status=200,
                )

            else:
                return Response(
                    json.dumps(channels, default=lambda o: o.__dict__, indent=4),
                    mimetype="json",
                    status=200,
                )
        else:
            return Response("Something went wrong", status=500)

    def post_channels(self, id, channels):
        query = f"""UPDATE tuners
            SET channels = '{json.dumps(channels)}'
            WHERE id = %s"""
        args = [id]

        if self.db_manager.run_query(query, args, return_result=False):
            return Response("Successfully updated channels", status=201)
        else:
            return Response("Something went wrong", status=500)
