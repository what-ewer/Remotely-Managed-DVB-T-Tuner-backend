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
        if not id:
            return Response(json.dumps({"status": False, "tuner_ids": []}), status=200)
        else:
            return Response(
                json.dumps({"status": True, "tuner_ids": self.__get_user_tuners(id)}),
                status=200,
            )

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
        return id[0][0] if id else False

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

    def register(self, username, password):
        if self.__user_already_exists(username):
            return Response(
                json.dumps({"status": False, "text": "User with username {username} already exists"}), status=200
            )
        elif self.__register_user(username, password):
            return Response(
                json.dumps({"status": False, "text": "Successfully registered {username}"}), status=200
            )
        else:
            return Response(
                json.dumps(f"Something went wrong while registering"), status=400
            )

    def __user_already_exists(self, username):
        try:
            query = f"""SELECT id FROM users
                WHERE login = '{username}'"""
        except Exception as exc:
            return True
        else:
            try:
                exists = self.db_manager.execute_query(query)
            except Exception as exc:
                return True
        return exists

    def __register_user(self, username, password):
        try:
            query = f"""INSERT INTO users (login, password)
                VALUES ('{username}', '{password}')"""
        except Exception as exc:
            return False
        else:
            try:
                registered = self.db_manager.execute_query(query)
            except Exception as exc:
                return False
        return True
