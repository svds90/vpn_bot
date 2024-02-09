import os
import requests
from dataclasses import dataclass
from typing import Any


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

    def __init__(self, server_info: dict):
        self.server_key: str = server_info.get('server_key', "")
        self.server_name: str = server_info.get('name', 'Outline server')
        self.server_id: str = server_info.get('serverId', "")
        self.server_metric_status: bool = server_info.get('metricsEnabled', False)
        self.server_created_time: int = server_info.get('createdTimestampsMs', 0)
        self.server_version: str = server_info.get('version', "")
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
        request = requests.get(f"{outline_api_url}/server", verify=False)
        server_json = request.json()
        server_json.update({"server_key": outline_api_url})

        return server_json


client = os.getenv("VPN_API_URL")
