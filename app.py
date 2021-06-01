from api.tuner import TunerAPI
from flask import Flask, request, Response
from database.db_manager import DBManager
from database.db_model import (
    JsonConverter,
    RecordOrders,
    Channel,
    EPG,
    TunerStatus,
    Settings,
    RecordedFiles,
)
from api.tuner import TunerAPI
from api.client import ClientAPI

app = Flask(__name__)

db_manager = DBManager()
client = ClientAPI(db_manager)
tuner = TunerAPI(db_manager)


@app.route("/")
def index():
    return "Index"


@app.route("/orders", methods=["POST"])
def client_orders():
    id = request.args.get("id")
    orders = JsonConverter.convert_all(request.data, RecordOrders)
    if id and orders:
        response = client.post_orders(id, orders)
    else:
        response = Response("Provide tuner id in args and orders in body", status=400)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/orders", methods=["GET"])
def tuner_orders():
    id = request.args.get("id")
    if id:
        response = tuner.get_orders(id)
    else:
        response = Response("Provide tuner id in args", status=400)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/channels", methods=["POST"])
def tuner_channels():
    id = request.args.get("id")
    channels = JsonConverter.check_json(request.data, Channel)
    return (
        tuner.post_channels(id, channels)
        if id and channels
        else Response("Provide tuner id in args and channels in body", status=400)
    )


@app.route("/channels", methods=["GET"])
def client_channels():
    id = request.args.get("id")
    return (
        client.get_channels(id)
        if id
        else Response("Provide tuner id in args", status=400)
    )


@app.route("/epg", methods=["POST"])
def tuner_epg():
    id = request.args.get("id")
    epg = JsonConverter.check_json(request.data, EPG)
    return (
        tuner.post_epg(id, epg)
        if id and epg
        else Response("Provide tuner id in args and orders in body", status=400)
    )


@app.route("/epg", methods=["GET"])
def client_epg():
    id = request.args.get("id")
    if id:
        response = client.get_epg(id)
    else:
        response = Response("Provide tuner id in args", status=400)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/status", methods=["POST"])
def tuner_status():
    id = request.args.get("id")
    status = JsonConverter.convert(request.data, TunerStatus)
    return (
        tuner.post_status(id, status)
        if id and status
        else Response("Provide tuner id in args and status in body", status=400)
    )


@app.route("/status", methods=["GET"])
def client_status():
    id = request.args.get("id")
    return (
        client.get_status(id)
        if id
        else Response("Provide tuner id in args", status=400)
    )


@app.route("/settings", methods=["POST"])
def client_settings():
    id = request.args.get("id")
    settings = JsonConverter.convert(request.data, Settings)
    return (
        client.post_settings(id, settings)
        if id and settings
        else Response("Provide tuner id in args and settings in body", status=400)
    )


@app.route("/settings", methods=["GET"])
def tuner_settings():
    id = request.args.get("id")
    return (
        tuner.get_settings(id)
        if id
        else Response("Provide tuner id in args", status=400)
    )


@app.route("/recorded", methods=["POST"])
def tuner_recorded():
    id = request.args.get("id")
    recorded = JsonConverter.convert_all(request.data, RecordedFiles)
    return (
        tuner.post_recorded(id, recorded)
        if id and recorded
        else Response("Provide tuner id in args and recored in body", status=400)
    )


@app.route("/recorded", methods=["GET"])
def client_recorded():
    id = request.args.get("id")
    return (
        client.get_recorded(id)
        if id
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
