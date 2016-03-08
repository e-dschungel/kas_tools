# kas_tools
This repo contains tools for the SSH shell of the german hoster [all-inkl.com](http://www.all-inkl.com).
They are implemented in Python and make use of the KAS API (see http://kasapi.kasserver.com/dokumentation/phpdoc/index.html).
They are intended to be used on the SSH shell (available for plans >= "Premium") of kasserver.com, other usages are not supported.

They can also be used as an example on how to use the KAS API in Python. 

kas_tools consists of the following tools:
|name|description|
|chown_kas|replacement for the missing chown command|
|edit|open file in editor and make sure owner and permssions are set so it is editable|
|getip|script to print the current IP|

## Installation
* Login via SSH
* Install pip (if not installed already)
 * symlink `/.local` to `/www/htdocs/USER/.local` to make it survive a de- and reactivation of SSH and the migratation to another server: `ln -s /www/htdocs/USER/.local /.local` (replace USER with your username)
 * `wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py --user && rm get-pip.py`
 * add `export PATH=$PATH:/.local/bin` to the file `/www/htdocs/USER/.user_bashrc` (create file if neccessary)
 * `source /.bashrc`
* `pip install --user suds-jurko`
* `git clone https://e-dschungel@github.com/e-dschungel/kas_tools.git`
* add `alias chown='/PATH/TO/kas_tools/chown_kas.py'`, `alias getip='/PATH/TO/kas_tools/getip.py'` and `alias edit='/PATH/TO/kas_tools/edit.py'`  to the file `/www/htdocs/USER/.user_bashrc`
* `source /.bashrc`

##chown
###Usage
Type `chown user path` to change the owner of the path to the given user.
The user can be `phpuser` or your current KAS user (i.e. `w123456`).
Other users are not allowed.
You will be prompted for your KAS password to perform the change.

####Flags
|flag|description|
|---|---|
|`-R`, `--recursive`| change owner recursively|
|`--version`| show version information|
|`--help`|show help message|

##edit
###Usage
Type `edit file` to edit the given file in an editor.
If neccesary the owner and the permissions are change to make the file editable.
If a change of the owner is neccesary you will be prompted for your KAS password.
After the editing the owner and the permissions are restored.

####Flags
|flag|description|
|---|---|
|`--version`| show version information|
|`--help`|show help message|
|`--editor`|set editor, by default the $EDITOR enviroment variable is used|


##getip
###Usage 
`getip` simply prints the current IP if executed on a KAS server.
Otherwise it returns an error.
