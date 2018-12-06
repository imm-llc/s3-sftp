#!/usr/bin/env python3
"""
A wrapper for the S3 API

Regretful Developer: Mitch Anderson

"""

import boto3, PyQt5, sys, os, json, getpass, botocore, ntpath, urllib3, platform, requests

from botocore import *

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QPushButton, QToolTip, QMessageBox, QInputDialog, QDesktopWidget, QMainWindow, 
    QLineEdit, QGridLayout, QFrame, QStyleFactory, QFileDialog, QAction, QComboBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont, QImage


APP_ICON = "include/bhi.png"
#APP_ICON = "bhi.icns"
# Set these here so we can change for different business units
WINDOW_TITLE = "BHI SFTP"
ERR_WINDOW_TITLE = "Credential Error"
MAIN_TOOLTIP = "BHI Born and Raised SFTP Program"
UPLOAD_TOOLTIP = "Securely upload files to BHI\nShortcut: Cmd+U"
QUIT_TOOLTIP = "Quit the program\nShortcut: Cmd+Q"
CLEAR_CREDS_TOOLTIP = "Delete your SFTP credentials\nShortcut: Cmd+D"
NEW_BUCKET_TOOLTIP = "Add another upload bucket"

CREDS_PROMPT_TITLE = "BHI SFTP CREDENTIALS"
AUTH_TOKEN_PROMPT = "Authorization Token"
BUSINESS_UNIT = "BHI"

# Default credential location
USER = getpass.getuser()
MAC_LOCATION = "/Users/{}/.bhi/".format(USER)
WIN_LOCATION = "C:\\Users\\{}\\.bhi\\".format(USER)
LINUX_LOCATION = "/home/{}/.bhi/".format(USER)

# Default file browser location
MAC_BROWSER_LOCATION = "/Users/{}/Downloads/".format(USER)
WIN_BROWSER_LOCATION = "C:/Users/{}/Downloads".format(USER)
LINUX_BROWSER_LOCATION = "/home/{}/Downloads".format(USER)



# Loggging
LOG_LOCATION = "http://example.com"
LOG_PORT = "11223"
LOG_FULL_URL = LOG_LOCATION+":"+LOG_PORT

# What OS are we on?
OS_TYPE = platform.system()
if OS_TYPE == "Darwin":
    BHI_LOCATION = MAC_LOCATION
    DEFAULT_BROWSER_LOCATION = MAC_BROWSER_LOCATION

elif OS_TYPE == "Windows":
    BHI_LOCATION = WIN_LOCATION
    DEFAULT_BROWSER_LOCATION = WIN_BROWSER_LOCATION
else:
    BHI_LOCATION = LINUX_LOCATION
    DEFAULT_BROWSER_LOCATION = LINUX_BROWSER_LOCATION

KEYS_FILE = os.path.join(BHI_LOCATION, "key_secret.json")

# Default file browser location
MAC_BROWSER_LOCATION = "/Users/{}/Downloads/".format(USER)

