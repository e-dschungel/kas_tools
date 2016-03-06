import hashlib
import json
from suds.client import Client
from suds.sudsobject import asdict
import logging
import socket
import getpass
import time
import os

class KAS:
    '''
    class to interact with the KAS API of the german hoster all-inkl.com, see http://kasapi.kasserver.com/dokumentation/phpdoc/ for details
    '''
    WSDL_AUTH = "https://kasapi.kasserver.com/soap/wsdl/KasAuth.wsdl"
    WSDL_API = "https://kasapi.kasserver.com/soap/wsdl/KasApi.wsdl"

    _auth_token = ""
    _user = ""
    _client = ""
    _flood_timestamp = dict()

    def login(self, user, password, lifetime=5, update_lifetime=True, debug=False):
        '''
        log into KAS, must be called before any other KAS operation
        :param user: KAS user
        :param password: password for KAS user
        :param lifetime: session lifetime
        :param update_lifetime: update lifetime on every request
        :param debug: set to True to debug all KAS API calls
        :return: nothing
        '''
        if debug:
            logging.getLogger('suds.client').setLevel(logging.DEBUG)

        self._user = user;

        client = Client(url=self.WSDL_AUTH)

        request = {
            'KasUser': self._user,
            'KasAuthType': 'sha1',
            'KasPassword': hashlib.sha1(password).hexdigest(),
            'SessionLifeTime': lifetime,
            'SessionUpdateLifeTime': self._convert_bool_to_str(update_lifetime),
        }

        response = client.service.KasAuth(Params=json.dumps(request))
        self._auth_token = response
        self._client = Client(url=self.WSDL_API)

    def _wait(self, function_name):
        '''
        waits blocking until given KAS action can be performed again
        :param function_name: KAS action name
        :return:
        '''
        if not function_name in self._flood_timestamp:
            return
        if time.time() > self._flood_timestamp[function_name]:
            return
        time.sleep(self._flood_timestamp[function_name] - time.time())

    def _update_flood_protection_time(self, function_name, response):
        '''
        updates time after which given KAS action can be performed again to avoid running into flooding protection
        :param function_name:
        :param response: response from KAS server
        :return:
        '''
        self._flood_timestamp[function_name] = time.time() + self._get_flood_delay(response)

    def _get_flood_delay(self, response):
        '''
        extracts flood delay from response
        :param response: response from KAS
        :return: delay
        '''
        return response.item[1].value.item[0].value

    def _send_request(self, request):
        '''
        sends request to KAS server, waits if necassary to avoid running in flood protection
        :param request: request to send
        :return: response from KAS server
        '''
        function_name = request['KasRequestType'];
        self._wait(function_name)
        response = self._client.service.KasApi(Params=json.dumps(request))
        self._update_flood_protection_time(function_name, response)
        return response


    def _convert_str_to_bool(self, input):
        '''
        helper function which converts strings to True or False
        :param input: string to convert
        :return: True if input=="Y" or "TRUE", False if input=="N" or "FALSE"
        '''
        if input=="Y" or input == "TRUE":
            return True
        elif input=="N" or input == "FALSE":
            return False
        else:
            raise ValueError(str(input) + " cannot be converted to bool")

    def _convert_to_dict(self, data):
        '''
        function to convert SUDS responses to python dicts, this mangles list to one large dict
        if you need a list of dicts this must be construxted outside of this function
        :param data: response as given by SUDS
        :return: dict with the values given in response, the types or the arguments are converted to Int, Float or Bool
        as appropriate
        '''
        out = dict()
        if isinstance(data, list):
            out = dict()
            for listelement in data:
                out.update(self._convert_to_dict(listelement))
        elif data.__class__.__name__ == "item":
            if hasattr(data, "value"):
                out = dict()
                key = data.key
                if isinstance(key, list) and all(isinstance(element, basestring) for element in key) and isinstance(data.value, list):
                    key = "".join(key)
                    value = "".join(data.value).encode("unicode-escape")
                    out[key] = self._fix_type(value)
                elif isinstance(key, basestring) and isinstance(data.value, basestring):
                    out[data.key] = self._fix_type(data.value.encode("unicode-escape"))
                elif isinstance(key, basestring) and isinstance(data.value, int):
                    out[data.key] = data.value
                elif isinstance(key, basestring) and data.value.__class__.__name__ == "value":
                    out[key] = self._convert_to_dict(data.value.item)
                else:
                    raise ValueError("Invalid type")
            else:
                return self._convert_to_dict(data.item)
        else:
            raise ValueError("Invalid type")
        return out

    def _isnumeric(self, value):
        '''
        checks if string is a number
        in contrast to python's own isnumeric and isdigit function this also works for negative numbers
        :param value: string to check
        :return: True if value is a number, False otherwise
        '''
        try:
            val = float(value)
            return True
        except ValueError:
            return False

    def _convert_str_to_numeric(self, s):
        '''
        :param s: string to convert
        :return: Int or Float of s
        '''
        if not self._isnumeric(s):
            raise ValueError(str(s) + " is no number")
        try:
            return int(s)
        except ValueError:
            return float(s)


    def _fix_type(self, value):
        '''
        converts types given as string to bool, Int or Float as appropriate
        :param data: string with value
        :return: value converted to bool, Int or Float (if appropiate), unchanged value otherwise
        '''
        if self._isnumeric(value):
            return self._convert_str_to_numeric(value)
        try:
            return self._convert_str_to_bool(value)
        except:
            ValueError
            pass
        return value


    def get_accounts(self):
        '''
        gets account data
        :return: dict with account data
        '''
        request = {
            'KasUser': self._user,
            'KasAuthType': 'session',
            'KasAuthData': self._auth_token,
            'KasRequestType': "get_accounts",
            'KasRequestParams': "",
        }

        response = self._send_request(request)
        out = []
        for listelement in response.item[1].value.item[2].value:
            out.append(self._convert_to_dict(listelement))
        return out

    def get_accountsettings(self):
        '''
        gets account settings
        :return: dict with account data
        '''
        request = {
            'KasUser': self._user,
            'KasAuthType': 'session',
            'KasAuthData': self._auth_token,
            'KasRequestType': "get_accountsettings",
            'KasRequestParams': "",
        }

        response = self._send_request(request)
        return self._convert_to_dict(response.item[1].value.item[2].value[0].value.item)

    def get_accountressources(self):
        '''
        gets account settings
        :return: dict with account data
        '''
        request = {
            'KasUser': self._user,
            'KasAuthType': 'session',
            'KasAuthData': self._auth_token,
            'KasRequestType': "get_accountressources",
            'KasRequestParams': "",
        }

        response = self._send_request(request)
        return self._convert_to_dict(response.item[1].value.item[2].value[0])

    def get_server_information(self):
        '''
        gets server information
        :return: dict with server information
        '''
        request = {
            'KasUser': self._user,
            'KasAuthType': 'session',
            'KasAuthData': self._auth_token,
            'KasRequestType': "get_server_information",
            'KasRequestParams': "",
        }

        response = self._send_request(request)
        out = []
        for listelement in response.item[1].value.item[2].value:
            out.append(self._convert_to_dict(listelement))
        return out

    def fix_chown_path(self, path):
        '''
        remove /www/htdocs/w123456 from path as the KAS API for update_chown expects it that way
        :param path: path to fix
        :return: fixed path
        '''
        path_to_remove = os.path.join("www", "htdocs", self.get_user())
        return path.replace(path_to_remove, "")

    def update_chown(self, owner, path, recursive=False):
        '''
        change owner of path to user
        :param owner: new owner
        :param path: path to change, relative to the ftp root, see fix_chown_path
        :param recursive: change recursive?
        :return:
        '''
        request = {
            'KasUser': self._user,
            'KasAuthType': 'session',
            'KasAuthData': self._auth_token,
            'KasRequestType': "update_chown",
            'KasRequestParams': {
                'chown_path': path,
                'chown_user': owner,
                'recursive': self._convert_bool_to_str(recursive)
            },
        }

        response = self._send_request(request)

    def is_local(self):
        '''
        checks if we are on a KAS system
        :return: True if yes
        '''
        if socket.getfqdn().endswith(".kasserver.com"):
            return True
        else:
            return False

    def get_user(self):
        '''
        returns KAS username if were are local on KAS system
        :return: KAS username
        '''
        if not self.is_local():
            raise IOError("Not on KAS!")
        username = getpass.getuser()
        username = username.replace("ssh-", "")
        return username

    def _convert_bool_to_str(self, input):
        '''
        helper function which converts logical values to "Y" or "N"
        :param input: logical value
        :return: "Y" if input==True "N" otherwise
        '''
        if input:
            return "Y"
        else:
            return "N"




