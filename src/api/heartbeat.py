from flask import Response
import json
from src.database.db_model import InformationNeeded


class HeartbeatAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_heartbeat(self, tuner_id):
        query = """SELECT changed_recording_order_list, changed_settings,
            need_recording_file_list, need_epg
            FROM information_needed
            WHERE tuner_id = %s"""
        args = [tuner_id]

        result = self.db_manager.run_query(query, args)
        if result:
            heartbeat = InformationNeeded(*result[0])
            return Response(
                json.dumps(heartbeat, default=lambda o: o.__dict__, indent=4),
                mimetype="json",
                status=201,
            )
        else:
            return Response("Something went wrong", status=500)

    def ask_for_information(self, tuner_id, information):
        possible_information = [
            "changed_recording_order_list",
            "changed_settings",
            "need_recording_file_list",
            "need_epg",
        ]
        if information not in possible_information:
            return Response(
                f"You can only ask for {json.dumps(possible_information)}", status=400
            )
        if self.__change_information(tuner_id, information, True):
            return Response(f"Successfully asked for {information}", status=200)
        else:
            return Response(
                f"Something went wrong when asking for {information}", status=400
            )
            
    def provide_information(self, tuner_id, information):
        possible_information = [
            "changed_recording_order_list",
            "changed_settings",
            "need_recording_file_list",
            "need_epg",
        ]
        if information not in possible_information:
            return Response(
                f"You can only provide information for {json.dumps(possible_information)}",
                status=400,
            )
        if self.__change_information(tuner_id, information, False):
            return Response(f"Successfully provided for {information}", status=200)
        else:
            return Response(
                f"Something went wrong when providing for {information}", status=400
            )

    def __change_information(self, tuner_id, information, val):
        query = f"""UPDATE information_needed
            SET {information} = %s
            WHERE tuner_id = %s
            """
        args = [val, tuner_id]

        return self.db_manager.run_query(query, args, return_result=False)
