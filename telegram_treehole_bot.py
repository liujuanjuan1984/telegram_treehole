"""a telegram bot, send message to rum group as a treehole content"""
import datetime
import logging
import time

import telegram
from quorum_data_py import feed
from quorum_mininode_py import MiniNode
from telegram.ext import Filters, MessageHandler, Updater

__version__ = "0.1.0"
logger = logging.getLogger(__name__)
logger.info("Version %s", __version__)


class TelegramTreeholeBot:
    """a telegram bot, send message to rum group as a treehole content"""

    def __init__(self, config):
        self.config = config
        self.rum = MiniNode(self.config.RUM_SEED, self.config.ETH_PVTKEY)
        self.tg_bot = telegram.Bot(token=self.config.TG_BOT_TOKEN)
        self.updater = Updater(token=self.config.TG_BOT_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.timer = datetime.datetime.now()

    def handle_private_chat(self, update, context):
        """send message to rum group and telegram channel"""
        logger.info("handle_private_chat")

        message_id = update.message.message_id
        userid = update.message.from_user.id
        _text = update.message.text

        if _text is None or len(_text) > 1000 or len(_text) < 10:
            self.tg_bot.send_message(
                chat_id=userid,
                text="⚠️ Message length must be between 10 and 1000 characters.",
                reply_to_message_id=message_id,
            )
            return

        logger.info("sleep 5 seconds %s", self.timer)
        while datetime.datetime.now() < self.timer + datetime.timedelta(
            seconds=self.config.Seconds
        ):
            logger.info("sleep 1 second")
            time.sleep(1)

        data = feed.new_post(self.config.ContentTag + _text)
        data["origin"] = {
            "type": "telegram",
            "name": self.config.TG_BOT_NAME,
        }
        resp = self.rum.api.post_content(data)
        if "trx_id" not in resp:
            raise ValueError(
                f"send to rum failed {resp}, report to {self.config.Developer}"
            )
        self.timer = datetime.datetime.now()
        logger.info("timer %s", self.timer)

        feed_url = f"{self.config.FEED_URL_BASE}{data['object']['id']}"
        logger.info("feed_url %s", feed_url)
        reply = "📤 Success to blockchain of rum group"
        reply_markup = {
            "inline_keyboard": [[{"text": "⚜️Click here to view", "url": feed_url}]]
        }
        resp = self.tg_bot.send_message(
            chat_id=userid,
            text=reply,
            parse_mode="HTML",
            reply_markup=reply_markup,
            reply_to_message_id=message_id,
        )
        logger.info("send reply done to user done.")

    def run(self):
        """run forever"""
        self.dispatcher.add_handler(
            MessageHandler(
                Filters.text & ~Filters.command & Filters.chat_type.private,
                self.handle_private_chat,
            )
        )
        self.updater.start_polling()
        self.updater.idle()
