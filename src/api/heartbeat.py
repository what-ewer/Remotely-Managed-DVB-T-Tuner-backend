from flask import Response
import json


class HeartbeatAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_heartbeat(self, tuner_id):
        return self.__get_heartbeat(tuner_id)

    def ask_for_information(self, tuner_id, information):
        possible_information = ["changed_recording_order_list", "changed_settings",
                "need_recording_file_list", "need_epg"]
        if information not in possible_information:
            return Response(f"You can only change information for {json.dumps(possible_information)}", status=400)
        if self.__change_information(tuner_id, information):
            return Response(f"Successfully changed information needed for {information}", status=200)
        else:
            return Response(f"Something went wrong when changing information needed for {information}", status=400)
        
    def __get_heartbeat(self, tuner_id):        
        try:
            query = f"""SELECT changed_recording_order_list, changed_settings,
                need_recording_file_list, need_epg
                FROM information_needed
                WHERE tuner_id = {tuner_id}
            """
        except:
            return Response("Something went wrong", status=400)
        else:
            try:
                heartbeat = self.db_manager.execute_query(query)
            except Exception as exc:
                return Response(str(exc), status=500)

        result = [
            {"changed_recording_order_list": h[0], "changed_settings": h[1], 
                "need_recording_file_list": h[2], "need_epg": h[3]}
                for h in heartbeat
        ]

        return (
            Response(json.dumps(result), status=200, mimetype="json")
        )

    def __change_information(self, tuner_id, information):
        try:
            query = f"""UPDATE information_needed
                SET `{information}` = NOT `{information}`
                WHERE tuner_id = {tuner_id}
            """
        except Exception as exc:
            return False
        else:
            try:
                self.db_manager.execute_query(query)
            except Exception as exc:
                return False
        return True