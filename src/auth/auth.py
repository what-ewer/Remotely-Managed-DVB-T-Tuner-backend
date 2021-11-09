from flask import Response
import json


class UserAuth:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def verify(self, username, password, id):
        (user_id, val) = self.__verify_user(username, password)
        return val and self.__verify_id(id, user_id)

    def register(self, username, password):
        if self.__user_already_exists(username):
            return Response(
                json.dumps(
                    {
                        "status": False,
                        "text": f"User with username {username} already exists",
                    }
                ),
                status=400,
            )
        elif self.__register_user(username, password):
            return Response(
                json.dumps(
                    {"status": True, "text": f"Successfully registered {username}"}
                ),
                status=201,
            )
        else:
            return Response(
                json.dumps(f"Something went wrong while registering"), status=500
            )

    def check_login(self, user, password):
        id = self.__get_user_id(user, password)
        if id:
            return Response(
                json.dumps({"status": True, "tuner_ids": self.__get_user_tuners(id)}),
                status=200,
            )
        else:
            return Response(json.dumps({"status": False, "tuner_ids": []}), status=200)

    def __verify_user(self, username, password):
        query = """SELECT id, login, password 
            FROM users
            WHERE login = %s AND password = %s"""
        args = [username, password]

        result = self.db_manager.run_query(query, args)
        return (result[0][0], True) if result else (-1, False)

    def __verify_id(self, id, user_id):
        query = """SELECT user_id, tuner_id
            FROM user_tuners
            WHERE user_id = %s AND tuner_id = %s"""
        args = [user_id, id]

        result = self.db_manager.run_query(query, args)
        return result if result else (-1, False)

    def __get_user_id(self, user, password):
        query = """SELECT id 
            FROM users
            WHERE login = %s AND password = %s"""
        args = [user, password]

        result = self.db_manager.run_query(query, args)
        return result[0][0] if result else 0

    def __get_user_tuners(self, id):
        query = """SELECT tuner_id 
            FROM user_tuners
            WHERE user_id = %s"""
        args = [id]

        result = self.db_manager.run_query(query, args)
        return [r[0] for r in result] if result else []

    def __user_already_exists(self, username):
        query = """SELECT id 
            FROM users
            WHERE login = %s"""
        args = [username]

        return self.db_manager.run_query(query, args)

    def __register_user(self, username, password):
        query = """INSERT INTO users (id, login, password)
                VALUES (DEFAULT, %s, %s)
            RETURNING id;"""
        args = [username, password]

        return self.db_manager.run_query(query, args, return_result=False)
