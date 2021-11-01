from flask import Flask, request, Response
from flask_httpauth import HTTPBasicAuth
from src.database.db_manager import DBManager
from src.database.db_model import (
    JsonConverter,
    Orders,
    Channel,
    EPG,
    TunerStatus,
    Settings,
    RecordedFiles,
)
from src.api import (
    orders,
    channels,
    epg,
    status,
    recorded,
    settings,
    tuner,
    heartbeat,
    favorites,
)
from src.auth.auth import UserAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

db_manager = DBManager()
auth_manager = UserAuth(db_manager)
orders_api = orders.OrdersAPI(db_manager)
channels_api = channels.ChannelsAPI(db_manager)
epg_api = epg.EpgAPI(db_manager)
status_api = status.StatusAPI(db_manager)
recorded_api = recorded.RecordedAPI(db_manager)
settings_api = settings.SettingsAPI(db_manager)
tuner_api = tuner.TunerAPI(db_manager)
heartbeat_api = heartbeat.HeartbeatAPI(db_manager)
favorites_api = favorites.FavoritesAPI(db_manager)


@auth.verify_password
def verify_password(username, password):
    return auth_manager.verify(username, password, request.args.get("id"))


def execute_function(function, args=None, data_class=None, convert=True):
    res_args = check_args(args)
    if isinstance(res_args, Response):
        return res_args
    elif data_class:
        json_data = get_json(data_class, convert)
        if json_data:
            res_args.append(json_data)
        else:
            return Response(
                "Required data for api doesn't provide needed class", status=400
            )

    return get_function_response(function, res_args)


def get_function_response(function, args):
    return function(*args)


def check_args(args):
    args_values = []
    missing_args = []
    for arg in args:
        if arg == "username" or arg == "password":
            arg_val = request.authorization.get(arg)
        else:
            arg_val = request.args.get(arg)
        args_values.append(arg_val)
        if not arg_val:
            missing_args.append(arg)

    return (
        Response(f"Provide arguements for {missing_args}", status=400)
        if missing_args
        else args_values
    )


def get_json(data_class, convert):
    data = request.data
    if convert:
        return JsonConverter.convert_any(data, data_class)
    else:
        return JsonConverter.check_json(data, data_class)


@app.route("/")
@auth.login_required
def index():
    return "Index"


# AuthAPI
@app.route("/login", methods=["GET"])
def check_login():
    return execute_function(auth_manager.check_login, ["username", "password"])


@app.route("/register", methods=["POST"])
def register_user():
    return execute_function(auth_manager.register, ["username", "password"])


# TunerAPI
@app.route("/tuner/create", methods=["POST"])
@auth.login_required
def create_tuner():
    return execute_function(tuner_api.create_tuner, ["username", "tuner_name"])


@app.route("/tuner/invite/add", methods=["POST"])
@auth.login_required
def invite_user():
    return execute_function(tuner_api.add_user_to_tuner, ["user", "tuner_id"])


@app.route("/tuner/invite/accept", methods=["POST"])
@auth.login_required
def accept_invite():
    return execute_function(tuner_api.accept_invite, ["username", "tuner_id"])


@app.route("/tuner/invite/decline", methods=["POST"])
@auth.login_required
def decline_invite():
    return execute_function(tuner_api.decline_invite, ["username", "tuner_id"])


@app.route("/tuner/users/remove", methods=["POST"])
@auth.login_required
def remove_user():
    return execute_function(
        tuner_api.remove_user_from_tuner, ["username", "user", "tuner_id"]
    )


@app.route("/tuner/users/list", methods=["GET"])
@auth.login_required
def tuner_user_list():
    return execute_function(tuner_api.list_users, ["username", "tuner_id"])


@app.route("/tuner/list", methods=["GET"])
@auth.login_required
def tuner_list():
    return execute_function(tuner_api.list_tuners, ["username"])


# OrdersAPI
@app.route("/orders", methods=["POST"])
@auth.login_required
def post_orders():
    return execute_function(
        orders_api.post_orders, ["id", "username", "password"], Orders
    )


@app.route("/orders", methods=["GET"])
@auth.login_required
def get_orders():
    return execute_function(orders_api.get_orders, ["id"])


@app.route("/orders", methods=["DELETE"])
@auth.login_required
def delete_orders():
    return execute_function(orders_api.delete_orders, ["tuner_id", "order_id"])


# ChannelsAPI
@app.route("/channels", methods=["POST"])
@auth.login_required
def post_channels():
    return execute_function(channels_api.post_channels, ["id"], Channel, False)


@app.route("/channels", methods=["GET"])
@auth.login_required
def get_channels():
    return execute_function(channels_api.get_channels, ["id"])


# EpgAPI
@app.route("/epg", methods=["POST"])
@auth.login_required
def post_epg():
    return execute_function(
        epg_api.post_epg, ["id", "username", "password"], EPG, False
    )


@app.route("/epg", methods=["GET"])
@auth.login_required
def get_epg():
    return execute_function(epg_api.get_epg, ["id"])


# StatusAPI
@app.route("/status", methods=["POST"])
@auth.login_required
def post_status():
    return execute_function(status_api.post_status, ["id"], TunerStatus)


@app.route("/status", methods=["GET"])
@auth.login_required
def get_status():
    return execute_function(status_api.get_status, ["id"])


# SettingsAPI
@app.route("/settings", methods=["POST"])
@auth.login_required
def post_settings():
    return execute_function(
        settings_api.post_settings, ["id", "username", "password"], Settings
    )


@app.route("/settings", methods=["GET"])
@auth.login_required
def get_settings():
    return execute_function(settings_api.get_settings, ["id"])


# Recorded API
@app.route("/recorded", methods=["POST"])
@auth.login_required
def post_recorded():
    return execute_function(recorded_api.post_recorded, ["id"], RecordedFiles)


@app.route("/recorded", methods=["GET"])
@auth.login_required
def get_recorded():
    return execute_function(recorded_api.get_recorded, ["id"])


# Heartbeat API
@app.route("/heartbeat", methods=["GET"])
@auth.login_required
def get_hearbeat():
    return execute_function(heartbeat_api.get_heartbeat, ["id"])


@app.route("/heartbeat/ask", methods=["POST"])
@auth.login_required
def information_needed():
    return execute_function(heartbeat_api.ask_for_information, ["id", "information"])


@app.route("/heartbeat/provide", methods=["POST"])
@auth.login_required
def information_provided():
    return execute_function(heartbeat_api.provide_information, ["id", "information"])


# Favorites API
@app.route("/favorites", methods=["POST"])
@auth.login_required
def add_favorite():
    return execute_function(favorites_api.add_favorite, ["username", "name"])


@app.route("/favorites", methods=["GET"])
@auth.login_required
def get_favorites():
    return execute_function(favorites_api.get_favorites, ["username"])


@app.route("/favorites", methods=["DELETE"])
@auth.login_required
def remove_favorite():
    return execute_function(favorites_api.remove_favorite, ["username", "name"])


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
