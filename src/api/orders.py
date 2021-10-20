from flask import Response
import json, datetime
from api.channels import ChannelsAPI


class OrdersAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.channel_api = ChannelsAPI(db_manager)

    def get_orders(self, id, return_list=False):
        query = f"SELECT channel_id, start, end FROM record_orders \
            WHERE tuner_id = {id}"

        ts = datetime.datetime.now().timestamp()
        try:
            orders = self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=500)

        result = [
            {"channel_id": str(o[0]), "start": o[1], "end": o[2]}
            for o in orders
            if o[2]
            > ts  # o[2] includes started programs that didn't end yet, 0[1] returns only not started
        ]

        return (
            Response(json.dumps(result), status=200, mimetype="json")
            if not return_list
            else result
        )

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
        return Response("Successfully posted orders", status=200)

    def delete_orders(self, tuner_id, order_id):
        if not self.__order_exists(order_id):
            return Response("Order doesnt exist", status=406)
        try:
            query = f"""DELETE FROM record_orders WHERE tuner_id = {tuner_id} and id = {order_id}"""
        except Exception as exc:
            return Response(str(exc), status=500)
        else:
            try:
                self.db_manager.execute_query(query)
            except Exception as exc:
                return Response(str(exc), status=500)
        return Response("Successfully deleted order", status=200)

    def __order_exists(self, order_id):
        try:
            query = f"""SELECT id FROM record_orders
            WHERE id = '{order_id}'"""
        except Exception as exc:
            return True
        else:
            try:
                id = self.db_manager.execute_query(query)
            except Exception as exc:
                return True
        return id

    def __check_overlapping(self, id, new_orders):
        orders = self.get_orders(id, True)
        channels = json.loads(self.channel_api.get_channels(id, True) or "null")
        multiplexes = {}
        muxes = set()
        if not channels:
            return True

        for c in channels:
            ch_id = c["id"]
            mux_id = c["multiplex_id"]
            muxes.add(mux_id)
            multiplexes[ch_id] = mux_id

        all_dates = [(o["start"], o["end"], o["channel_id"]) for o in orders]
        all_dates.extend([(o.start, o.end, o.channel_id) for o in new_orders])
        mux_dates = {mux_id: [] for mux_id in muxes}
        for d in all_dates:
            if d[2] not in multiplexes.keys():
                return False
            else:
                mux_dates[multiplexes[d[2]]].append((d[0], d[1]))

        for m in mux_dates.values():
            m = sorted(m, key=lambda o: o[0])
            for i in range(len(m) - 1):
                if m[i][1] > m[i + 1][0]:
                    return False
        return True
