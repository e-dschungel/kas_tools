#!/usr/bin/env python
import kas
import argparse
import os
import getpass


def check_user(owner):
    '''
    checks if new owner is acceptable: so either phpuser or current KAS user
    :param owner: requested new owner
    :return: True if username is accepatable, False if not
    '''
    if owner == "":
        return False
    if owner == "phpuser" or owner == kas.get_user():
        return True
    return False

def fix_path(path):
    '''
    remove /www/htdocs/w123456 from path () as the KAS API expects it that way
    :param path: path to fix
    :return: fixed path
    '''
    path_to_remove = "/www/htdocs/" + kas.get_user()
    return path.replace(path_to_remove, "")

if __name__ == "__main__":
    # get arguments from CLI
    parser = argparse.ArgumentParser()
    parser.add_argument('-R', '--recursive', action='store_true')
    parser.add_argument('user')
    parser.add_argument('path')
    args = parser.parse_args()

    #make sure path is absolute
    args.path = os.path.abspath(args.path)

    #check input
    kas = kas.KAS()
    if not check_user(args.user):
        raise IOError("Invalid username!")
    if not os.path.exists(args.path):
        raise IOError("Path does not exist")

    #get KAS user and password
    kas_user = kas.get_user();
    password = getpass.getpass("KAS password for user " + kas_user + ": ")

    #log into KAS
    kas.login(kas_user, password)

    #execute chown
    kas.update_chown(args.user, fix_path(args.path), args.recursive)
