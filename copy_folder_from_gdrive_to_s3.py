# -*- coding: utf-8 -*-

#%% Prelims

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Id of the root GDrive folder; you can find it in the URL for that folder.
gdriveRootFolderId = '0B9xn8UisQwEeS0ZFLWh0NDY1ZG8'
# Name of the s3 bucket (excl. 's3://'), plus optionally a path within that bucket
s3RootFolderName = 'example_bucket_name/path/within'

#%% Authenticate - the first time do this manually

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
# A browser window will open. login using the appropriate account.

#%% Having authenticated, save your credentials to a file (BUT KEEP IT SAFE)

gauth.SaveCredentialsFile('mycreds.txt')

#%% The second time round, we can authenticate using the saved credentials file.
# i.e. skipping the above uthentication step.

gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")

#%% Get the folder structure

drive = GoogleDrive(gauth)

fileDict = dict()
folder_queue = [gdriveRootFolderId]
dir_queue = ['/']
cnt = 0

while len(folder_queue) != 0:
    current_folder_id = folder_queue.pop(0)
    file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(current_folder_id)}).GetList()
    
    current_parent = dir_queue.pop(0)
    print(current_parent, current_folder_id)
    for file1 in file_list:
        fileDict[cnt] = dict()
        fileDict[cnt]['id'] = file1['id']
        fileDict[cnt]['title'] = file1['title']
        fileDict[cnt]['dir'] = current_parent + file1['title']
        fileDict[cnt]['mimeType'] = file1['mimeType']

        if file1['mimeType'] == 'application/vnd.google-apps.folder':
            fileDict[cnt]['type'] = 'folder'
            fileDict[cnt]['dir'] += '/'
            folder_queue.append(file1['id'])
            dir_queue.append(fileDict[cnt]['dir'])
        else:
            fileDict[cnt]['type'] = 'file'
            
        cnt += 1

#%% Create bash script to copy from gdrive to s3

# This is the base wget command that we will use. This might change in the future due to changes in Google drive
wget_text = '"wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&amp;confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate \'https://docs.google.com/uc?export=download&amp;id=FILE_ID\' -O- | sed -rn \'s/.*confirm=([0-9A-Za-z_]+).*/\\1\\n/p\')&id=FILE_ID" -O- | aws s3 cp - s3://S3BUCKETNAMEFILE_NAME --content-type "FILEMIMETYPE" && rm -rf /tmp/cookies.txt"'.replace('&amp;', '&')
wget_text = wget_text.replace('S3BUCKETNAME', s3RootFolderName)

with open('script.sh', 'w') as f: 
    fileDict.keys()
    for file_iter in fileDict.keys():
        if fileDict[file_iter]['type'] == 'folder':
            pass # s3 will automatically create missing folders
        else:
            # postProcess filename - remove awkward characters
            fileName = fileDict[file_iter]['dir']
            fileName = fileName.replace(' ', '_')
            fileName = fileName.replace("'", "")
            fileName = fileName.replace("(", "")
            fileName = fileName.replace(")", "")
    
            scriptText = wget_text[1:-1]  + '\n'
            scriptText = scriptText.replace('FILE_ID', fileDict[file_iter]['id'])
            scriptText = scriptText.replace('FILE_NAME', fileName)
            scriptText = scriptText.replace('FILEMIMETYPE', fileDict[file_iter]['mimeType'])
            f.write(scriptText)
