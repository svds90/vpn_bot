import os
import requests
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


class OutlineServerError(Exception):
    pass


class OutlineBase:
    """
    Base class for all Outline instances
    """

    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]


class OutlineServerInfo(OutlineBase):

    def __init__(self, server_info: Any):
        print("init OutlineServerInfo")
        self.key: str = server_info.get('server_key', "")
        self.name: str = server_info.get('name', 'Outline server')
        self.id: str = server_info.get('serverId', "")
        self.metric_status: bool = server_info.get('metricsEnabled', False)
        self.created_time: str = server_info.get('createdTimestampMs', "")
        self.version: str = server_info.get('version', "")
        self.data_limit: Optional[dict] = server_info.get('accessKeyDataLimit', None)
        self.port_for_new_keys: int = server_info.get('portForNewAccessKeys', 0)
        self.hostname_for_keys: str = server_info.get('hostnameForAccessKeys', "")

    def __call__(self):
        return self.__dict__


class OutlineServer(OutlineBase):
    """
    Class for interacting with the Outline server
    """

    def __init__(self, outline_api_url: str):
        print("init OutlineServer")
        self.outline_api_url = outline_api_url
        self.server_info = OutlineServerInfo(self.__fetch_server_info(outline_api_url))
        OutlineClient(self.outline_api_url)

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

    def server_change_hostname(self, new_hostname: str) -> None:
        """
        Changes the hostname for access keys. Must be a valid hostname or IP address.
        If it's a hostname, DNS must be set up independently of this API.
        """

        requests.put(f"{self.outline_api_url}/server/hostname-for-access-keys",
                     json={"hostname": new_hostname}, verify=False)
        self.server_info.hostname_for_keys = new_hostname

    def server_rename(self, new_name: str) -> None:
        """
        Renames the server
        """

        requests.put(f"{self.outline_api_url}/name", json={"name": new_name}, verify=False)
        self.server_info.name = new_name

    def server_get_telemetry_status(self):
        """
        Returns whether metrics is being shared
        """

        r = requests.get(f"{self.outline_api_url}/metrics/enabled", verify=False)
        return r.json()['metricsEnabled']

    def server_change_telemetry_status(self, status: bool):
        """
        Enables or disables sharing of metrics
        """

        requests.put(f"{self.outline_api_url}/metrics/enabled",
                     json={"metricsEnabled": status}, verify=False)
        self.server_info.metric_status = status

    def server_change_default_port(self, port: int):
        """
        Changes the default port for newly created access keys.
        This can be a port already used for access keys.
        """

        requests.put(f"{self.outline_api_url}/server/port-for-new-access-keys",
                     json={"port": port}, verify=False)
        self.server_info.port_for_new_keys = port

    def server_set_global_data_limit(self, limit: int):
        """
        Sets a data transfer limit for all access keys
        """

        requests.put(f"{self.outline_api_url}/server/access-key-data-limit",
                     json={"limit": {"bytes": limit}}, verify=False)
        self.server_info.data_limit = {"limit": {"bytes": limit}}

    def server_disable_global_data_limit(self):
        """
        Removes the access key data limit, lifting data transfer restrictions on all access keys.
        """

        requests.delete(f"{self.outline_api_url}/server/access-key-data-limit", verify=False)
        self.server_info.data_limit = None


class OutlineClientInfo(OutlineBase):

    def __init__(self, user_info={}):
        print("init OutlineClientInfo")
        self.user_id: Optional[str] = user_info.get('id', None)
        self.user_name: str = user_info.get('name', "")
        self.user_password: str = user_info.get('password', "")
        self.user_port: int = user_info.get('port', 0)
        self.user_method: str = user_info.get('method', "")
        self.user_access_url: str = user_info.get('accessUrl', "")
        self.user_data_limit: Optional[dict] = user_info.get('limit', None)

    def __call__(self):
        return self.__dict__


class OutlineClient(OutlineBase):

    def __init__(self, outline_api_url: str):
        print("init OutlineClient")
        self.outline_api_url = outline_api_url

    def __load_user_info(self, id: str):
        r = requests.get(f"{self.outline_api_url}/access-keys/{id}", verify=False)
        self.client_info = OutlineClientInfo(r.json())

    def user_get_info(self, id: str):
        self.__load_user_info(id)

    def user_test(self):
        pass


class OutlineC(OutlineServer, OutlineClient):
    def __init__(self, outline_api_url):
        super().__init__(outline_api_url)
