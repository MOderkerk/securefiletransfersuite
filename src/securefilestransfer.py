"""
small application for sending or receiving files via sftp
version: 1.0
date: 09/2021
licence : apache 2.0

Explanations for usage see readme.md file
"""

import datetime
import logging
import os
import sys
from re import search
import paramiko

paramiko.util.log_to_file(os.getenv('sftmLogFile'))
logging.getLogger("paramiko").setLevel(logging.INFO)


def log_console(level: str, message: str):
    """
    Log to the console
    :param level Loglever to display
    :param message message to display
    """
    print(str(datetime.datetime.now()) + ' [' + level.upper() + '] ' + message)


def open_connection(server, port):
    """
    Opens  connection to the specific server and port and returns the sftpclient
    :param server server address to use
    :param port port to the sftp server normally 22
    """
    print('Open sftp connection to ' + server)
    credentials = read_credentials(server)
    if str(3) != str(len(credentials)):
        print(
            'Something went wrong reading the credentials . Found {0} entries for server'.format(str(len(credentials))))
        raise PermissionError('No Username/Password or multiple entries found for server ' + server)

    else:

        host = server + ':' + port
        transporter = paramiko.Transport(host)
        username, password = credentials[1], credentials[2]
        transporter.connect(None, username, password)
        return paramiko.SFTPClient.from_transport(transporter)


def read_credentials(server):
    """ Read the credentials for the specific server from a file with the format
     <server>;<user>;<password>;
     :param server url of the server which is also used in the secret file
    """
    log_console('INFO', 'Searching for the credentials for server ' + server)
    credential_file = os.getenv('sftmCredentialFile')
    if credential_file is None:
        raise AttributeError('Environment variable sftmCredentialFile not found')
    file = open(credential_file, "r")
    lines = file.readlines()
    credentials = []
    file.close()
    for line in lines:
        if search(server, line):
            credentials = line.split(';')
            log_console('INFO', 'Credentials found ')
    return credentials


def close_connection(sftp_client: paramiko.SFTPClient):
    """
    Close the connection to the server
    :param sftp_client sftclient object to use
    """
    log_console('INFO', 'Closing the connection')
    sftp_client.close()


def download_file(source, target, sftp_client: paramiko.SFTPClient):
    """ Download the given file (source) to the target folder incl the target file name
    :param: source sourcefile
    :param: target target path with target filename
    :param: sftp_client client to use
    """
    log_console('INFO', 'Start downloading ' + source + ' to ' + target)
    log_console('INFO', 'Stats of remote file: ' + str(sftp_client.lstat(source)))
    sftp_client.get(source, target)
    log_console('INFO', 'File transferred')


def upload_file(source, target, sftp_client: paramiko.SFTPClient):
    """
    upload the given file (source) to the target folder
    :param: source sourcefile
    :param: target target path with target filename
    :param: sftp_client client to use
    """
    log_console('INFO', 'Start downloading ' + source + ' to ' + target)
    sftp_client.put(source, target)
    log_console('INFO', 'File transferred')


def print_dir(directory, sftp_client: paramiko.SFTPClient):
    """
    print the content of a directory
    :param: directory directory to show
    :param: sftp_client sftpclient to use
    """
    log_console('INFO', 'Printing content of folder ' + directory)
    print(sftp_client.listdir(directory))


def read_control_file(file):
    """
    Reads the control file with the information of the sftp session
    :param: file path to the control file from the args
    :return: lines read controlfile
    """
    file = open(file, 'r')
    lines = file.readlines()
    file.close()
    log_console('INFO', 'Control file contains {0} lines '.format(str(len(lines))))
    return lines


def print_header_info():
    """
    print the application header
    :return:
    """
    print('Secure File Transfer Version 1.0')
    print('--------------------------------')


def validate_arguments():
    """
    validating the arguments from commandline
    :returns:
    """
    if str(2) != str(len(sys.argv)):
        log_console('ERROR', 'Found Parameters ' + str(sys.argv))
        raise AttributeError('[ERROR] You must specify a ftp control file. Please check manual ')


def execute_control_file_commands(controllines):
    """
    executing the sftp control file
    :param: controlllines information read from the controllfile
    """
    log_console('INFO', 'Starting executing control file')

    for line in controllines:
        sftp = None
        splitted_line = line.split(';')
        # log_console('DEBUG',str(splitted_line))
        command = splitted_line[0].upper()
        if command == 'OPEN':
            sftp = open_connection(splitted_line[1], splitted_line[2])

        if command == 'CLOSE':
            close_connection(sftp)
        if command == 'DOWN':
            download_file(splitted_line[1], splitted_line[2], sftp)
        if command == 'UP':
            upload_file(splitted_line[1], splitted_line[2], sftp)
        if command == 'DIR':
            print_dir(splitted_line[1], sftp)
        if command == ' ':
            log_console("INFO", "ignoring blank line in control file")


if __name__ == "__main__":
    print_header_info()
    try:
        validate_arguments()
        control_lines = read_control_file(sys.argv[1])
        execute_control_file_commands(control_lines)
    except AttributeError as e:
        print(e)
    except FileNotFoundError as e:
        print('File not found. {0}'.format(e))
