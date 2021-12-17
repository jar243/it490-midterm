from broker import run_rabbit_app

import pysftp as sftp

def sftpMain ():
    try:

        s = sftp.Connection(
                host="127.0.0.1", 
                username='sftpuser', 
                password='sftp123'
                )

        remotepath='/sftpuser'
        localpath ='/home/it490/'
    except Exception:
        print (Exception)

sftpMain()
