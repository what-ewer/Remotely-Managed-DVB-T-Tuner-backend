from flask import Response
import json


class TunerAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_tuner(self, username, tuner_name):
        tuner_id = self.__create_user_tuner(tuner_name)
        if tuner_id:
            if self.__associate_tuner_with(username, tuner_id, "owner"):
                return Response(
                    json.dumps(f"Successfully created new tuner"), status=200
                )
        return Response(
            json.dumps(f"Something went wrong while creating tuner"), status=400
        )

    def add_user_to_tuner(self, username, tuner_id):
        if self.__user_already_added(username, tuner_id):
            return Response(
                json.dumps(f"User already invited/declined or user of tuner"),
                status=400,
            )
        if self.__add_user_to_tuner(username, tuner_id):
            return Response(
                json.dumps(f"Successfully invited user to tuner"), status=200
            )
        return Response(json.dumps(f"Failed to invite user to tuner"), status=400)

    def accept_invite(self, username, tuner_id):
        res = self.__user_already_added(username, tuner_id)
        if res and len(res) == 1:
            [(uid, tid, role)] = res
            if role == "invited":
                if self.__answer_invite(uid, tid, "user"):
                    return
                else:
                    return Response(
                        json.dumps(f"Successfully accepted invite to tuner"), status=200
                    )
            else:
                return Response(
                    json.dumps(
                        f"Cannot accept invitation to tuner, current status: {role}"
                    ),
                    status=400,
                )
        return Response(json.dumps(f"Failed to accept invite"), status=400)

    def decline_invite(self, username, tuner_id):
        res = self.__user_already_added(username, tuner_id)
        if res and len(res) == 1:
            [(uid, tid, role)] = res
            if role == "invited":
                if self.__answer_invite(uid, tid, "declined"):
                    return
                else:
                    return Response(
                        json.dumps(f"Successfully accepted invite to tuner"), status=200
                    )
            else:
                return Response(
                    json.dumps(
                        f"Cannot accept invitation to tuner, current status: {role}"
                    ),
                    status=400,
                )
        return Response(json.dumps(f"Failed to accept invite"), status=400)

    def remove_user_from_tuner(self, username, user, tuner_id):
        if not self.__is_user_owner(username, tuner_id):
            return Response(
                json.dumps(f"You cannot remove users if you're not owner"), status=400
            )
        if self.__is_user_of_tuner(user, tuner_id):
            if self.__remove_user_from_tuner(user, tuner_id):
                return Response(
                    json.dumps(f"Successfully removed user from tuner"), status=200
                )
        else:
            return Response(json.dumps(f"No such user for this tuner"), status=400)
        return Response(json.dumps(f"Failed to remove user from tuner"), status=400)

    def list_users(self, username, tuner_id):
        if not self.__is_user_of_tuner(username, tuner_id):
            return Response(
                json.dumps(f"You cannot list users if you're not user"), status=400
            )
        users = self.__get_users_of_tuner(tuner_id)
        if users:
            return Response(json.dumps(users), status=200)
        else:
            return Response(
                json.dumps(f"Failed to get a list of users from tuner"), status=400
            )

    def list_tuners(self, username):
        tuners = self.__get_tuners_of_user(username)
        if tuners:
            return Response(json.dumps(tuners), status=200)
        else:
            return Response(
                json.dumps(f"Failed to get a list of tuners of user or list is empty"),
                status=400,
            )

    def __create_user_tuner(self, tuner_name):
        try:
            query = f"""INSERT INTO tuners (tuner_name)
                VALUES ('{tuner_name}')"""
        except Exception as exc:
            return 0
        else:
            try:
                registered = self.db_manager.execute_query(query, True)
            except Exception as exc:
                return 0
        return registered

    def __associate_tuner_with(self, username, tuner_id, role):
        try:
            query = f"""INSERT INTO user_tuners (user_id, tuner_id, role)
                VALUES ((SELECT id
                FROM users
                WHERE login = '{username}'), {tuner_id}, '{role}')
                """
        except Exception as exc:
            return False
        else:
            try:
                registered = self.db_manager.execute_query(query, True)
                print(registered)
            except Exception as exc:
                return False
        return registered

    def __user_already_added(self, username, tuner_id):
        try:
            query = f"""SELECT user_id, tuner_id, role
            FROM user_tuners
            WHERE user_id = (
                SELECT id 
                FROM users
                WHERE login = '{username}'
            ) AND
            tuner_id = {tuner_id}"""
        except Exception as exc:
            return False
        else:
            try:
                added = self.db_manager.execute_query(query)
            except Exception as exc:
                return False
        return added

    def __add_user_to_tuner(self, username, tuner_id):
        try:
            query = f"""INSERT INTO user_tuners (user_id, tuner_id, role)
                VALUES ((SELECT id
                FROM users
                WHERE login = '{username}'), {tuner_id}, 'invited')
                """
        except Exception as exc:
            return False
        else:
            try:
                registered = self.db_manager.execute_query(query, True)
            except Exception as exc:
                return False
        return registered

    def __answer_invite(self, user_id, tuner_id, status):
        try:
            query = f"""UPDATE user_tuners
                SET role = '{status}'
                WHERE user_id = {user_id} AND tuner_id = {tuner_id}
                """
        except Exception as exc:
            return False
        else:
            try:
                registered = self.db_manager.execute_query(query, True)
            except Exception as exc:
                return False
        return registered

    def __is_user_owner(self, username, tuner_id):
        try:
            query = f"""SELECT user_id, tuner_id, role
            FROM user_tuners
            WHERE user_id = (
                SELECT id 
                FROM users
                WHERE login = '{username}'
            ) AND
            tuner_id = {tuner_id}
            AND role = 'owner'"""
        except Exception as exc:
            return False
        else:
            try:
                added = self.db_manager.execute_query(query)
            except Exception as exc:
                return False
        return added

    def __is_user_of_tuner(self, username, tuner_id):
        try:
            query = f"""SELECT user_id, tuner_id, role
            FROM user_tuners
            WHERE user_id = (
                SELECT id 
                FROM users
                WHERE login = '{username}'
            ) AND
            tuner_id = {tuner_id}"""
        except Exception as exc:
            return False
        else:
            try:
                added = self.db_manager.execute_query(query)
            except Exception as exc:
                return False
        return added

    def __remove_user_from_tuner(self, username, tuner_id):
        try:
            query = f"""DELETE FROM user_tuners
            WHERE user_id = (
                SELECT id 
                FROM users
                WHERE login = '{username}'
            ) AND
            tuner_id = {tuner_id}"""
        except Exception as exc:
            return False
        else:
            try:
                self.db_manager.execute_query(query)
                return True
            except Exception as exc:
                return False

    def __get_tuners_of_user(self, username):
        try:
            query = f"""SELECT user_tuners.tuner_id, tuners.tuner_name, user_tuners.role
            FROM user_tuners
            INNER JOIN tuners
            ON tuners.id = user_tuners.tuner_id
            WHERE user_tuners.user_id = (
                SELECT id 
                FROM users
                WHERE login = '{username}'
            )"""
        except Exception as exc:
            return False
        else:
            try:
                tuners = self.db_manager.execute_query(query)
            except Exception as exc:
                print(exc)
                return False
        return tuners

    def __get_users_of_tuner(self, tuner_id):
        try:
            query = f"""SELECT user_tuners.user_id, users.login, user_tuners.role
            FROM user_tuners
            INNER JOIN users
            ON users.id = user_tuners.user_id
            WHERE user_tuners.tuner_id = {tuner_id}"""
        except Exception as exc:
            return False
        else:
            try:
                users = self.db_manager.execute_query(query)
            except Exception as exc:
                return False
        return users
