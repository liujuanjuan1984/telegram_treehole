"""
a telegram bot
send message to rum group as content with a tag 
and signed with same private key
"""

import asyncio
import datetime
import logging

from quorum_data_py import feed
from quorum_mininode_py import MiniNode
from telegram.ext import Application, MessageHandler, filters

__version__ = "0.4.0"
logger = logging.getLogger(__name__)
logger.info("Version %s", __version__)


class TelegramToRumBot:
    """
    a telegram bot,
    send message to rum group as content with a tag
    and signed with same private key
    """

    def __init__(self, config):
        self.config = config
        self.rum = MiniNode(self.config.RUM_SEED, self.config.ETH_PVTKEY)
        self.app = Application.builder().token(self.config.TG_BOT_TOKEN).build()
        self.timer = datetime.datetime.now()

    def _get_text(self, _text):
        text = _text
        header = self.config.HEADER_TAG
        footer = self.config.FOOTER_TAG
        if header and header not in _text:
            text = header + _text
        if footer and footer not in _text:
            text += footer
        return text

    async def handle_private_chat(self, update, context):
        """send message to rum group and telegram channel"""
        logger.info("handle_private_chat %s", update.message.message_id)
        if self.config.USERS:
            if not (
                update.message.from_user.id in self.config.USERS
                or update.message.from_user.username in self.config.USERS
            ):
                await update.message.reply_text(
                    "⚠️ You are not allowed to use this bot.",
                )
                return

        _text = update.message.text or update.message.caption or ""
        _photo = update.message.photo
        text = self._get_text(_text)
        if _photo:
            image = await context.bot.get_file(_photo[-1].file_id)
            image = bytes(await image.download_as_bytearray())
        else:
            image = None
            if len(_text) > 1000 or len(_text) < 10:
                await update.message.reply_text(
                    "⚠️ Message length must be between 10 and 1000 characters.",
                )
                return

        while datetime.datetime.now() < self.timer + datetime.timedelta(
            seconds=self.config.Seconds
        ):
            await asyncio.sleep(1)

        if image:
            data = feed.new_post(content=text, images=[image])
        else:
            data = feed.new_post(content=text)

        data["origin"] = {"type": "telegram", "name": self.config.TG_BOT_NAME}

        if update.message.forward_from_chat:
            name = update.message.forward_from_chat.username
            url = f"https://t.me/{name}/{update.message.forward_from_message_id}"
            data["origin"]["name"] = name
            data["origin"]["url"] = url

        resp = self.rum.api.post_content(data)

        if "trx_id" not in resp:
            await context.bot.send_message(
                chat_id=self.config.Developer,
                text=f"send to rum failed {resp}",
            )
        self.timer = datetime.datetime.now()

        feed_url = f"{self.config.FEED_URL_BASE}/posts/{data['object']['id']}"
        logger.info("feed_url %s", feed_url)
        reply = f"⚜️ Success to blockchain.\n👉[{self.config.FEED_TITLE}]({feed_url})"

        await update.message.reply_text(reply, parse_mode="Markdown")
        logger.info("send reply done to user done.")

    def run(self):
        """run forever"""
        content_filter = (filters.TEXT | filters.PHOTO) & ~filters.COMMAND
        self.app.add_handler(
            MessageHandler(
                content_filter & filters.ChatType.PRIVATE,
                self.handle_private_chat,
            )
        )
        self.app.run_polling()
