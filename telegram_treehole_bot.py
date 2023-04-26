"""a telegram bot, send message to rum group as a treehole content"""
import asyncio
import datetime
import logging

from quorum_data_py import feed
from quorum_mininode_py import MiniNode
from telegram.ext import Application, MessageHandler, filters

__version__ = "0.3.0"
logger = logging.getLogger(__name__)
logger.info("Version %s", __version__)


class TelegramTreeholeBot:
    """a telegram bot, send message to rum group as a treehole content"""

    def __init__(self, config):
        self.config = config
        self.rum = MiniNode(self.config.RUM_SEED, self.config.ETH_PVTKEY)
        self.app = Application.builder().token(self.config.TG_BOT_TOKEN).build()
        self.timer = datetime.datetime.now()

    async def handle_private_chat(self, update, context):
        """send message to rum group and telegram channel"""
        message_id = update.message.message_id
        logger.info("handle_private_chat %s", message_id)
        userid = update.message.from_user.id
        _text = update.message.text or update.message.caption or ""
        text = self.config.ContentTag + _text
        _photo = update.message.photo
        if _photo:
            image = await context.bot.get_file(_photo[-1].file_id)
            image = bytes(await image.download_as_bytearray())
            if self.config.SendToChannel:
                resp = await context.bot.send_photo(
                    chat_id=self.config.TG_CHANNEL_NAME,
                    photo=image,
                    caption=text + f"\nFrom {self.config.TG_BOT_NAME}",
                )
        else:
            image = None
            if len(_text) > 1000 or len(_text) < 10:
                await context.bot.send_message(
                    chat_id=userid,
                    text="⚠️ Message length must be between 10 and 1000 characters.",
                    reply_to_message_id=message_id,
                )
                return
            if self.config.SendToChannel:
                resp = await context.bot.send_message(
                    chat_id=self.config.TG_CHANNEL_NAME,
                    text=text + f"\nFrom {self.config.TG_BOT_NAME}",
                )

        while datetime.datetime.now() < self.timer + datetime.timedelta(
            seconds=self.config.Seconds
        ):
            await asyncio.sleep(1)
        if image:
            data = feed.new_post(content=text, images=[image])
        else:
            data = feed.new_post(content=text)

        data["origin"] = {
            "type": "telegram",
            "name": self.config.TG_BOT_NAME,
        }
        if self.config.SendToChannel:
            data["origin"]["url"] = f"{self.config.TG_CHANNEL_URL}/{resp.message_id}"

        resp = self.rum.api.post_content(data)
        if "trx_id" not in resp:
            raise ValueError(
                f"send to rum failed {resp}, report to {self.config.Developer}"
            )
        self.timer = datetime.datetime.now()

        feed_url = f"{self.config.FEED_URL_BASE}/posts/{data['object']['id']}"
        logger.info("feed_url %s", feed_url)
        reply = f"⚜️ Success to blockchain.\n👉[{self.config.FEED_TITLE}]({feed_url})"
        if self.config.SendToChannel:
            reply = +f"\n📤 View at {self.config.TG_CHANNEL_NAME}"
        resp = await context.bot.send_message(
            chat_id=userid,
            text=reply,
            parse_mode="Markdown",
            reply_to_message_id=message_id,
        )
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
