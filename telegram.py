# import this file with:
# from <file_name> import message_type, TelegramClient

import asyncio
import logging
from collections import deque
from enum import IntEnum

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery

log = logging.getLogger("telegram_bridge")


class message_type(IntEnum):
        # исходящие сообщения
        text            = 1
        video           = 2
        image           = 3
        file            = 4

        # входящие сообщения
        callback_query  = 11
        message         = 12

    

class TelegramClient:
    """
    Для подключения модуля нужно написать:\n
    from <имя_файла> import TelegramClient, message_type\n
    Инициализировать: tg_client = Telegram_client(token)\n
    Запустить: await start_service()\n
    Остановить: await stop_service()\n
    Осуществляет обмен сообщенями с Телеграмом. Поддерживает отправку текстовых сообщений до 4КБ.\n
    Для отправки сообщения нужно написать:\n
    \tsend_message({"message_type" : message_type.text, "data" : data}),
    \tгде data = {"chat_id" : 1234567890, "text" : "qwertyy", "reply_markup" = reply_markup | None}\n
    Для получения сообщения нужно использовать get_incoming_message() -> Message | CallbackQuery | None\n
    """


    def __init__(self, token):
        self.token = token
        self.incoming_messages_queue = deque()
        self.outcoming_messages_queue = deque()
        self.bot = None
        self.dp = None
        self.background_tasks = []


    async def sender(self):
        try:
            while True:
                await asyncio.sleep(0.1)

                if len(self.outcoming_messages_queue) > 0:
                    if self.bot is not None:

                        query = self.outcoming_messages_queue[0]
                        self.outcoming_messages_queue.popleft()

                        mtype, data = query.get("message_type"), query.get("data")
                        if mtype == message_type.text:
                            chat_id = data.get("chat_id")
                            text = data.get("text")
                            reply_markup = data.get("reply_markup")
                            if len(text) <= 4096:
                                await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
                                log.info(f"Для {chat_id} отправлено сообщение" + \
                                         f"{', reply_markup присутствует.' if reply_markup is not None else '.'}")
                            else:
                                log.warning(f"сообщение слишком длинное: {text[:80]}...")

                        # сюда можно прикрутить обработку других типов сообщений
                        
                        else:
                            # Подавлять необрабатываемые сообщения
                            log.warning("сообщение не поддерживается")
        
        
        except asyncio.CancelledError:
            pass


    def is_income_queue_empty(self) -> bool:
        if len(self.incoming_messages_queue) > 0:
            return False
        return True

    def send_message(self, data : dict):
        """
        Пример использования:\n
        send_message({"message_type" : message_type.text, "data" : {"chat_id" : 1234567890, "text" : "Приветствую"}})
        """
        self.outcoming_messages_queue.append(data)

    def get_incoming_message(self) -> dict | None:
        if not self.is_income_queue_empty():
            result = self.incoming_messages_queue[0]
            self.incoming_messages_queue.popleft()

            return result
        

    async def start_service(self):
        self.dp = Dispatcher()
        bot = Bot(token=self.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.bot = bot


        @self.dp.message()
        def on_message(message : Message):
            self.incoming_messages_queue.append({"message_type" : message_type.message,
                                                 "data" : message})
            log.info(f"Пришло сообщение от {message.from_user.full_name} ({message.from_user.id}): " + \
                     f"{message.text if len(message.text) <= 80 else f'{message.text[:80]}...'}")

        @self.dp.callback_query()
        def on_callback_query(callback : CallbackQuery):
            self.incoming_messages_queue.append({"message_type" : message_type.callback_query,
                                                 "data" : callback})
            log.info(f"Пришёл CallbackQuery от {callback.from_user.full_name} ({callback.from_user.id}): " + \
                     f"{callback.data if len(callback.data) <= 80 else f'{callback.data[:80]}...'}")


        self.background_tasks.append(
            asyncio.create_task(self.dp.start_polling(self.bot))
        )
        self.background_tasks.append(
            asyncio.create_task(self.sender())
        )

        log.info("Telegram-клиент запущен")


    async def stop_service(self):
        self.dp.stop_polling()
        for task in self.background_tasks:
            task.cancel()
        await asyncio.gather(*self.background_tasks)
        log.info("Telegram-клиент остановлен")

        


