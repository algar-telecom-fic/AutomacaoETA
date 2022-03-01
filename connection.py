host = "127.0.0.1"

port = 3022

username = "gabriel"

password = "123456"

command = "ls"

import paramiko

ssh = paramiko.SSHClient()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(host, port, username, password)


stdin, stdout, stderr = ssh.exec_command(command)

lines = stdout.readlines()

print(lines)