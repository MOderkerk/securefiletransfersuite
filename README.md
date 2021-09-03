# Secure file transfer suite
Small python script for automatic uploading or downloading files over sftp using a control file.

##Usage
After setting two environment variables 

variableName | description
----------|-----------
sftmCredentialFile | csvfile with the serverurl,username and password delimited by ;    
sftmLogFile | path incl. fileanme of the log where the sftp errors and infos are logged (not the logs from the script)



just execute : 

> python securefiletransfer.py <controlfile> 


## Control File Syntax
The control file is a csv based file with ; as seperator.

Each line starts with a command followed by its parameters

### Commands

command| description | parameter
----|----|----
OPEN |opens the connection to the sftp server | serveraddress (same as in the credential file) and port
DOWN | downloads a file from the server to a local file | absolute path of the sourcefile , absolute path to the local file to save
UP | uploads a local file to the remote server | absolute path of the sourcefile , absolute path to the local file to save
DIR | execute dir command of the given path | path to folder to show
CLOSE | close the connection

Example:
> OPEN;LOCALHOST;22
> 
> DOWN;/opt/data/log1.txt;c:\log1.txt
> 
> UP;c:\log2.txt;/opt/data/log2.txt
> 
> DIR;/opt/data
> 
> CLOSE

## Example credential file
> localhost;username;password
