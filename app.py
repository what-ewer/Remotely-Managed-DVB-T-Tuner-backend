from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from src.database.db_manager import DBManager
from src.database.db_model import (
    JsonConverter,
    Orders,
    Channel,
    EPG,
    Settings,
    RecordedFiles,
)
from src.api import (
    api_executor as api_ex,
    orders,
    channels,
    epg,
    recorded,
    settings,
    tuner,
    heartbeat,
    favorites,
)
from src.misc.config_parser import ConfigParser
from src.auth.auth import UserAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

config_parser = ConfigParser()
conf_params = config_parser.parse_config(
    "src/database/database.ini", "postgresql_conn_data"
)
db_manager = DBManager(conf_params)
auth_manager = UserAuth(db_manager)
heartbeat_api = heartbeat.HeartbeatAPI(db_manager)
channels_api = channels.ChannelsAPI(db_manager)
orders_api = orders.OrdersAPI(db_manager, channels_api, heartbeat_api)
settings_api = settings.SettingsAPI(db_manager, heartbeat_api)
epg_api = epg.EpgAPI(db_manager, heartbeat_api)
recorded_api = recorded.RecordedAPI(db_manager, heartbeat_api)
tuner_api = tuner.TunerAPI(db_manager)
favorites_api = favorites.FavoritesAPI(db_manager)
api_executor = api_ex.APIExecutor(JsonConverter)


@auth.verify_password
def verify_password(username, password):
    return auth_manager.verify(username, password, request.args.get("id"))


@app.route("/")
@auth.login_required
def index():
    return "Index"


# AuthAPI
@app.route("/login", methods=["GET"])
def check_login():
    return api_executor.execute_function(
        auth_manager.check_login, ["username", "password"]
    )


@app.route("/register", methods=["POST"])
def register_user():
    return api_executor.execute_function(
        auth_manager.register, ["username", "password"]
    )


# TunerAPI
@app.route("/tuner/create", methods=["POST"])
@auth.login_required
def create_tuner():
    return api_executor.execute_function(
        tuner_api.create_tuner, ["username", "tuner_name"]
    )


@app.route("/tuner/invite/add", methods=["POST"])
@auth.login_required
def invite_user():
    return api_executor.execute_function(
        tuner_api.add_user_to_tuner, ["user", "tuner_id"]
    )


@app.route("/tuner/invite/accept", methods=["POST"])
@auth.login_required
def accept_invite():
    return api_executor.execute_function(
        tuner_api.accept_invite, ["username", "tuner_id"]
    )


@app.route("/tuner/invite/decline", methods=["POST"])
@auth.login_required
def decline_invite():
    return api_executor.execute_function(
        tuner_api.decline_invite, ["username", "tuner_id"]
    )


@app.route("/tuner/users/remove", methods=["POST"])
@auth.login_required
def remove_user():
    return api_executor.execute_function(
        tuner_api.remove_user_from_tuner, ["username", "user", "tuner_id"]
    )


@app.route("/tuner/users/list", methods=["GET"])
@auth.login_required
def tuner_user_list():
    return api_executor.execute_function(tuner_api.list_users, ["username", "tuner_id"])


@app.route("/tuner/list", methods=["GET"])
@auth.login_required
def tuner_list():
    return api_executor.execute_function(tuner_api.list_tuners, ["username"])


# OrdersAPI
@app.route("/orders", methods=["POST"])
@auth.login_required
def post_orders():
    return api_executor.execute_function(
        orders_api.post_orders, ["id", "username", "password"], Orders
    )


@app.route("/orders", methods=["GET"])
@auth.login_required
def get_orders():
    return api_executor.execute_function(orders_api.get_orders, ["id"])


@app.route("/orders", methods=["DELETE"])
@auth.login_required
def delete_orders():
    return api_executor.execute_function(
        orders_api.delete_orders, ["tuner_id", "order_id"]
    )


# ChannelsAPI
@app.route("/channels", methods=["POST"])
@auth.login_required
def post_channels():
    return api_executor.execute_function(
        channels_api.post_channels, ["id"], Channel, False
    )


@app.route("/channels", methods=["GET"])
@auth.login_required
def get_channels():
    return api_executor.execute_function(channels_api.get_channels, ["id"])


# EpgAPI
@app.route("/epg", methods=["POST"])
@auth.login_required
def post_epg():
    return api_executor.execute_function(epg_api.post_epg, ["id"], EPG, False)


@app.route("/epg", methods=["GET"])
@auth.login_required
def get_epg():
    return api_executor.execute_function(epg_api.get_epg, ["id"])


# SettingsAPI
@app.route("/settings", methods=["POST"])
@auth.login_required
def post_settings():
    return api_executor.execute_function(settings_api.post_settings, ["id"], Settings)


@app.route("/settings", methods=["GET"])
@auth.login_required
def get_settings():
    return api_executor.execute_function(settings_api.get_settings, ["id"])


# Recorded API
@app.route("/recorded", methods=["POST"])
@auth.login_required
def post_recorded():
    return api_executor.execute_function(
        recorded_api.post_recorded, ["id"], RecordedFiles
    )


@app.route("/recorded", methods=["GET"])
@auth.login_required
def get_recorded():
    return api_executor.execute_function(recorded_api.get_recorded, ["id"])


# Heartbeat API
@app.route("/heartbeat", methods=["GET"])
@auth.login_required
def get_hearbeat():
    return api_executor.execute_function(heartbeat_api.get_heartbeat, ["id"])


@app.route("/heartbeat/ask", methods=["POST"])
@auth.login_required
def information_needed():
    return api_executor.execute_function(
        heartbeat_api.ask_for_information, ["id", "information"]
    )


@app.route("/heartbeat/provide", methods=["POST"])
@auth.login_required
def information_provided():
    return api_executor.execute_function(
        heartbeat_api.provide_information, ["id", "information"]
    )


# Favorites API # series: 0 - titles, 1 - episodes
@app.route("/favorites", methods=["POST"])
@auth.login_required
def add_favorite():
    return api_executor.execute_function(
        favorites_api.add_favorite, ["username", "name", "series"]
    )


@app.route("/favorites", methods=["GET"])
@auth.login_required
def get_favorites():
    return api_executor.execute_function(favorites_api.get_favorites, ["username"])


@app.route("/favorites", methods=["DELETE"])
@auth.login_required
def remove_favorite():
    return api_executor.execute_function(
        favorites_api.remove_favorite, ["username", "name", "series"]
    )


# temporary endpoints for some features
@app.route("/generate/database", methods=["POST"])
def generate_data():
    db_manager.generate_db_without_data()
    return "Data generated"


@app.route("/generate/example", methods=["POST"])
def generate_all():
    db_manager.generate_db_with_data()
    return "Generated tables and data"


if __name__ == "__main__":
    app.run()
