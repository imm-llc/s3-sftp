# s3-sftp
GUI Wrapper for S3 API using Python3, PyQt5, and the Boto3 SDK.  

You'll need S3 keys and a valid bucket name in order to use this application. You can specify any region, it just needs to be valid.

Region list:

https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html

### Notes

All development and testing thusfar has been performed on macOS Mojave.

### IAM Permissions

This application is written with the intention of allowing someone, say, a client, to upload objects to S3. As such, they need permission to `PutObject` on their bucket.

In order to verify connection to S3, the `uploadS3` function lists the contents of the specified bucket. So the user will need the `ListBucket` permission.

Example Policy:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::dev-sftp-test-bhi",
                "arn:aws:s3:::dev-sftp-test-bhi/*"
            ]
        }
    ]
}
```

The application doesn't allow deleting object and I don't intend to add that functionality unless there's a very compelling business case.


### Local Testing

Virtualenv setup:

Virtualenv steps: python3 -m virtualenv <Virtual env name>

In virtualenv : pip3 install boto3; pip3 install pyqt5; pip3 install botocore; pip3 install ntpath
