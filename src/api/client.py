from flask import Response
import json
from api.tuner import TunerAPI

class ClientAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.tuner = TunerAPI(self.db_manager)

    def post_orders(self, id, orders):
        if self.__check_overlapping(id, orders):
            for o in orders:
                self.post_order(id, o, True)
            return Response("successfully posted orders", status=200)
        else:
            return Response("Orders are overlapping", status=400)            

    def post_order(self, id, order, checked=False):
        try:
            if checked or self.__check_overlapping(id, order):
                query = f"""INSERT INTO record_orders(tuner_id, channel_id, start, end) \
                    VALUES({id}, '{order.channel_id}', {order.start}, {order.end})"""
        except:
            return Response("Wrong order", status=400)
        else:
            try:
                self.db_manager.execute_query(query)
            except Exception as exc:
                return Response(str(exc), status=500)
        return Response("successfully posted orders", status=200)
    
    def delete_orders(self, tuner_id, order_id):
        try:
            query = f"""DELETE FROM record_orders WHERE tuner_id = {tuner_id} and id = {order_id}"""
        except Exception as exc:
            return Response(str(exc), status=500)
        else:
            try:
                self.db_manager.execute_query(query)
            except Exception as exc:
                return Response(str(exc), status=500)
        return Response("successfully deleted order", status=200)

    def get_tuner_info(self, query, return_list=False):
        try:
            res = self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)
        res = res[0][0]
        return Response(res, status=200, mimetype='json') if not return_list else res

    def get_channels(self, id, return_list=False):
        query = f"SELECT channels FROM tuners \
            WHERE id = {id}"
        return self.get_tuner_info(query, return_list)

    def get_epg(self, id):
        query = f"SELECT epg FROM tuners \
            WHERE id = {id}"
        return self.get_tuner_info(query)

    def get_status(self, id):
        query = f"""SELECT free_space, is_recording, current_recording_time, current_recording_size FROM tuner_status
            WHERE tuner_id = {id}"""
        try:
            status = self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)

        result = [
            {
                "free_space": str(s[0]),
                "is_recording": s[1],
                "current_recording_time": str(s[2]),
                "current_recording_size": str(s[3]),
            }
            for s in status
        ]
        return Response(json.dumps(result), status=200, mimetype='json')

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
        return Response(json.dumps(result), status=200, mimetype='json')

    def post_settings(self, id, settings):
        try:
            query = f"""INSERT OR REPLACE INTO settings(tuner_id, recording_location, tvh_username, tvh_password)
                        VALUES({id}, '{settings.recording_location}', '{settings.tvh_username}', '{settings.tvh_password}')"""
        except:
            return Response("Wrong settings list", status=400)
        else:
            try:
                self.db_manager.execute_query(query)
            except Exception as exc:
                return Response(str(exc), status=500)
        return Response("successfully posted settings", status=200)

    def __check_overlapping(self, id, new_orders):
        orders = self.tuner.get_orders(id, True)
        # channels = self.get_channels(id, True)
        # print(channels)
        all_dates = [(o["start"], o["end"]) for o in orders]
        all_dates.extend([(o.start, o.end) for o in new_orders])
        all_dates = sorted(all_dates, key=lambda o: o[0])
        for i in range(len(all_dates)-1):
            if all_dates[i][1] > all_dates[i+1][0]:
                return False
        return True