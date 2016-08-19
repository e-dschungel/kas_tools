# kas_tools
This repo contains tools for the SSH shell of the german hoster [all-inkl.com](http://www.all-inkl.com).
They are implemented in Python and make use of the KAS API (see http://kasapi.kasserver.com/dokumentation/phpdoc/index.html).
They are intended to be used on the SSH shell (available for plans >= "Premium") of kasserver.com, other usages are not supported.

They can also be used as an example on how to use the KAS API in Python. 

kas_tools consists of the following tools:

|name|description|
|---|---|
|chown|replacement for the missing chown command|
|edit|open file in editor and make sure owner and permssions are set so it is editable|
|getip|script to print the current IP|

## Installation
* Login via SSH
* Install SUDS library: `pip2 install --user suds-jurko`
* Clone repo: `git clone https://e-dschungel@github.com/e-dschungel/kas_tools.git /PATH/TO/kas_tools`
* Add `'PATH=$PATH:/PATH/TO/kas_tools'` to `/www/htdocs/USER/.user_bashrc`
* Reload bashrc: `source /.bashrc`

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

###Changelog
####0.1
- first public version

####0.2
- multiple path can be chowned at once
- improved help message

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
