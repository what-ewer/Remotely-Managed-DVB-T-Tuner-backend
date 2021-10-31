from flask import Response
import json, requests


class FavoritesAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_favorite(self, username, name):
        user_id = self.__get_user_id(username)
        if user_id:
            query = f"""INSERT INTO favorites (user_id, favorite)
                VALUES({user_id}, '{name}')"""

            try:
                res = self.db_manager.execute_query(query)
            except Exception as exc:
                return Response(str(exc), status=400)

            return Response("Successfully added favorite to user", status=200)
        else:
            return Response("Couldnt recognize user", status=400)


    def get_favorites(self, username):
        query = f"""SELECT favorite
            FROM favorites
            INNER JOIN users
            ON users.id = favorites.user_id
            WHERE users.login = '{username}'"""

        try:
            res = self.db_manager.execute_query(query)
        except Exception as exc:
            return Response(str(exc), status=400)

        return Response(json.dumps(res), status=200)

    def remove_favorite(self, username, name):
        user_id = self.__get_user_id(username)
        if user_id:
            query = f"""DELETE FROM favorites
                WHERE user_id={user_id} AND favorite='{name}'"""

            try:
                res = self.db_manager.execute_query(query)
            except Exception as exc:
                return Response(str(exc), status=400)

            return Response("Successfully removed favorite to user", status=200)
        else:
            return Response("Couldnt recognize user", status=400)

        
    def __get_user_id(self, username):
        query = f"""SELECT id
            FROM users
            WHERE login = '{username}'"""

        try:
            res = self.db_manager.execute_query(query)
        except Exception as exc:
            return 0

        return res[0][0] if res else 0