from config import load_settings
from mqtt_bridge import MqttClient
from telegram import message_type, TelegramClient

import asyncio
import logging
import sys
import json
from base64 import b64decode, b64encode

from aiogram.utils.serialization import deserialize_telegram_object_to_python

client_mqtt = None
tg_client = None
log = None


async def transfer():
    try:
        while True:
            await asyncio.sleep(0.1)

            if not client_mqtt.is_income_queue_empty():
                json_message = client_mqtt.get_incoming_message()
                python_message = json.loads(json_message)

                mtype = python_message.get("message_type")
                # может понадобиться для системных сообщений,
                # не предназначенных для Телеграм

                tg_client.send_message(python_message)
                
                log.debug("Сообщение передано в TelegramClient")

            if not tg_client.is_income_queue_empty():
                message = tg_client.get_incoming_message()

                python_object = deserialize_telegram_object_to_python(message["data"])
                message["data"] = python_object

                json_message = json.dumps(message)

                client_mqtt.send_message(json_message)

                log.debug("Сообщение передано в MqttClient")



    except [asyncio.CancelledError, KeyboardInterrupt]:
        log.info("Выключение...")
        await client_mqtt.stop_service()
        await tg_client.stop_service()

# async def send_telegram_message(message_json, bot):
#     message_dict = json.loads(message_json)[0]
#     message = Message.model_validate(message_dict, context={'bot' : bot})
#     message.answer()

async def main():
    global client_mqtt
    global tg_client
    global log

    settings = load_settings()

    log = logging.getLogger("telegram_bridge")
    mode = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(level=mode, stream=sys.stdout,
                    format="%(asctime)s %(levelname)s %(message)s")


    client_mqtt = MqttClient(settings.mqtt_username, settings.mqtt_password,
                             settings.mqtt_broker, settings.mqtt_port)
    tg_client = TelegramClient(settings.telegram_token)

    await client_mqtt.start_service()
    await tg_client.start_service()

    await transfer()

    







if __name__ == "__main__":
    asyncio.run(main())