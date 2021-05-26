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
        if id is not None and orders != b""
        else Response("Provide tuner id in args and orders in body", status=400)
    )


@app.route("/channels", methods=["POST"])
def tuner_channels():
    id = request.args.get("id")
    channels = request.data
    return (
        tuner.post_channels(id, channels)
        if id is not None and channels != b""
        else Response("Provide tuner id in args", status=400)
    )


@app.route("/channels", methods=["GET"])
def client_channels():
    id = request.args.get("id")
    return (
        client.get_channels(id)
        if id is not None
        else Response("Provide tuner id in args", status=400)
    )


@app.route("/epg", methods=["POST"])
def tuner_epg():
    id = request.args.get("id")
    channels = request.data
    return (
        tuner.post_epg(id, channels)
        if id is not None and channels != b""
        else Response("Provide tuner id in args", status=400)
    )


@app.route("/epg", methods=["GET"])
def client_epg():
    id = request.args.get("id")
    return (
        client.get_epg(id)
        if id is not None
        else Response("Provide tuner id in args and orders in body", status=400)
    )


@app.route("/heartbeat", methods=["POST"])
def tuner_heartbeat():
    id = request.args.get("id")
    status = request.data
    return (
        tuner.post_status(id, status)
        if id is not None and status != b""
        else Response("Provide tuner id in args and status in body", status=400)
    )


@app.route("/heartbeat", methods=["GET"])
def client_heartbeat():
    id = request.args.get("id")
    return (
        client.get_status(id)
        if id is not None
        else Response("Provide tuner id in args", status=400)
    )


@app.route("/settings", methods=["GET"])
def tuner_settings():
    id = request.args.get("id")
    return (
        tuner.get_settings(id)
        if id is not None
        else Response("Provide tuner id in args", status=400)
    )


@app.route("/settings", methods=["POST"])
def client_settings():
    id = request.args.get("id")
    settings = request.data
    return (
        client.post_settings(id, settings)
        if id is not None and settings != b""
        else Response("Provide tuner id in args and settings in body", status=400)
    )


@app.route("/recorded", methods=["POST"])
def tuner_recorded():
    id = request.args.get("id")
    recorded = request.data
    return (
        tuner.post_recorded(id, recorded)
        if id is not None and recorded != b""
        else Response("Provide tuner id in args and recored in body", status=400)
    )


@app.route("/recorded", methods=["GET"])
def client_recorded():
    id = request.args.get("id")
    return (
        client.get_recorded(id)
        if id is not None
        else Response("Provide tuner id in args", status=400)
    )


# temporary endpoints for some features
@app.route("/generate/database", methods=["GET"])
def generate_data():
    db_manager.generate_db_without_data()
    return "Data generated"


@app.route("/generate/example", methods=["GET"])
def generate_all():
    db_manager.generate_db_with_data()
    return "Generated tables and data"
