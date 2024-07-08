import logging

from module.config import Config
from module.hydro.tools import reload_stats
from module.structures import DailyJson
from module.hydro.submission import fetch_submissions
from module.hydro.ranking import fetch_rankings
from module.utils import save_json


class HydroHandler:

    def __init__(self, config: Config, url: str):
        self.config = config
        self.url = url

    def save_daily(self):
        logging.info("开始保存今日榜单")
        reload_stats(self.config, self.url, "problemStat")
        reload_stats(self.config, self.url, "rp")
        daily = DailyJson(fetch_submissions(self.config, False), fetch_rankings(self.config))
        save_json(self.config, daily)
