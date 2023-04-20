import logging
import os

from telegram_treehole_bot import TelegramTreeholeBot

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(asctime)s - %(levelname)s - %(message)s",
)


class Config:
    RUM_SEED = "rum://seed?v=1&e=0&n=0&c=qOh_wTyuoKDoXxxxxxIaH5sa9TCLPkHCnpnROM8"
    ETH_PVTKEY = "0x5ee77ca3...effaf"
    FEED_URL_BASE = "https://example/posts/"
    TG_BOT_TOKEN = "1234566767:mybotkey"  # bot token
    TG_BOT_NAME = "@MyBotName"
    Developer = "@MyTelegramName"
    Seconds = 5  # no spam; each 5 seconds can only post one treehole
    ContentTag = "#Treehole "


if __name__ == "__main__":
    config = Config()
    TelegramTreeholeBot(config).run()
