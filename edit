#!/usr/bin/env python
import kas
import argparse
import os
import getpass
import grp
import pwd
import time
import subprocess
import stat


def get_owner(file):
    '''
    returns owner of file in the form the KAS API expects it
    KAS API     filesystem
    phpuser     www-data
    w123456     ssh-w123456
    :param file: file
    :return: owner of file
    '''
    stat_info = os.stat(file)
    uid = stat_info.st_uid
    user = pwd.getpwuid(uid)[0]
    if user == "www-data":
        user = "phpuser"
    elif user.startswith("ssh-"):
      user = user.replace("ssh-", "")
    else:
        raise IOError("Unknown type of owner: " . user)
    return user

def get_default_editor():
    '''
    get default editor from environment variable $EDITOR, if it is empty use vi
    :return: name of default editor
    '''
    editor = os.getenv('EDITOR')
    if not editor:
        editor = "vi" #vi should be available on all POSIX systems
    return editor

def edit_file(file):
    '''
    edit given file, permmsions are set to file can be edited
    :param file:
    :return: nothing
    '''
    initial_permissions = stat.S_IMODE(os.lstat(args.file).st_mode)
    try:
        os.chmod(args.file, initial_permissions | stat.S_IREAD | stat.S_IWRITE)
        subprocess.call([args.editor, args.file])
    finally:
        os.chmod(args.file, initial_permissions)


if __name__ == "__main__":
    #version of this tool
    __version__ = "0.1"

    #max time to wait for chown (in seconds)
    max_wait_time = 30

    # get arguments from CLI
    parser = argparse.ArgumentParser(description='tool to chown a file to make it editable if necessary, edit it with your favourite editor and chown it back, homepage: https://github.com/e-dschungel/kas_tools')
    parser.add_argument('file')
    parser.add_argument('--editor', default = get_default_editor(), help="editor to call")
    parser.add_argument('--version', action='version', version = '%(prog)s ' + __version__)
    args = parser.parse_args()

    #make sure path is absolute
    args.file = os.path.abspath(args.file)

    if not os.path.isfile(args.file):
        print("file {} is not a file!".format(args.file))
        exit(1)

    kas = kas.KAS()
    kas_user = kas.get_user()

    initial_owner = get_owner(args.file)

    if initial_owner == "root":
        print("This file is owned by root, this ownership cannot be restored!")
        exit(1)

    is_readwriteable_by_initial_owner = os.access(args.file, os.R_OK | os.W_OK)

    if is_readwriteable_by_initial_owner or (not is_readwriteable_by_initial_owner and initial_owner == kas_user):
        #file is editable or permssion can be changed to make it editable
        edit_file(args.file)
    else: #chmod(w123456) is required to make file editable
        print("{} needs an owner change".format(args.file))
        #get KAS password
        password = getpass.getpass("KAS password for user " + kas_user + ": ")
        try:
            #change owner
            kas.login(kas_user, password)
            kas.update_chown(kas_user, kas.fix_chown_path(args.file))
            print("Waiting for owner to change...")
            wait_time = 0
            while(True):
                time.sleep(1)
                wait_time += 1
                if (kas.get_user() == get_owner(args.file) or wait_time > max_wait_time):
                    break

            if wait_time > max_wait_time:
                print("Could not chown file {}".format(args.file))
                exit(1)

            #after the owner has changed, the file can be edited in any case
            edit_file(args.file)

        finally:
            #restore owner
            if get_owner(args.file) != initial_owner:
                kas.login(kas_user, password)
                kas.update_chown(initial_owner, kas.fix_chown_path(args.file))







