from datetime import datetime
from typing import List

from src.adapter import slack
from src.adapter.oncuration.api.libs.dto import OncurationDto
from src.adapter.oncuration.api.oncuration_api import OncurationApi


class OncurationService:

    def __init__(self):
        self.api: OncurationApi = OncurationApi()

    def fetch_content_list(self, page: int) -> List[str]:
        return self.api.get_content_list(page=page)

    def fetch_content(self, url: str) -> OncurationDto:
        return self.api.get_fashion_content(url=url)

    @staticmethod
    def not_exist_reference_ids(
            fetched_reference_ids: List[str],
            saved_reference_ids: List[str]
    ) -> set[str]:
        return set(fetched_reference_ids) - set(saved_reference_ids)

    @staticmethod
    def to_datetime(reference_date: str):
        try:
            return datetime.strptime(reference_date, "%Y.%m.%d")
        except ValueError:
            return datetime.now()

    @staticmethod
    def is_stop_collect(reference_date: datetime) -> bool:
        if reference_date.year < 2023:
            return True
        return False

    @staticmethod
    def update_notify(count) -> True:
        if count == 0:
            slack.send_to_slack(data="[INFO] Oncuration Update Missing")
        if count != 0:
            slack.send_to_slack(data=f"[INFO] Oncuration Update ..{count}")

    @staticmethod
    def logging(logger, data):
        _log_message = f"{datetime.now()} [Oncuration] Fetch Data ...{data}"
        logger.info(_log_message)
