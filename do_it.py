import logging

from telegram_treehole_bot import TelegramTreeholeBot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


class Config:
    RUM_SEED = "rum://seed?v=1&e=0&n=0&c=qOh_wTyuoKDoXxxxxxIaH5sa9TCLPkHCnpnROM8"
    ETH_PVTKEY = "0x5ee77ca3...effaf"
    FEED_URL_BASE = "https://example.com"
    TG_BOT_TOKEN = "1234566767:mybotkey"  # bot token
    TG_BOT_NAME = "@MyBotName"
    TG_CHANNEL_NAME = "@MyChannelName"
    TG_CHANNEL_URL = "https://t.me/MyChannelName"
    SendToChannel = True  # if True, send to channel
    Developer = "@MyTelegramName"
    Seconds = 5  # no spam; each 5 seconds can only post one treehole
    ContentTag = "#Treehole "


if __name__ == "__main__":
    config = Config()
    TelegramTreeholeBot(config).run()
