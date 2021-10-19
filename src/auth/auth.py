from flask import Response
import json

class UserAuth:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def verify(self, username, password, id):
        (user_id, val) = self.__verify_user(username, password)
        return val and self.__verify_id(id, user_id)

    def __verify_user(self, username, password):
        try:
            query = f"""SELECT id, login, password FROM users
                WHERE login = '{username}' AND password = '{password}'"""
        except Exception as exc:
            return (-1, False)
        else:
            try:
                user = self.db_manager.execute_query(query)
            except Exception as exc:
                return (-1, False)
        return (user[0][0], True) if user else (-1, False)

    def __verify_id(self, id, user_id):
        try:
            query = f"""SELECT user_id, tuner_id
                WHERE user_id = '{user_id}' AND tuner_id = '{id}'"""
        except Exception as exc:
            return (-1, False)
        else:
            try:
                user_tuner = self.db_manager.execute_query(query)
            except Exception as exc:
                return (-1, False)
        return user_tuner

    def check_login(self, user, password):
        id = self.__get_user_id(user, password)
        print(id)
        if not id:
            return Response(json.dumps({"status": False, "tuner_ids": []}), status=400)
        else:
            return Response(json.dumps({"status": True, "tuner_ids": self.__get_user_tuners(id)}), status=200)
        
    def __get_user_id(self, user, password):
        try:
            query = f"""SELECT id FROM users
                WHERE login = '{user}' AND password = '{password}'"""
        except Exception as exc:
            return False
        else:
            try:
                id = self.db_manager.execute_query(query)
            except Exception as exc:
                return False
        return id[0][0] if id else -1

    def __get_user_tuners(self, id):
        try:
            query = f"""SELECT tuner_id FROM user_tuners
                WHERE user_id = {id}"""
        except Exception as exc:
            return []
        else:
            try:
                tuner_ids = self.db_manager.execute_query(query)
            except Exception as exc:
                return []
        return [i[0] for i in tuner_ids] if tuner_ids else []