from flask import Flask, request, Response
from flask_httpauth import HTTPBasicAuth
from src.database.db_manager import DBManager
from src.database.db_model import (
    JsonConverter,
    RecordOrders,
    Channel,
    EPG,
    TunerStatus,
    Settings,
    RecordedFiles,
    User,
)
from src.api import (
    orders,
    channels,
    epg,
    status,
    recorded,
    settings,
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

#AuthAPI
@app.route("/login", methods=["GET"])
def check_login():
    return auth_manager.check_login(request.authorization.get("username"), request.authorization.get("password"))


@app.route("/register", methods=["POST"])
def register_user():
    return auth_manager.register(request.authorization.get("username"), request.authorization.get("password"))

# OrdersAPI
@app.route("/orders", methods=["POST"])
@auth.login_required
def client_orders():
    return execute_function(orders_api.post_orders, ["id"], RecordOrders)


@app.route("/orders", methods=["GET"])
@auth.login_required
def tuner_orders():
    return execute_function(orders_api.get_orders, ["id"])


@app.route("/orders", methods=["DELETE"])
@auth.login_required
def delete_orders():
    return execute_function(orders_api.delete_orders, ["tuner_id", "order_id"])


# ChannelsAPI
@app.route("/channels", methods=["POST"])
@auth.login_required
def tuner_channels():
    return execute_function(channels_api.post_channels, ["id"], Channel, False)


@app.route("/channels", methods=["GET"])
@auth.login_required
def client_channels():
    return execute_function(channels_api.get_channels, ["id"])


# EpgAPI
@app.route("/epg", methods=["POST"])
@auth.login_required
def tuner_epg():
    return execute_function(epg_api.post_epg, ["id"], EPG, False)


@app.route("/epg", methods=["GET"])
@auth.login_required
def client_epg():
    return execute_function(epg_api.get_epg, ["id"])


# StatusAPI
@app.route("/status", methods=["POST"])
@auth.login_required
def tuner_status():
    return execute_function(status_api.post_status, ["id"], TunerStatus)


@app.route("/status", methods=["GET"])
@auth.login_required
def client_status():
    return execute_function(status_api.get_status, ["id"])


# SettingsAPI
@app.route("/settings", methods=["POST"])
@auth.login_required
def client_settings():
    return execute_function(settings_api.post_settings, ["id"], Settings)


@app.route("/settings", methods=["GET"])
@auth.login_required
def tuner_settings():
    return execute_function(settings_api.get_settings, ["id"])


# Recorded API
@app.route("/recorded", methods=["POST"])
@auth.login_required
def tuner_recorded():
    return execute_function(recorded_api.post_recorded, ["id"], RecordedFiles)


@app.route("/recorded", methods=["GET"])
@auth.login_required
def client_recorded():
    return execute_function(recorded_api.get_recorded, ["id"])


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
