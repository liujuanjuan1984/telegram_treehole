import logging

from telegram_to_rum_bot import TelegramToRumBot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


class Config:
    USERS = []
    RUM_SEED = "rum://seed?v=1&e=0&n=0&c=qOh_wTyuoKDoXxxxxxIaH5sa9TCLPkHCnpnROM8"
    ETH_PVTKEY = "0x5ee77ca3...effaf"
    FEED_URL_BASE = "https://example.com"
    FEED_TITLE = "My Treehole"
    TG_BOT_TOKEN = "1234566767:mybotkey"  # bot token
    TG_BOT_NAME = "@MyBotName"
    Developer = "@MyTelegramName"
    Seconds = 5  # no spam; each 5 seconds can only post one treehole
    HEADER_TAG = "#Treehole "
    FOOTER_TAG = ""


if __name__ == "__main__":
    config = Config()
    TelegramToRumBot(config).run()
