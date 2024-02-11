import os
import requests
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


class OutlineServerError(Exception):
    pass


class OutlineBase:
    """Base class for all Outline instances"""

    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self


class OutlineServerInfo(OutlineBase):

    def __init__(self, server_info: Any):
        self.server_key: str = server_info.get('server_key', "")
        self.server_name: str = server_info.get('name', 'Outline server')
        self.server_id: str = server_info.get('serverId', "")
        self.server_metric_status: bool = server_info.get('metricsEnabled', False)
        self.server_created_time: str = server_info.get('createdTimestampMs', "")
        self.server_version: str = server_info.get('version', "")
        self.server_data_limit: Optional[dict] = server_info.get('accessKeyDataLimit', None)
        self.server_port_for_new_keys: int = server_info.get('portForNewAccessKeys', 0)
        self.server_hostname_for_keys: str = server_info.get('hostnameForAccessKeys', "")


class OutlineServer(OutlineBase):
    """Class for interacting with the Outline server"""

    def __init__(self, outline_api_url: str):
        self.outline_api_url = outline_api_url
        self.server_info = OutlineServerInfo(self.__fetch_server_info(outline_api_url))

    def __call__(self) -> str:
        return self.outline_api_url

    def __fetch_server_info(self, outline_api_url):

        request = requests.get(f"{outline_api_url}/server", verify=False, timeout=2)
        server_json = {
            **request.json(),
            'server_key': outline_api_url,
            'createdTimestampMs': self.__timestamp_to_date(request.json()['createdTimestampMs'])
        }

        return server_json

    def __timestamp_to_date(self, timestamp: int) -> str:
        date_time = datetime.fromtimestamp(timestamp / 1000)
        date_time = date_time.strftime("%d/%m/%y %H:%M:%S")

        return date_time

    def change_hostname(self, new_hostname: str) -> None:
        requests.put(f"{self.outline_api_url}/server/hostname-for-access-keys",
                     json={"hostname": new_hostname}, verify=False)
        self.server_info.server_hostname_for_keys = new_hostname

    def rename_server(self, new_name: str) -> None:
        requests.put(f"{self.outline_api_url}/name", json={"name": new_name}, verify=False)
        self.server_info.server_name = new_name

    def get_metrics_status(self):
        r = requests.get(f"{self.outline_api_url}/metrics/enabled", verify=False)

        return r.json()['metricsEnabled']

    def change_metrics_status(self, status: bool):
        requests.put(f"{self.outline_api_url}/metrics/enabled",
                     json={"metricsEnabled": status}, verify=False)
        self.server_info.server_metric_status = status

    def change_default_port(self, port: int):
        requests.put(f"{self.outline_api_url}/server/port-for-new-access-keys",
                     json={"port": port}, verify=False)
        self.server_info.server_port_for_new_keys = port

    def set_global_data_limit(self, limit: int):
        requests.put(f"{self.outline_api_url}/server/access-key-data-limit",
                     json={"limit": {"bytes": limit}}, verify=False)
        self.server_info.server_data_limit = {"limit": {"bytes": limit}}

    def disable_global_data_limit(self):
        requests.delete(f"{self.outline_api_url}/server/access-key-data-limit", verify=False)
        self.server_info.server_data_limit = None


class OutlineClientInfo(OutlineBase):
    pass
