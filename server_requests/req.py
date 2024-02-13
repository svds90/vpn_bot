import os
import requests
from dataclasses import dataclass, field
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
        return self.__dict__


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
    """
    Class for interacting with the Outline server
    """

    def __init__(self, outline_api_url: str):
        self.outline_api_url = outline_api_url
        self.server_info = OutlineServerInfo(self.__fetch_server_info(outline_api_url))
        self.client = OutlineClient(self.outline_api_url)

        for method_name in dir(OutlineClient):
            method = getattr(OutlineClient, method_name)
            if callable(method) and not method_name.startswith("__"):
                setattr(self, method_name, getattr(self.client, method_name))

    def __call__(self, *args, **kwargs):
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
        """
        Changes the hostname for access keys. Must be a valid hostname or IP address.
        If it's a hostname, DNS must be set up independently of this API.
        """

        requests.put(f"{self.outline_api_url}/server/hostname-for-access-keys",
                     json={"hostname": new_hostname}, verify=False)
        self.server_info.server_hostname_for_keys = new_hostname

    def rename_server(self, new_name: str) -> None:
        """
        Renames the server
        """

        requests.put(f"{self.outline_api_url}/name", json={"name": new_name}, verify=False)
        self.server_info.server_name = new_name

    def get_telemetry_status(self):
        """
        Returns whether metrics is being shared
        """

        r = requests.get(f"{self.outline_api_url}/metrics/enabled", verify=False)
        return r.json()['metricsEnabled']

    def change_telemetry_status(self, status: bool):
        """
        Enables or disables sharing of metrics
        """

        requests.put(f"{self.outline_api_url}/metrics/enabled",
                     json={"metricsEnabled": status}, verify=False)
        self.server_info.server_metric_status = status

    def change_default_port(self, port: int):
        """
        Changes the default port for newly created access keys.
        This can be a port already used for access keys.
        """

        requests.put(f"{self.outline_api_url}/server/port-for-new-access-keys",
                     json={"port": port}, verify=False)
        self.server_info.server_port_for_new_keys = port

    def set_global_data_limit(self, limit: int):
        """
        Sets a data transfer limit for all access keys
        """

        requests.put(f"{self.outline_api_url}/server/access-key-data-limit",
                     json={"limit": {"bytes": limit}}, verify=False)
        self.server_info.server_data_limit = {"limit": {"bytes": limit}}

    def disable_global_data_limit(self):
        """
        Removes the access key data limit, lifting data transfer restrictions on all access keys.
        """

        requests.delete(f"{self.outline_api_url}/server/access-key-data-limit", verify=False)
        self.server_info.server_data_limit = None


class OutlineClientInfo(OutlineBase):

    def __init__(self, user_info={}):
        self.user_id: Optional[str] = user_info.get('id', None)
        self.user_name: str = user_info.get('name', "")
        self.user_password: str = user_info.get('password', "")
        self.user_port: int = user_info.get('port', 0)
        self.user_method: str = user_info.get('method', "")
        self.user_access_url: str = user_info.get('accessUrl', "")
        self.user_data_limit: Optional[dict] = user_info.get('limit', None)


class OutlineClient(OutlineBase):

    def __init__(self, outline_api_url: str):
        self.outline_api_url = outline_api_url

    def __load_user_info(self, id: str):
        r = requests.get(f"{self.outline_api_url}/access-keys/{id}", verify=False)
        self.user_info = OutlineClientInfo(r.json())

    def get_key(self, id: str):
        self.__load_user_info(id)

    def test(self):
        self.outline_api_url = self.user_info
        self.__load_user_info() = self.__load_user_info()
        self.outline_api_url = self.__load_user_info()


outline = OutlineServer("https://192.168.67.17:28063/usBOG_wsviMFPuTOyT9F7A")
