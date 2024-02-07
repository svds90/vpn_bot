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


@dataclass
class OutlineServerInfo(OutlineBase):

    server_name: str
    server_id: str
    server_metric_status: bool
    server_created_time: int
    server_version: str
    server_port_for_new_keys: int
    server_hostname_for_keys: str


class OutlineServer(OutlineBase):
    """Class for interacting with the Outline server"""

    def __init__(self, outline_api_url: str):
        self.outline_api_url = outline_api_url

        req = requests.get(f"{outline_api_url}/server", verify=False)
        self.server_info = OutlineServerInfo(req.json())

    def __call__(self) -> str:
        return self.outline_api_url


client = os.getenv("VPN_API_URL")
