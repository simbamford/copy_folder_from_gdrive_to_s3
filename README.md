# copy_folder_from_gdrive_to_s3

Python script to copy a publicly available folder from GDrive to s3. Requires 
manual authentication, then data streams directly.

This repo fuses these bits of know-how:
- https://medium.com/analytics-vidhya/how-to-connect-google-drive-to-python-using-pydrive-9681b2a14f20
- https://medium.com/datadriveninvestor/recursively-download-all-the-contents-of-a-google-drive-folder-using-python-wget-and-a-bash-script-d8f2c6b105d5
- https://stackoverflow.com/questions/49448291/combining-wget-and-aws-s3-cp-to-upload-data-to-s3-without-saving-locally
- https://docs.aws.amazon.com/cli/latest/reference/s3/cp.html (For copying mime types correctly)

Although the folder you're trying to copy is available to anyone with the link, 
you need to authenticate with GDrive in order to use the API. So firstly, use 
the Google Cloud Platform web interface to create a project. Then in 
APIs & Services -> Credentials -> OAuth 2.0 Client IDs, download the credentials 
for the project. Rename the resulting file to 'client_secrets.json' and make 
sure this file is on the python path (for example, by putting it in the same 
folder as this script). 

We'll be using pydrive (https://pypi.org/project/PyDrive/), so:

pip install PyDrive

working from a local machine, run the script section-by-section 
(sections delineated by #%%). You will be asked to authenticate with Google.
At this point you may wish to save your credentials if you want everything else 
to run in batch.
 
Then the script will query gdrive recursively to create a list of all the files 
and folders. 

Then there is a section which generates a script file. The resulting script has 
one line for each file, which copies directly from gdrive to s3, to a bucket of 
your choice. So at this point I upload the script to an EC2 instance (it could 
also be made to work from e.g. cloud-9 or lambda with some work). 
You don't need to allocate disk space for temporary storage. 

You'll need to make sure that the instance has aws credentials, by installing 
awscli:

sudo apt update
sudo apt install awscli

... and then using:

aws configure
(You will be prompted for your credentials).

Then you can run the script, i.e.:

./script.sh

... and the cloud-to-cloud copy will take place. 
