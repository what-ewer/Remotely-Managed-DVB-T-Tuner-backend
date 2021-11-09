from flask import Response
import json, datetime
from src.database.db_model import (
    EPG,
    JsonConverter,
    Channel,
    RecordInformation,
    RecordOrders,
)


class OrdersAPI:
    def __init__(self, db_manager, channel_api, heartbeat_api):
        self.db_manager = db_manager
        self.heartbeat = heartbeat_api
        self.channel_api = channel_api

    def get_orders(self, id):
        query = """SELECT ri.order_id,
            ri.channel_name,
            ri.channel_id,
            ri.channel_number,
            ri.start,
            ri.stop,
            ri.title,
            ri.subtitle,
            ri.summary,
            ri.description,
            ri.genres,
            ri.record_size,
            ri.file_name
            FROM record_orders AS ro
            INNER JOIN record_information as ri
            ON ro.id = ri.order_id
            WHERE tuner_id = %s"""
        args = [id]

        result = self.db_manager.run_query(query, args)
        if result:
            ts = datetime.datetime.now().timestamp()
            orders = list(
                filter(lambda o: o.stop > ts, [RecordInformation(*o) for o in result])
            )
            return Response(
                json.dumps(orders, default=lambda o: o.__dict__, indent=4),
                mimetype="json",
                status=200,
            )
        else:
            return Response("Something went wrong", status=500)

    def post_orders(self, id, username, password, orders):
        info_ids = []
        channels = self.__get_channels(id)
        if not channels:
            return Response(
                json.dumps(
                    {"ids": info_ids, "msg": "There are no channels for this tuner"}
                ),
                status=400,
            )
        (res, err_msg) = self.__check_overlapping(id, orders, channels)
        if res:
            self.heartbeat.ask_for_information(id, "changed_recording_order_list")
            for o in orders:
                order_info = self.__get_additional_information(id, o)
                if order_info:
                    order_id = self.post_order(id, o, True)
                    if order_id:
                        information_id = self.__post_additional_information(
                            order_id, order_info[0]
                        )
                        info_ids.append(information_id)
                else:
                    return Response(
                        json.dumps({"ids": info_ids, "msg": "No such program in EPG"}),
                        status=400,
                    )
            return Response(
                json.dumps({"ids": info_ids, "msg": "successfully posted orders"}),
                status=200,
            )
        else:
            return Response(
                json.dumps({"ids": info_ids, "msg": err_msg}),
                status=400,
            )

    def post_order(self, id, order, checked=False):
        if checked or self.__check_overlapping(id, order):
            query = """INSERT INTO record_orders(id, tuner_id, channel_id, start, stop)
                VALUES(DEFAULT, %s, %s, %s, %s)
                RETURNING id;"""
            args = [id, order.channel_id, order.start, order.stop]
            return self.db_manager.run_query(query, args, return_id=True)
        return 0

    def delete_orders(self, tuner_id, order_id):
        if not self.__order_exists(order_id):
            return Response("Order does not exist", status=406)
        
        if self.__is_recorded_already(tuner_id, order_id):
            return Response("The order is already recorded!", status=400)

        if self.__started_recording(tuner_id):
            return Response("The tuner already started recording order!", status=400)

        query = """DELETE FROM record_information
            WHERE order_id = %s;        
            DELETE FROM record_orders 
            WHERE tuner_id = %s AND id = %s
            RETURNING id"""
        args = [order_id, tuner_id, order_id]

        if self.db_manager.run_query(query, args, return_result=False):
            return Response("Successfully deleted order", status=200)
        else:
            return Response("Something went wrong", status=500)

    def __get_additional_information(self, id, order):
        epg = self.__get_epg(id)
        if epg:
            to_be_downloaded = list(
                filter(
                    lambda p: (
                        p.channel_uuid == order.channel_id
                        and p.start == order.start
                        and p.stop == order.stop
                    ),
                    epg,
                )
            )
            return to_be_downloaded
        return []

    def __get_epg(self, id):
        query = """SELECT epg 
            FROM tuners
            WHERE id = %s"""
        args = [id]

        result = self.db_manager.run_query(query, args)
        if result[0][0]:
            epg = JsonConverter.convert_any(result[0][0], EPG)
            return epg
        else:
            return False

    def __post_additional_information(self, order_id, info):
        query = """INSERT INTO record_information(order_id, channel_name, channel_id, channel_number, start,
            stop, title, subtitle, summary, description, genres, record_size, file_name)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, NULL)
            RETURNING order_id;"""
        args = [
            order_id,
            info.channel_name,
            info.channel_uuid,
            info.channel_number,
            info.start,
            info.stop,
            info.title,
            info.subtitle,
            info.summary,
            info.description,
            ",".join(str(g) for g in info.genre) if info.genre else "0",
        ]

        result = self.db_manager.run_query(query, args, return_id=True)
        return result

    def __order_exists(self, order_id):
        query = """SELECT id 
            FROM record_orders
            WHERE id = %s"""
        args = [order_id]

        return self.db_manager.run_query(query, args)

    def __check_overlapping(self, id, new_orders, channels):
        orders = self.__get_orders(id)
        multiplexes = {}
        muxes = set()

        for c in channels:
            ch_id = c.id
            mux_id = c.multiplex_id
            muxes.add(mux_id)
            multiplexes[ch_id] = mux_id

        all_dates = [(o.start, o.stop, o.channel_id) for o in orders]
        all_dates.extend([(o.start, o.stop, o.channel_id) for o in new_orders])
        mux_dates = {mux_id: [] for mux_id in muxes}
        for d in all_dates:
            if d[2] not in multiplexes.keys():
                return (False, "There is no such channel in channels")
            else:
                mux_dates[multiplexes[d[2]]].append((d[0], d[1]))

        for m in mux_dates.values():
            m = sorted(m, key=lambda o: o[0])
            for i in range(len(m) - 1):
                if m[i][1] > m[i + 1][0]:
                    return (False, "Orders are overlapping")
        return (True, "")

    def __get_channels(self, id):
        query = """SELECT channels 
            FROM tuners
            WHERE id = %s"""
        args = [id]

        result = self.db_manager.run_query(query, args)
        if result and result[0][0]:
            channels = JsonConverter.convert_any(result[0][0], Channel)
            return channels
        return ""

    def __get_orders(self, id):
        query = """SELECT id, channel_id, start, stop 
            FROM record_orders
            WHERE tuner_id = %s"""
        args = [id]

        result = self.db_manager.run_query(query, args)
        if result:
            ts = datetime.datetime.now().timestamp()
            orders = list(
                filter(lambda o: o.stop > ts, [RecordOrders(*o) for o in result])
            )
            return orders
        else:
            return []

    def __is_recorded_already(self, order_id, tuner_id):
        query = """SELECT order_id
            FROM recorded_files
            WHERE order_id = %s AND tuner_id = %s"""
        args = [order_id, tuner_id]

        result = self.db_manager.run_query(query, args, return_result=True)
        return result

    def __started_recording(self, order_id):
        query = """SELECT start, stop
            FROM record_orders
            WHERE id = %s"""
        args = [order_id]

        result = self.db_manager.run_query(query, args)
        if result:
            (start, stop) = result[0]
            ts = datetime.datetime.now().timestamp()
            if ts < start:
                return True
            else:
                return False            
        return True
