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

    def convert_str_to_bool(self, input):
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

    def convert_to_dict(self, data):
        out = dict()
        if isinstance(data, list):
            out = dict()
            for listelement in data:
                out.update(self.convert_to_dict(listelement))
        elif data.__class__.__name__ == "item":
            if hasattr(data, "value"):
                out = dict()
                #print data.key
                key = data.key
                if isinstance(key, list) and all(isinstance(element, basestring) for element in key):
                    key = "".join(key)
                    value = "".join(data.value).encode("unicode-escape")
                    out[key] = self.fix_type(value)
                elif isinstance(key, basestring):
                    out[data.key] = self.fix_type(data.value.encode("unicode-escape"))
                else:
                    raise ValueError("Invalid type")
            else:
                return self.convert_to_dict(data.item)
        else:
            raise ValueError("Invalid type")
        return out

    def num(self, s):
        '''
        :param s: string to convert
        :return: Int or Float of s
        '''
        if not s.isdigit():
            raise ValueError(str(s) + " is no number")
        try:
            return int(s)
        except ValueError:
            return float(s)


    def fix_type(self, value):
        '''
        converts types given as string to bool, Int or Float as appropriate
        :param data: string with value
        :return: value converted to bool, Int or Float (if appropiate), unchanged value otherwise
        '''
        if value.isdigit():
            return self.num(value)
        try:
            return self.convert_str_to_bool(value)
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
            'KasUser': self.__user,
            'KasAuthType': 'session',
            'KasAuthData': self.__auth_token,
            'KasRequestType': "get_accounts",
            'KasRequestParams': "",
        }

        response = self.__client.service.KasApi(Params=json.dumps(request))
        return self.convert_to_dict(response.item[1].value.item[2].value)

    def get_accountsettings(self):
        '''
        gets account settings
        :return: dict with account data
        '''
        request = {
            'KasUser': self.__user,
            'KasAuthType': 'session',
            'KasAuthData': self.__auth_token,
            'KasRequestType': "get_accountsettings",
            'KasRequestParams': "",
        }

        response = self.__client.service.KasApi(Params=json.dumps(request))
        return self.convert_to_dict(response.item[1].value.item[2].value[0].value.item)


    def update_chown(self, user, path, recursive=False):
        '''
        change owner of path to user
        :param user: new owner
        :param path: path to change
        :param recursive: change recursive?
        :return:
        '''
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

