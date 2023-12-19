from datetime import datetime
from typing import List

from src.adapter import slack
from src.adapter.seoulinspired.api.libs.dto import SeoulInspiredDto
from src.adapter.seoulinspired.api.seoulinspired_api import SeoulInspiredApi


class SeoulInspiredService:
    def __init__(self):
        self.api: SeoulInspiredApi = SeoulInspiredApi()

    def fetch_links(self, page: int) -> List[str]:
        return self.api.get_links(page=page)

    def fetch_content(self, url: str) -> SeoulInspiredDto:
        return self.api.emit(url=url)

    @staticmethod
    def not_exist_reference_ids(
            fetched_reference_ids: List[int],
            saved_reference_ids: List[int]
    ) -> set[int]:
        return set(fetched_reference_ids) - set(saved_reference_ids)

    @staticmethod
    def to_datetime(reference_date: str):
        try:
            return datetime.strptime(reference_date, "%Y. %m. %d. %H:%M")
        except ValueError:
            return datetime.now()

    @staticmethod
    def is_reference_date_matching(reference_date: datetime) -> bool:
        if reference_date.year >= 2023:
            return True
        return False

    @staticmethod
    def to_datetime(reference_date: str):
        return datetime.strptime(reference_date, '%Y-%m-%d')

    @staticmethod
    def update_notify(count) -> True:
        if count == 0:
            slack.send_to_slack(data="[INFO] SeoulInspired Update Missing")
        if count != 0:
            slack.send_to_slack(data=f"[INFO] SeoulInspired Update ..{count}")

    @staticmethod
    def logging(logger, data):
        _log_message = f"{datetime.now()} [SeoulInspired] Fetch Data ...{data}"
        logger.info(_log_message)
