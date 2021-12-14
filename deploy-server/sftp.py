import pysftp as sftp

def sftpMain ():
    try:   
        s = sftp.Connection(host="host_name", username="usr_name", password="passwd")
        remotepath = 'path to folder on server'
        localpath = 'path of the folder to upload'

        s.put(localpath,remotepath)
    except Exception:
        print (Exception)
sftpMain()




