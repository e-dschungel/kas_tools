import hashlib
import json
from suds.client import Client
from suds.sudsobject import asdict
import logging
import socket
import getpass


class KAS:
    '''
    class to interact with the KAS API of the german hoster all-inkl.com, see http://kasapi.kasserver.com/dokumentation/phpdoc/ for details
    '''
    WSDL_AUTH = "https://kasapi.kasserver.com/soap/wsdl/KasAuth.wsdl"
    WSDL_API = "https://kasapi.kasserver.com/soap/wsdl/KasApi.wsdl"

    __auth_token = ""
    __user = ""
    __client = ""

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

        self.__user = user;

        client = Client(url=self.WSDL_AUTH)

        request = {
            'KasUser': self.__user,
            'KasAuthType': 'sha1',
            'KasPassword': hashlib.sha1(password).hexdigest(),
            'SessionLifeTime': lifetime,
            'SessionUpdateLifeTime': self.convert_bool_to_str(update_lifetime),
        }

        response = client.service.KasAuth(Params=json.dumps(request))
        self.__auth_token = response
        self.__client = Client(url=self.WSDL_API)

    def get_accounts(self):
        request = {
            'KasUser': self.__user,
            'KasAuthType': 'session',
            'KasAuthData': self.__auth_token,
            'KasRequestType': "get_accounts",
            'KasRequestParams': "",
        }

        response = self.__client.service.KasApi(Params=json.dumps(request))
        print (response)

    def update_chown(self, user, path, recursive=False):
        request = {
            'KasUser': self.__user,
            'KasAuthType': 'session',
            'KasAuthData': self.__auth_token,
            'KasRequestType': "update_chown",
            'KasRequestParams': {
                'chown_path': path,
                'chown_user': user,
                'recursive': self.convert_bool_to_str(recursive)
            },
        }

        response = self.__client.service.KasApi(Params=json.dumps(request))

    def is_local(self):
        '''
        checks if we are on a KAS system
        :return: True if yes
        '''
        return True
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

    def convert_bool_to_str(self, input):
        '''
        helper function which converts logical values to "Y" or "N"
        :param input: logical value
        :return: "Y" if input==True "N" otherwise
        '''
        if input:
            return "Y"
        else:
            return "N"