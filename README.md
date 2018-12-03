# s3-sftp
GUI Wrapper for S3 API using Python3, PyQt5, and the Boto3 SDK.  

You'll need S3 keys and a valid bucket name in order to use this application. You can specify any region, it just needs to be valid.

Region list: 

https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html

### Notes

All development and testing thusfar has been performed on macOS Mojave. 

### Logging

I've built in a remote logging feature so you are alerted when an upload succeeds or fails. If you don't want to log anything, you'll need to (at the very least):

Remove the `GetAuthToken` function.

Change the call to `self.GetAuthToken()` in `GetRegion` to `self.GetBucket()`.

Remove the `self.AUTH_TOKEN` variable in the `UI` function. 

Define `LOG_LOCATION` as a blackhole. 127.0.0.1 should work. The logging function is a `try/except` block. It _should_ error silently if it can't connect.

Of course, the clean way to remove logging is perform the above steps, remove the `try/except` blocks, and remove the logging variables in lines 45-47ish.


If you _do_ want to set up remote logging, you're in luck. I wrote a logging server in Go. 

### logging-server.go

High level: 

Posts to Slack when there are success or failures with the app.

In Depth: 

Coming soon but I want to go home today.


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
