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


@app.route("/tuner/heartbeat", methods=["POST"])  # TODO (priority - *)
def tuner_heartbeat():
    return "Heartbeat"


@app.route("/tuner/settings", methods=["GET"])  # TODO (priority - *)
def tuner_settings():
    return "Settings"


@app.route("/tuner/orders", methods=["GET"])
def tuner_orders():
    id = request.args.get("id")
    res = tuner.get_orders(id)
    return res


@app.route("/tuner/recorded", methods=["POST"])  # TODO (priority - *)
def tuner_recorded():
    return "Recorded"


@app.route("/tuner/epg", methods=["POST"])  # TODO (priority - **)
def tuner_epg():
    return "Epg"


@app.route("/tuner/channels", methods=["POST"])  # TODO (priority - **)
def tuner_channels():
    return "Channels"


@app.route("/client/heartbeat", methods=["GET"])  # TODO (priority - *)
def client_heartbeat():
    return "Heartbeat"


@app.route("/client/orders", methods=["POST"])  # TODO (priority - ***)
def client_orders():
    return "Orders"


@app.route("/client/channels", methods=["GET"])  # TODO (priority - **)
def client_channels():
    return "Channels"


# temporary endpoints for some features
@app.route("/generate/tables", methods=["GET"])  # TODO (priority - **)
def generate_tables():
    DBManager.setup_tables()
    return "Tables generated"


@app.route("/generate/data", methods=["GET"])  # TODO (priority - **)
def generate_data():
    DBManager.generate_data()
    return "Data generated"
