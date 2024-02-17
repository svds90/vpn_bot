import requests
from typing import Any, Dict, Optional
from exceptions import *


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


class OutlineClientInfo(OutlineBase):

    def __init__(self, user_info={}):
        print("init OutlineClientInfo")
        self.id: Optional[str] = user_info.get('id', None)
        self.name: str = user_info.get('name', "")
        self.password: str = user_info.get('password', "")
        self.port: int = user_info.get('port', 0)
        self.method: str = user_info.get('method', "")
        self.access_url: str = user_info.get('accessUrl', "")
        self.data_limit: Optional[dict] = user_info.get('dataLimit', None)

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

    def __fetch_server_info(self, outline_api_url):

        request = requests.get(f"{outline_api_url}/server", verify=False, timeout=2)
        server_json = {**request.json(), 'server_key': outline_api_url}
        return server_json

    def change_hostname(self, new_hostname: str) -> None:
        """
        Changes the hostname for access keys. Must be a valid hostname or IP address.
        If it's a hostname, DNS must be set up independently of this API.
        """

        r = requests.put(f"{self.outline_api_url}/server/hostname-for-access-keys",
                         json={"hostname": new_hostname}, verify=False)

        if r.status_code != 204:
            raise OutlineInvalidHostname(r.status_code)

        self.server_info.hostname_for_keys = new_hostname

    def rename_server(self, new_name: str) -> None:
        """
        Renames the server
        """

        r = requests.put(f"{self.outline_api_url}/name", json={"name": new_name}, verify=False)

        if r.status_code != 204:
            raise OutlineInvalidName(r.status_code)

        self.server_info.name = new_name

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

        r = requests.put(f"{self.outline_api_url}/metrics/enabled",
                         json={"metricsEnabled": status}, verify=False)

        if r.status_code != 204:
            raise OutlineTelemetryError(r.status_code)

        self.server_info.metric_status = status

    def change_default_port(self, port: int):
        """
        Changes the default port for newly created access keys.
        This can be a port already used for access keys.
        """

        r = requests.put(f"{self.outline_api_url}/server/port-for-new-access-keys",
                         json={"port": port}, verify=False)

        if r.status_code != 204:
            raise OutlinePortError(r.status_code)

        self.server_info.port_for_new_keys = port

    def set_global_data_limit(self, limit: int):
        """
        Sets a data transfer limit for all access keys
        """

        r = requests.put(f"{self.outline_api_url}/server/access-key-data-limit",
                         json={"limit": {"bytes": limit}}, verify=False)

        if r.status_code != 204:
            raise OutlineInvalidDataLimit(r.status_code)

        self.server_info.data_limit = {"limit": {"bytes": limit}}

    def disable_global_data_limit(self):
        """
        Removes the access key data limit, lifting data transfer restrictions on all access keys.
        """

        requests.delete(f"{self.outline_api_url}/server/access-key-data-limit", verify=False)
        self.server_info.data_limit = None


class OutlineClient(OutlineBase):

    def __init__(self, outline_api_url: str):
        print("init OutlineClient")
        self.outline_api_url = outline_api_url
        self.client_info = OutlineClientInfo()

    def get_all_keys(self):
        """
        Lists the access keys
        """

        r = requests.get(f"{self.outline_api_url}/access-keys", verify=False)
        return r.json()

    def get_key(self, id: str):
        """
        Get an access key
        """

        r = requests.get(f"{self.outline_api_url}/access-keys/{id}", verify=False)

        if r.status_code != 200:
            raise OutlineInvalidAccessKey(r.status_code)

        self.client_info = OutlineClientInfo(r.json())

    def get_all_metrics(self):
        """
        Returns the data transferred per access key
        """

        r = requests.get(f"{self.outline_api_url}/metrics/transfer", verify=False)
        return r.json()

    def create_key(self):
        """
        Creates a new access key
        """

        requests.post(f"{self.outline_api_url}/access-keys",
                      json={"method": "chacha20-ietf-poly1305"}, verify=False)

    def delete_key(self, id: str):
        """
        Deletes an access key
        """

        r = requests.delete(f"{self.outline_api_url}/access-keys/{id}", verify=False)

        if r.status_code != 204:
            raise OutlineInvalidAccessKey(r.status_code)

        self.client_info = OutlineClientInfo()

    def rename_key(self, id: str, name: str):
        """
        Renames an access key
        """

        r = requests.put(f"{self.outline_api_url}/access-keys/{id}/name",
                         json={"name": str(name)}, verify=False)

        if r.status_code != 204:
            raise OutlineInvalidAccessKey(r.status_code)

    def set_data_limit(self, id: str, data_limit: int):
        """
        Sets a data limit for the given access key
        """

        r = requests.put(f"{self.outline_api_url}/access-keys/{id}/data-limit",
                         json={"limit": {"bytes": data_limit}}, verify=False)

        if r.status_code != 204:
            raise OutlineInvalidDataLimit(r.status_code)

    def disable_data_limit(self, id: str):
        """
        Removes the data limit on the given access key.
        """

        r = requests.delete(f"{self.outline_api_url}/access-keys/{id}/data-limit", verify=False)

        if r.status_code != 204:
            raise OutlineInvalidDataLimit(r.status_code)


class Outline(OutlineBase):
    def __init__(self, outline_api_url):
        self.server = OutlineServer(outline_api_url)
        self.client = OutlineClient(outline_api_url)
