import datetime
import logging
import os
import sys
from re import search
import paramiko

paramiko.util.log_to_file(os.getenv('sftmLogFile'))
logging.getLogger("paramiko").setLevel(logging.INFO)


def log_console(level: str, message: str):
    """ Log to the console """
    print(str(datetime.datetime.now()) + ' [' + level.upper() + '] ' + message)


def open_connection(server, port):
    """ Opens  connection to the specific server and port and returns the sftpclient """
    print('Open sftp connection to ' + server)
    credentials = read_credentials(server)
    if len(credentials) != 3:
        print('Something went wrong reading the credentials . Found ' + len(credentials) + ' entries for server')
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
    """
    log_console('INFO', 'Searching for the credentials for server ' + server)
    credential_file = os.getenv('sftmCredentialFile')
    if credential_file == None:
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
    """ Close the connection to the server """
    log_console('INFO', 'Closing the connection')
    sftp_client.close()


def download_file(source, target_folder, sftp_client: paramiko.SFTPClient):
    """ Download the given file (source) to the target folder incl the target file name """
    log_console('INFO', 'Start downloading ' + source + ' to ' + target_folder)
    log_console('INFO', 'Stats of remote file: ' + str(sftp_client.lstat(source)))
    sftp_client.get(source, target_folder)
    log_console('INFO', 'File transferred')


def upload_file(source, target_folder, sftp_client: paramiko.SFTPClient):
    """ upload the given file (source) to the target folder """
    log_console('INFO', 'Start downloading ' + source + ' to ' + target_folder)
    sftp_client.put(source, target_folder)
    log_console('INFO', 'File transferred')


def print_dir(directory, sftp_client: paramiko.SFTPClient):
    """ print the content of a directory """
    log_console('INFO', 'Printing content of folder ' + directory)
    print(sftp_client.listdir(directory))


def read_control_file(file):
    """ Reads the control file with the information of the sftp session """
    file = open(file, 'r')
    lines = file.readlines()
    file.close()
    log_console('INFO', 'Control file contains ' + str(len(lines)) + ' lines ')
    return lines


def print_header_info():
    print('Secure File Transfer Version 1.0')
    print('--------------------------------')


def validate_arguments():
    """ validating the arguments from commandline """
    if len(sys.argv) != 2:
        log_console('ERROR', 'Found Parameters ' + str(sys.argv))
        raise AttributeError('[ERROR] You must specify a ftp control file. Please check manual ')


def execute_control_file_commands(controllines):
    """ executing the sftp control file """
    log_console('INFO', 'Starting executing control file')

    for line in controllines:
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


if __name__ == "__main__":
    print_header_info()
    try:
        validate_arguments()
        control_lines = read_control_file(sys.argv[1])
        execute_control_file_commands(control_lines)

    except AttributeError as e:
        print(e)
