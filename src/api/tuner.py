from flask import Response
import json


class TunerAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def create_tuner(self, username, tuner_name):
        tuner_id = self.__create_user_tuner(tuner_name)
        if tuner_id:
            if self.__associate_tuner_with(
                username, tuner_id, "owner"
            ) and self.__add_tuner_related_information(tuner_id):
                return Response(
                    json.dumps(f"Successfully created new tuner"), status=201
                )
        return Response(
            json.dumps(f"Something went wrong while creating tuner"), status=500
        )

    def add_user_to_tuner(self, username, tuner_id):
        if self.__user_already_added(username, tuner_id):
            return Response(
                json.dumps(f"User already invited/declined or user of tuner"),
                status=400,
            )
        if self.__add_user_to_tuner(username, tuner_id):
            return Response(
                json.dumps(f"Successfully invited user to tuner"), status=201
            )
        return Response(json.dumps(f"Failed to invite user to tuner"), status=500)

    def accept_invite(self, username, tuner_id):
        res = self.__user_already_added(username, tuner_id)
        if res and len(res) == 1:
            [(uid, tid, role)] = res
            if role == "invited":
                if self.__answer_invite(uid, tid, "user"):
                    return Response(
                        json.dumps(f"Successfully accepted invite to tuner"), status=200
                    )
                else:
                    return Response(json.dumps(f"Failed to accept invite"), status=500)
            else:
                return Response(
                    json.dumps(
                        f"Cannot accept invitation to tuner, current status: {role}"
                    ),
                    status=400,
                )
        return Response(json.dumps(f"Failed to accept invite"), status=500)

    def decline_invite(self, username, tuner_id):
        res = self.__user_already_added(username, tuner_id)
        if res and len(res) == 1:
            [(uid, tid, role)] = res
            if role == "invited":
                if self.__answer_invite(uid, tid, "declined"):
                    return Response(
                        json.dumps(f"Successfully declined invite to tuner"), status=200
                    )
                else:
                    return Response(json.dumps(f"Failed to decline invite"), status=500)
            else:
                return Response(
                    json.dumps(
                        f"Cannot decline invitation to tuner, current status: {role}"
                    ),
                    status=400,
                )
        return Response(json.dumps(f"Failed to decline invite"), status=500)

    def remove_user_from_tuner(self, username, user, tuner_id):
        if not self.__is_user_owner(username, tuner_id):
            return Response(
                json.dumps("You cannot remove users if you're not owner"), status=400
            )
        if self.__is_user_of_tuner(user, tuner_id):
            if self.__remove_user_from_tuner(user, tuner_id):
                return Response(
                    json.dumps("Successfully removed user from tuner"), status=200
                )
        else:
            return Response(json.dumps("No such user for this tuner"), status=400)
        return Response(json.dumps("Failed to remove user from tuner"), status=500)

    def list_users(self, username, tuner_id):
        if not self.__is_user_of_tuner(username, tuner_id):
            return Response(
                json.dumps("You cannot list users if you're not user"), status=400
            )
        users = self.__get_users_of_tuner(tuner_id)
        if users:
            return Response(json.dumps(users), status=200)
        else:
            return Response(
                json.dumps("Failed to get a list of users from tuner"), status=400
            )

    def list_tuners(self, username):
        tuners = self.__get_tuners_of_user(username)
        if tuners:
            return Response(json.dumps(tuners), status=200)
        else:
            return Response(
                json.dumps(f"Failed to get a list of tuners of user or list is empty"),
                status=500,
            )

    def __create_user_tuner(self, tuner_name):
        query = """INSERT INTO tuners (id, tuner_name)
                VALUES (DEFAULT, %s)
                RETURNING id;"""
        args = [tuner_name]

        return self.db_manager.run_query(query, args, return_id=True)

    def __associate_tuner_with(self, username, tuner_id, role):
        query = """INSERT INTO user_tuners (user_id, tuner_id, role)
            VALUES ((SELECT id
            FROM users
            WHERE login = %s), %s, %s)
            RETURNING tuner_id;
            """
        args = [username, tuner_id, role]

        return self.db_manager.run_query(query, args, return_id=True)

    def __add_tuner_related_information(self, tuner_id):
        query = """INSERT INTO settings (tuner_id, recording_location, free_space, tvh_username, tvh_password)
            VALUES(%s, '/recordings', 0, '', '')
            RETURNING tuner_id;
            """
        query2 = """INSERT INTO information_needed (tuner_id, changed_recording_order_list, changed_settings, need_recording_file_list, need_epg)
            VALUES(%s, True, True, True, True)
            RETURNING tuner_id;
            """
        args = [tuner_id]

        return self.db_manager.run_query(
            query, args, return_id=True
        ) and self.db_manager.run_query(query2, args, return_id=True)

    def __user_already_added(self, username, tuner_id):
        query = """SELECT user_id, tuner_id, role
            FROM user_tuners
            WHERE user_id = (
                SELECT id 
                FROM users
                WHERE login = %s
            ) AND
            tuner_id = %s"""
        args = [username, tuner_id]

        return self.db_manager.run_query(query, args)

    def __add_user_to_tuner(self, username, tuner_id):
        query = """INSERT INTO user_tuners (user_id, tuner_id, role)
                VALUES ((SELECT id
                FROM users
                WHERE login = %s), %s, 'invited')
            RETURNING user_id, tuner_id;
                """
        args = [username, tuner_id]

        return self.db_manager.run_query(query, args, return_id=True)

    def __answer_invite(self, user_id, tuner_id, status):
        query = """UPDATE user_tuners
            SET role = %s
            WHERE user_id = %s AND tuner_id = %s
            RETURNING role;
            """
        args = [status, user_id, tuner_id]

        return self.db_manager.run_query(query, args, return_id=True)

    def __is_user_owner(self, username, tuner_id):
        query = """SELECT user_id, tuner_id, role
            FROM user_tuners
            WHERE user_id = (
                SELECT id 
                FROM users
                WHERE login = %s
            ) AND
            tuner_id = %s
            AND role = 'owner'"""
        args = [username, tuner_id]

        return self.db_manager.run_query(query, args)

    def __is_user_of_tuner(self, username, tuner_id):
        query = """SELECT user_id, tuner_id, role
            FROM user_tuners
            WHERE user_id = (
                SELECT id 
                FROM users
                WHERE login = %s
            ) AND
            tuner_id = %s"""
        args = [username, tuner_id]

        return self.db_manager.run_query(query, args)

    def __remove_user_from_tuner(self, username, tuner_id):
        query = """DELETE FROM user_tuners
            WHERE user_id = (
                SELECT id 
                FROM users
                WHERE login = %s
            ) AND
            tuner_id = %s"""
        args = [username, tuner_id]

        return self.db_manager.run_query(query, args, return_result=False)

    def __get_tuners_of_user(self, username):
        query = f"""SELECT user_tuners.tuner_id, tuners.tuner_name, user_tuners.role
            FROM user_tuners
            INNER JOIN tuners
            ON tuners.id = user_tuners.tuner_id
            WHERE user_tuners.user_id = (
                SELECT id 
                FROM users
                WHERE login = %s
            )"""
        args = [username]

        return self.db_manager.run_query(query, args)

    def __get_users_of_tuner(self, tuner_id):
        query = """SELECT user_tuners.user_id, users.login, user_tuners.role
            FROM user_tuners
            INNER JOIN users
            ON users.id = user_tuners.user_id
            WHERE user_tuners.tuner_id = %s"""
        args = [tuner_id]

        return self.db_manager.run_query(query, args)
