from flask import Response


class UserAuth:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def verify(self, username, password, id):
        (user_id, val) = self.verify_user(username, password)
        return val and self.verify_id(id, user_id)

    def verify_user(self, username, password):
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

    def verify_id(self, id, user_id):
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
