# s3-sftp
GUI Wrapper for S3 API using Python3, PyQt5, and the Boto3 SDK.  

You'll need S3 keys in order to use this application. You can specify any region, it just needs to be valid.

Region list: 

https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html

### Notes

All development and testing thusfar has been performed on macOS Mojave. 


### Local Testing

Virtualenv setup:

Virtualenv steps: python3 -m virtualenv <Virtual env name>
In virtualenv : pip3 install boto3; pip3 install pyqt5; pip3 install botocore; pip3 install ntpath