class sftpUI(QWidget):
    def __init__(self):
        # Inherit from class
        super().__init__()
        # Let the UI function do the heavy lifting
        self.UI()

    def UI(self):
            # Check if credentials directory exists
            BHI_DIR_EXISTS = os.path.isdir(BHI_LOCATION)
            if not BHI_DIR_EXISTS:
                os.mkdir(BHI_LOCATION)
            else:
                pass
            # Check if credential file exists
            CREDS_FILE_EXISTS = os.path.isfile(KEYS_FILE)
            # credentials exist, go to main screen, we'll verify that they work later
            if CREDS_FILE_EXISTS:
                # Need to make this a try block
                with open(KEYS_FILE, "r") as KF:
                    JSON_AUTH_DATA = json.load(KF)
                    self.s3_access_key = JSON_AUTH_DATA['Access']
                    self.s3_secret_key = JSON_AUTH_DATA['Secret']
                    self.s3_region = JSON_AUTH_DATA['Region']
                    self.AUTH_TOKEN = JSON_AUTH_DATA['AuthToken']
                    # Set default bucket
                    self.UPLOAD_BUCKET = JSON_AUTH_DATA['Bucket'][0]
                    # Build empty list
                    self.BUCKET_LIST = []
                    self.ALL_BUCKETS = JSON_AUTH_DATA['Bucket']
                    # Add buckets to list
                    for BUCKET in self.ALL_BUCKETS:
                        self.BUCKET_LIST.append(BUCKET)
                    KF.close()
                pass
            # Credentials don't exist, go to pop up for access key
            else:
                #print("no creds")
                self.GetAccessKey()
            

            # Start creating buttons

            # Set tooltip font
            QToolTip.setFont(QFont('SansSerif', 10))
            # Create tooltip for app
            self.setToolTip(MAIN_TOOLTIP)
                       
            # Create quit button
            QUIT_BUTTON = QPushButton('Quit', self)
            QUIT_BUTTON.setShortcut("Ctrl+Q")
            # Quit button tooltip definition
            QUIT_BUTTON.setToolTip(QUIT_TOOLTIP)
            # Jump to confirming they want to quit
            QUIT_BUTTON.clicked.connect(self.ConfirmQuit)
            QUIT_BUTTON.resize(QUIT_BUTTON.sizeHint())

            # Create upload button
            UPLOAD_BUTTON = QPushButton('Upload', self)
            UPLOAD_BUTTON.setShortcut("Ctrl+U")
            # Create tooltip for upload_button
            UPLOAD_BUTTON.setToolTip(UPLOAD_TOOLTIP)
            # Set recommended button size
            UPLOAD_BUTTON.resize(UPLOAD_BUTTON.sizeHint())

            # Call function when Upload clicked
            UPLOAD_BUTTON.clicked.connect(self.uploadS3)

            # Create Add New Bucket button
            ADD_BUCKET = QPushButton('Add New Bucket', self)
            ADD_BUCKET.setShortcut("Ctrl+N")
            ADD_BUCKET.setToolTip(NEW_BUCKET_TOOLTIP)
            ADD_BUCKET.resize(ADD_BUCKET.sizeHint())
            ADD_BUCKET.clicked.connect(self.AddNewBucket)
            

            # Create clear credentials button
            CLEAR_CREDENTIALS = QPushButton('Clear Credentials', self)
            CLEAR_CREDENTIALS.setShortcut("Ctrl+D")
            CLEAR_CREDENTIALS.setToolTip(CLEAR_CREDS_TOOLTIP)
            # Jump to confirming they want to quit
            CLEAR_CREDENTIALS.clicked.connect(self.clearCredentials)
            CLEAR_CREDENTIALS.resize(CLEAR_CREDENTIALS.sizeHint())

            # Define main window size and location
            self.GRID_WINDOW = QGridLayout()
            self.setLayout(self.GRID_WINDOW)
            # Set Window Title
            self.setWindowTitle(WINDOW_TITLE)
            # Set Tray icon
            self.setWindowIcon(QIcon(APP_ICON))
            
            # Not working yet

            #BACKGROUND = QImage(APP_ICON)
            #scaled_image = BACKGROUND.scaled(QSize(138, 177))
            #palette = QPalette()
            #palette.setBrush(1, QBrush(scaled_image))
            #self.setPalette(palette)
            # Build bucket list for dropdown
            self.BUCKET_LIST_BOX = QComboBox(self)
            if len(self.BUCKET_LIST) < 2:
                self.UPLOAD_BUCKET = self.UPLOAD_BUCKET
                self.BUCKET_LIST_BOX.addItem(self.UPLOAD_BUCKET)
                self.GRID_WINDOW.addWidget(self.BUCKET_LIST_BOX, 3, 3)
            else:
                for BUCKET in self.BUCKET_LIST:
                    self.BUCKET_LIST_BOX.addItem(BUCKET)
                self.GRID_WINDOW.addWidget(self.BUCKET_LIST_BOX, 3, 3)


            
            
            # Create list of buttons for layout:

            BUTTONS = [QUIT_BUTTON, CLEAR_CREDENTIALS, ADD_BUCKET, UPLOAD_BUTTON]

            # Create list of positions for buttons, x, y coordinates
            # If another button is needed, increment range 
            BUTTON_POSITIONS = [(i,j) for i in range(4) for j in range(4)]

            # Generate layout
            for BUTTON, POSITION in zip(BUTTONS, BUTTON_POSITIONS):
                self.GRID_WINDOW.addWidget(BUTTON, *POSITION)
            
            self.move(300, 150)

            # Create window
            self.show()

    def ConfirmQuit(self):
        # Title of popup,  Message in text field, option 1, option 2, default
        confirmation = QMessageBox.question(self, "Message", "Are you sure you want to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            sys.exit()
        else:
            # Quit this pop up
            QApplication.instance().quit
    
    def GetAccessKey(self):
        # Create initial JSON for auth
        self.AUTH_JSON = {}
        # Create popup
        text, okPressed = QInputDialog.getText(self, CREDS_PROMPT_TITLE, "SFTP Acces Key", QLineEdit.Normal, "")
        if okPressed and text != '':
            self.AUTH_JSON['Access'] = str(text)
            self.GetSecretKey()
        # If cancel is pressed, go to GetSecretKey function
        elif not okPressed:
            self.GetSecretKey()
        # They pressed ok but with no input, prompt again
        else:
            self.GetAccessKey()
    def GetSecretKey(self):
        text, okPressed = QInputDialog.getText(self, CREDS_PROMPT_TITLE, "SFTP Secret Key", QLineEdit.Normal, "")
        if okPressed and text != '':
            self.AUTH_JSON['Secret'] = str(text)
            self.GetRegion()
        # They cancelled, move on to region
        elif not okPressed:
            self.GetRegion()
        else:
            # They pressed ok but with no input, prompt again
            self.GetSecretKey()
    def GetRegion(self):
        text, okPressed = QInputDialog.getText(self, CREDS_PROMPT_TITLE, "SFTP Region", QLineEdit.Normal, "")
        if okPressed and text != '':
            self.AUTH_JSON['Region'] = str(text)
            # We're ok to move to UI now, we have Access, Secret, and Region
            self.GetAuthToken()
        # They've already cancelled access, let's quit this pop up. We'll error out later but we'll catch it
        elif not okPressed:
            QApplication.instance().quit
        else:
            # They pressed ok but with no input, prompt again
            self.GetRegion()
    def GetAuthToken(self):
        text, okPressed = QInputDialog.getText(self, AUTH_TOKEN_PROMPT, "Authorization Token", QLineEdit.Normal, "")
        if okPressed and text != '':
            self.AUTH_JSON['AuthToken'] = str(text)
            # We're ok to move to UI now, we have Access, Secret, and Region
            self.GetBucket()
        # They've already cancelled access, let's quit this pop up. We'll error out later but we'll catch it
        elif not okPressed:
            QApplication.instance().quit
        else:
            # They pressed ok but with no input, prompt again
            self.GetAuthToken()
    def GetBucket(self):
        text, okPressed = QInputDialog.getText(self, CREDS_PROMPT_TITLE, "SFTP Bucket", QLineEdit.Normal, "")
        if okPressed and text != '':
            self.AUTH_JSON['Bucket'] = []
            self.AUTH_JSON['Bucket'].append(str(text))
            with open(KEYS_FILE, "w") as KF:
                # Write final JSON to file
                KF.write(json.dumps(self.AUTH_JSON))

                # We're ok to move to UI now, we have Access, Secret, and Region
            self.UI()
        # They've already cancelled access, let's quit this pop up. We'll error out later but we'll catch it
        elif not okPressed:
            QApplication.instance().quit
        else:
            # They pressed ok but with no input, prompt again
            self.GetBucket()
    
    def AddNewBucket(self):
        text, okPressed = QInputDialog.getText(self, CREDS_PROMPT_TITLE, "SFTP Bucket", QLineEdit.Normal, "")
        NEW_BUCKET = str(text)
        if okPressed and text != '':
            with open(KEYS_FILE, "r") as KF:
                UPDATED_JSON = json.load(KF)
                KF.close()
            UPDATED_JSON['Bucket'].append(NEW_BUCKET)
            with open(KEYS_FILE, "w") as KF:
                KF.write(json.dumps(UPDATED_JSON))
                KF.close()
            self.NotifyForRelaunch()

            # Add alert telling them to relaunch App
        elif not okPressed:
            QApplication.instance().quit
        else:
            self.UI()

            #with open(self.KEYS_FILE)


    def clearCredentials(self):
        confirmation = QMessageBox.question(self, "Confirmation", "Delete Credentials?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            os.remove(KEYS_FILE)
            self.UI()
        else:
            # Quit this pop up
            QApplication.instance().quit
    def uploadS3(self):

        try:
            # establish s3 var    
            s3 = boto3.resource('s3', aws_access_key_id=self.s3_access_key, aws_secret_access_key=self.s3_secret_key, region_name=self.s3_region)

            try:
                # Set UPLOAD.BUCKET to whatever is currently selected in the dropdown

                self.UPLOAD_BUCKET = str(self.BUCKET_LIST_BOX.currentText())
                #print(self.UPLOAD_BUCKET)
                # Try to list bucket contents
                CHECK_BUCKET_CONNECTION = s3.Bucket(self.UPLOAD_BUCKET)
                for item in CHECK_BUCKET_CONNECTION.objects.all():
                    with open(os.devnull, "w") as DEV:
                        DEV.write(str(item))

                # Create label verifying connection is OK
                self.GRID_WINDOW.addWidget(QLabel("SFTP Connection to {} OK".format(self.UPLOAD_BUCKET)), 3, 1)
                
                # Call fileSelector function, pass s3 to make life easy
                self.fileSelector(s3)

            except botocore.exceptions.ClientError as e:
                # Cast error to a string so we can look for the reason behind the error

                ERROR_MESSAGE = str(e)
                self.GRID_WINDOW.addWidget(QLabel('SFTP Connection Failed'), 1, 1)

                #print(ERROR_MESSAGE)
                if "InvalidAccessKeyId" in ERROR_MESSAGE:
                    # Define short error message
                    self.ERROR = "Invalid Access Key"
                    # Give full error
                    self.FULL_ERROR = ERROR_MESSAGE
                    self.badCredentialsError()
                elif "SignatureDoesNotMatch" in ERROR_MESSAGE:
                    self.ERROR = "Invalid Secret Key"
                    self.FULL_ERROR = ERROR_MESSAGE
                    self.badCredentialsError()
                else:
                    self.ERROR = "Unknown error with SFTP Client"
                    self.FULL_ERROR = ERROR_MESSAGE
                    self.badCredentialsError()
            except botocore.exceptions.EndpointConnectionError as e:
                ERROR_MESSAGE = str(e)
                self.GRID_WINDOW.addWidget(QLabel('SFTP Connection Failed'), 1, 1)
                self.ERROR = "Invalid Region"
                self.FULL_ERROR = ERROR_MESSAGE
                self.badCredentialsError()

            # Things got weird with urllib3
            #except urllib3.exceptions.NewConnectionError as e:
            #    print("URLLIB")
    
            except Exception as e:
                ERROR_MESSAGE = str(e)
                self.GRID_WINDOW.addWidget(QLabel('SFTP Connection Failed'), 1, 1)

                # Catch all
                self.ERROR = "Unknown error"
                self.FULL_ERROR = ERROR_MESSAGE
                self.badCredentialsError()
        except Exception as e:
            ERROR_MESSAGE = str(e)
            self.GRID_WINDOW.addWidget(QLabel('SFTP Connection Failed'), 1, 1)
            self.ERROR = "Unhandled error"
            self.FULL_ERROR = ERROR_MESSAGE
            self.badCredentialsError()
    def fileSelector(self, s3):
        UPLOAD_BUCKET = self.UPLOAD_BUCKET

        # Open window to select file, grab item at 0 index so we don't include filter
        FILES_TO_UPLOAD = QFileDialog.getOpenFileNames(self, 'Open file', MAC_BROWSER_LOCATION)[0]

        if FILES_TO_UPLOAD:
            COUNT = len(FILES_TO_UPLOAD)
            if COUNT < 2:
                FILE_PLURAL = "file"
            else:
                FILE_PLURAL = "files"
            for FILE in FILES_TO_UPLOAD:
                # Can comment out if not debugging
                #print("DEBUG MODE: NOT UPLOADING")
                # Can comment out if not debugging
                #print("Full Path: {}".format(str(FILE)))
                ### Do not comment out
                PATH, FILE_NAME = ntpath.split(str(FILE))
                # Can comment out if not debugging
                #print("Uploading: {} to {}".format(FILE_NAME, UPLOAD_BUCKET))

                # Uncomment following line to enable uploading

                #s3.meta.client.upload_file(FILE, UPLOAD_BUCKET, FILE_NAME)
                # Can comment out if not debugging
                #ALERT_SUCCESS = QMessageBox()
                # Can comment out if not debugging
                #ALERT_SUCCESS.setIcon(QMessageBox.Information)
                # Can comment out if not debugging
                #ALERT_SUCCESS.setText("Successfully uploaded {} {} to {}".format(str(COUNT), FILE_PLURAL, BUSINESS_UNIT))
                # Can comment out if not debugging
                #ALERT_SUCCESS.setWindowTitle(WINDOW_TITLE)
                # Can comment out if not debugging
                #ALERT_SUCCESS.setStandardButtons(QMessageBox.Ok)
                # Can comment out if not debugging
                #ALERT_SUCCESS.exec_()
        
                # Commented for debugging/non-prod
                # Call s3 to upload file; parameters = Local file, Bucket to upload to, destination name
                # We want destination file name to be _just_ the filename itself, otherwise you're creating a nasty path in S3
                try:
                    ########################## (Local file, Bucket to upload to, destination name)
                    s3.meta.client.upload_file(FILE, UPLOAD_BUCKET, FILE_NAME)
                    # Build success alert message 
                    ALERT_SUCCESS = QMessageBox()
                    ALERT_SUCCESS.setIcon(QMessageBox.Information)
                    ALERT_SUCCESS.setText("Successfully uploaded {} {} to {}".format(str(COUNT), FILE_PLURAL, BUSINESS_UNIT))
                    ALERT_SUCCESS.setWindowTitle(WINDOW_TITLE)
                    ALERT_SUCCESS.setStandardButtons(QMessageBox.Ok)
                    
                    # Send log message first
                    try:
                        JSON_SUCCESS = {}
                        JSON_SUCCESS['Auth'] = self.AUTH_TOKEN # Set per client
                        JSON_SUCCESS['Action'] = "Success"
                        JSON_SUCCESS['LogMessage'] = "Successful upload to {}".format(UPLOAD_BUCKET)
                        requests.post(LOG_FULL_URL, data=json.dumps(JSON_SUCCESS))
                    except:
                        # If we can't send the error to the log endpoint, fail silently
                        continue
                    
                    ALERT_SUCCESS.exec_()

                # Generic exception, not sure what errors will be thrown here
                except Exception as e:
                    FULL_ERROR = str(e)
                    ALERT_FAIL = QMessageBox()
                    ALERT_FAIL.setIcon(QMessageBox.Critical)
                    ALERT_FAIL.setInformativeText("Click 'Show Details...' for full error")
                    ALERT_FAIL.setDetailedText(FULL_ERROR)
                    ALERT_FAIL.setText("Failed to upload {} {} to {}".format(str(COUNT), FILE_PLURAL, BUSINESS_UNIT))
                    ALERT_FAIL.setWindowTitle(WINDOW_TITLE)
                    ALERT_FAIL.setStandardButtons(QMessageBox.Ok)
                    try:
                        JSON_ERROR = {}
                        JSON_ERROR['Auth'] = self.AUTH_TOKEN # Set per client
                        JSON_ERROR['Action'] = "Fail"
                        JSON_ERROR['LogMessage'] = FULL_ERROR
                        print(FULL_ERROR)
                        print(LOG_FULL_URL)
                        requests.post(LOG_FULL_URL, data=json.dumps(JSON_ERROR))
                        
                    except:
                        # If we can't send the error to the log endpoint, fail silently
                        pass
                    ALERT_FAIL.exec_()
    def badCredentialsError(self):

        # Build credential error message 
        ALERT_CREDENTIALS = QMessageBox()
        ALERT_CREDENTIALS.setIcon(QMessageBox.Critical)
        ALERT_CREDENTIALS.setText("Error: {}".format(self.ERROR))
        ALERT_CREDENTIALS.setInformativeText("Click 'Show Details...' for full error")
        ALERT_CREDENTIALS.setDetailedText(self.FULL_ERROR)
        ALERT_CREDENTIALS.setWindowTitle(ERR_WINDOW_TITLE)
        ALERT_CREDENTIALS.setStandardButtons(QMessageBox.Ok)
        
        # Send log message first
        try:
            JSON_ERROR = {}
            JSON_ERROR['Auth'] = self.AUTH_TOKEN # Set per client
            JSON_ERROR['Action'] = "Fail"
            JSON_ERROR['LogMessage'] = self.FULL_ERROR
            requests.post(LOG_FULL_URL, data=json.dumps(JSON_ERROR))
        except:
            # If we can't send the error to the log endpoint, fail silently
            pass
        
        # Open alert popup
        ALERT_CREDENTIALS.exec_()
    
    def NotifyForRelaunch(self):
        RELAUNCH_NOTIFICATION = QMessageBox()
        RELAUNCH_NOTIFICATION.setIcon(QMessageBox.Information)
        RELAUNCH_NOTIFICATION.setText("Please restart the application to use new bucket")
        RELAUNCH_NOTIFICATION.setWindowTitle("New Bucket Added")
        RELAUNCH_NOTIFICATION.setStandardButtons(QMessageBox.Ok)
        RELAUNCH_NOTIFICATION.exec_()
        

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = sftpUI()
    sys.exit(app.exec_())
