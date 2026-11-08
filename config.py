import os
from dataclasses import dataclass

from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings():
    telegram_token : str
    mqtt_broker : str | None
    mqtt_port : int | None
    mqtt_username : str | None
    mqtt_password : str | None
    client_id : str | None
    mqtt_topic_outgoing : str | None
    mqtt_topic_income : str | None
    key_phrase : str | None
    flask_port : int
    debug : bool

def load_settings() -> Settings:
    load_dotenv()

    return Settings(
        telegram_token = os.environ["TOKEN"],
        mqtt_broker = os.environ.get("MQTT_BROKER") or None,
        mqtt_port = int(os.environ.get("MQTT_PORT")) or None,
        mqtt_username = os.environ.get("MQTT_USERNAME") or None,
        mqtt_password = os.environ.get("MQTT_PASSWORD") or None,
        client_id = os.environ.get("CLIENT_ID") or None,
        mqtt_topic_outgoing = os.environ.get("MQTT_TOPIC_OUTGOING") or None,
        mqtt_topic_income = os.environ.get("MQTT_TOPIC_INCOME") or None,
        key_phrase = os.environ.get("MYSQL_DATABASE") or None,
        flask_port = int(os.environ.get("FLASK_PORT")),
        debug = bool(os.environ.get("DEBUG"))
    )