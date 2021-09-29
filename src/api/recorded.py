from flask import Response
import json


class RecordedAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_recorded(self, id):
        query = f"""SELECT program_name, record_size FROM recorded_files
                WHERE tuner_id = {id}"""
        try:
            recorded = self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)

        result = [
            {"program_name": str(r[0]), "record_size": str(r[1])} for r in recorded
        ]
        return Response(json.dumps(result), status=200, mimetype="json")

    def post_recorded(self, id, recorded):
        for o in recorded:
            try:
                query = f"""INSERT INTO recorded_files(tuner_id, channel_id, program_name, record_size, start, end) \
                    VALUES({id}, '{o.channel_id}', '{o.program_name}', {o.record_size}, {o.start}, {o.end})"""
            except:
                return Response("Wrong record recorded list", status=400)
            else:
                try:
                    self.db_manager.execute_query(query)
                except Exception as exc:
                    return Response(str(exc), status=500)
        return Response("successfully posted recorded", status=200)
