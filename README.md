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

The logging server is my first brush with Go so keep that in mind. The application formats a JSON containing an auth token ('Auth'), the status of the action ('Action'), and a more descriptive message ('LogMessage').

The auth token is provided during the first run of the application, or if the credentials are cleared. There are no requirements for the auth token as far as length/complexity goes. They need to be stored server-side in whichever file you define. Do a search for "// Open allowed tokens file" in logging-server.go to find where you define this file location. I added this as a safeguard against, well, unauthorized use of the server.

Once the server receives a properly authenticated JSON, it parses the JSON and formats a Slack message. In order for the Slack integration to work, you'll need to create a bot and add the bot token to the program. slack_api is the variable for the bot token.

The Slack attachment color depends on if the value is 'Success' or 'Fail'. If there was a failure, the full error from the application should be sent to Slack. I wrote it this way to give a head start on user complaints.

If there's a successful upload, you'll receive a message saying "Successfully upload to ". That way files don't sit un-actioned in S3. It also keeps you from having to check S3 to see if a new file was uploaded.

I added an untested setup for TLS in the server. It might work, it might not. You can run a reverse proxy for encryption as well. The default port for logging-server is TCP/31313.

I recommend compiling the program with go build and creating a service file for it.

There is a built-in health check function for the Go server. By default, it's /health-check. This will return a simple "pong" in response to a GET request. There's no authorization on this endpoint.


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
