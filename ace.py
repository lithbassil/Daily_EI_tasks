import paramiko


host = 'ACE IP'
username = 'ACE USERNAME'
password = 'ACE PASSWORD'
sftp_pwd = ''

# This to see if the sftp server asked insert the password to log in
pswd = 'password'

# list of certificates from cisco ACE crypto file 
explist = open('export_list.txt', 'r')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=host, username=username, password=password, look_for_keys=False, allow_agent=False)

for export_cert in explist:
    try:
        stdin, stdout, stderr = ssh.exec_command(export_cert)
        output1 = stdout.readlines()
        print(' '.join(map(str, output1)))
        if pswd in output:
            stdin, stdout, stderr = ssh.exec_command(sftp_pwd)
            output2 = stdout.readlines()
            print(' '.join(map(str, output2)))
    except Exception as err:
        print(err)
