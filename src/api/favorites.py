from flask import Response
import json, requests


class FavoritesAPI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_favorite(self, username, name):
        user_id = self.__get_user_id(username)
        if user_id:
            if self.__already_favorited(user_id, name):
                return Response("Favorite already added", status=400)
            query = """INSERT INTO favorites (user_id, favorite)
                VALUES(?, ?)"""
            args = [user_id, name]

            if self.db_manager.run_query(query, args, return_result=False):
                return Response("Successfully added favorite to user", status=201)
            else:
                return Response("Something went wrong", status=500)
        else:
            return Response("Could not recognize user", status=500)

    def get_favorites(self, username):
        query = """SELECT favorite
            FROM favorites
            INNER JOIN users
            ON users.id = favorites.user_id
            WHERE users.login = ?"""
        args = [username]

        result = self.db_manager.run_query(query, args)
        if result:
            return Response(json.dumps(result), status=200)
        else:
            return Response("Something went wrong", status=500)

    def remove_favorite(self, username, name):
        user_id = self.__get_user_id(username)
        if user_id:
            if not self.__already_favorited(user_id, name):
                return Response("Favorite does not exist", status=500)

            query = """DELETE FROM favorites
                WHERE user_id = ? AND favorite = ?"""
            args = [user_id, name]
            result = self.db_manager.run_query(query, args, return_result=False)
            if result:
                return Response("Successfully removed favorite", status=200)
            else:
                return Response("Something went wrong", status=500)
        else:
            return Response("Couldnt recognize user", status=500)

    def __get_user_id(self, username):
        query = """SELECT id
            FROM users
            WHERE login = ?"""
        args = [username]

        result = self.db_manager.run_query(query, args)
        return result[0][0] if result else 0

    def __already_favorited(self, user_id, name):
        query = """SELECT *
            FROM favorites
            WHERE user_id = ? AND favorite = ?"""
        args = [user_id, name]

        result = self.db_manager.run_query(query, args)
        return result
