# chown_kas
This is a replacement for chown for the SSH shell of the german hoster [all-inkl.com](http://www.all-inkl.com).
It is implemented in Python and makes use of the KAS API (see http://kasapi.kasserver.com/dokumentation/phpdoc/index.html).
It is intended to be used on the SSH shell (available for plans >= "Premium")  of kasserver.com, other usages are not supported.

It can also be used as an example on how to use the KAS API in Python. 

## Installation
* Login via SSH
* Install pip (if not installed already)
 * `wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py --user && rm get-pip.py`
 * add `export PATH=$PATH:/.local/bin` to the file `/www/htdocs/USER/user_bashrc` (create if neccessary)
 * `source /.bashrc`
* `pip install --user suds-jurko`
* `git clone https://e-dschungel@github.com/e-dschungel/chown_kas.git`
* add `alias chown ./chown/chown_kas.py`
* `source /.bashrc`

##Usage
Type `chown user path` to change the owner of the path to the given user.
The user can be `phpuser` or your current KAS user (i.e. `w123456`).
Other users are not allowed.
You will be promted for your KAS password to perform the change.

###Flags
-R: set owner recursively
