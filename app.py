from api.tuner import TunerAPI
from flask import Flask, request, Response
from database.db_manager import DBManager
from api.tuner import TunerAPI
from api.client import ClientAPI

app = Flask(__name__)

db_manager = DBManager()
client = ClientAPI(db_manager)
tuner = TunerAPI(db_manager)


@app.route("/")
def index():
    return "Index"


@app.route("/orders", methods=["GET"])
def tuner_orders():
    id = request.args.get("id")
    return (
        tuner.get_orders(id)
        if id is not None
        else Response("Provide tuner id in args", status=400)
    )


@app.route("/orders", methods=["POST"])
def client_orders():
    id = request.args.get("id")
    orders = request.data
    return (
        client.post_orders(id, orders)
        if id is not None and orders is not b""
        else Response("Provide tuner id in args and/or orders in body", status=400)
    )


@app.route("/channels", methods=["POST"])  # TODO (priority - **)
def tuner_channels():
    return "Channels"


@app.route("/channels", methods=["GET"])  # TODO (priority - **)
def client_channels():
    return "Channels"


@app.route("/epg", methods=["POST"])  # TODO (priority - **)
def tuner_epg():
    return "Epg"


@app.route("/epg", methods=["GET"])  # TODO (priority - **)
def client_epg():
    return "Epg"


@app.route("/heartbeat", methods=["POST"])  # TODO (priority - *)
def tuner_heartbeat():
    return "Heartbeat"


@app.route("/heartbeat", methods=["GET"])  # TODO (priority - *)
def client_heartbeat():
    return "Heartbeat"


@app.route("/settings", methods=["GET"])  # TODO (priority - *)
def tuner_settings():
    return "Settings"


@app.route("/settings", methods=["POST"])  # TODO (priority - *)
def client_settings():
    return "Settings"


@app.route("/recorded", methods=["POST"])  # TODO (priority - *)
def tuner_recorded():
    return "Recorded"


@app.route("/recorded", methods=["GET"])  # TODO (priority - *)
def client_recorded():
    return "Recorded"


# temporary endpoints for some features
@app.route("/generate/database", methods=["GET"])
def generate_data():
    db_manager.generate_db_without_data()
    return "Data generated"


@app.route("/generate/example", methods=["GET"])
def generate_all():
    db_manager.generate_db_with_data()
    return "Generated tables and data"
