#!/usr/bin/env python3
"""
A wrapper for the S3 API

Regretful Developer: Mitch Anderson

Virtualenv steps: python3 -m virtualenv <Virtual env name>
In virtualenv : pip3 install boto3; pip3 install pyqt5; pip3 install botocore; pip3 install ntpath

"""
import boto3, PyQt5, sys, os, json, getpass, botocore, ntpath, urllib3, platform
from botocore import *

from PyQt5 import QtWidgets, QtGui
# Need to narrow this down
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QPushButton, QToolTip, QMessageBox, QInputDialog, QDesktopWidget, QMainWindow, QStatusBar, 
    QLineEdit, QTextEdit, QGridLayout, QHBoxLayout, QFrame, QSplitter, QStyleFactory, QFileDialog, QAction)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont, QImage, QPalette, QBrush


APP_ICON = "include/bhi.png"

# Set these here so we can change for different business units
WINDOW_TITLE = "BHI SFTP"
ERR_WINDOW_TITLE = "Credential Error"
MAIN_TOOLTIP = "BHI Born and Raised SFTP Program"
UPLOAD_TOOLTIP = "Securely upload files to BHI\nShortcut: Cmd+U"
QUIT_TOOLTIP = "Quit the program\nShortcut: Cmd+Q"
CLEAR_CREDS_TOOLTIP = "Delete your SFTP credentials\nShortcut: Cmd+D"
CREDS_PROMPT_TITLE = "BHI SFTP CREDENTIALS"
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

KEYS_FILE = os.path.join(BHI_LOCATION, "key_secret.py")

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
                with open(KEYS_FILE, "r") as KF:
                    KF_LINES = KF.read().splitlines()
                    # Add these variables to the sftpUI class
                    self.s3_access_key = KF_LINES[0]
                    self.s3_secret_key = KF_LINES[1]
                    self.s3_region = KF_LINES[2]
                    KF.close()
                pass
            # Credentials don't exist, go to pop up for access key
            else:
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
            QUIT_BUTTON.resize(QUIT_BUTTON.sizeHint())
            # Jump to confirming they want to quit
            QUIT_BUTTON.clicked.connect(self.ConfirmQuit)
            

             # Create upload button
            UPLOAD_BUTTON = QPushButton('Upload', self)
            UPLOAD_BUTTON.setShortcut("Ctrl+U")
            # Create tooltip for upload_button
            UPLOAD_BUTTON.setToolTip(UPLOAD_TOOLTIP)
            # Set recommended button size
            UPLOAD_BUTTON.resize(UPLOAD_BUTTON.sizeHint())

            # Call function when Upload clicked
            UPLOAD_BUTTON.clicked.connect(self.uploadS3)
            

            # Create clear credentials button
            CLEAR_CREDENTIALS = QPushButton('Clear Credentials', self)
            CLEAR_CREDENTIALS.setShortcut("Ctrl+D")
            CLEAR_CREDENTIALS.setToolTip(CLEAR_CREDS_TOOLTIP)
            CLEAR_CREDENTIALS.resize(CLEAR_CREDENTIALS.sizeHint())

            # Jump to confirming they want to quit
            CLEAR_CREDENTIALS.clicked.connect(self.clearCredentials)
            

            # Define main window size and location
            GRID_WINDOW = QGridLayout()
            self.setLayout(GRID_WINDOW)
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
            
            # Create list of buttons for layout:

            BUTTONS = [QUIT_BUTTON, CLEAR_CREDENTIALS, UPLOAD_BUTTON]

            # Create list of positions for buttons, x, y coordinates
            # If another button is needed, increment range 
            BUTTON_POSITIONS = [(i,j) for i in range(3) for j in range(3)]

            # Generate layout
            for BUTTON, POSITION in zip(BUTTONS, BUTTON_POSITIONS):
                GRID_WINDOW.addWidget(BUTTON, *POSITION)
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
        # Create popup
        text, okPressed = QInputDialog.getText(self, CREDS_PROMPT_TITLE, "SFTP Acces Key", QLineEdit.Normal, "")
        if okPressed and text != '':
            with open(KEYS_FILE, "a") as KF:
                KF.write(str(text))
                KF.close()
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
            with open(KEYS_FILE, "a") as KF:
                KF.write("\n")
                KF.write(str(text))
                KF.close()
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
            with open(KEYS_FILE, "a") as KF:
                KF.write("\n")
                KF.write(str(text))
                KF.close()
                # We're ok to move to UI now, we have Access, Secret, and Region
                self.UI()
        # They've already cancelled access, let's quit this pop up. We'll error out later but we'll catch it
        elif not okPressed:
            QApplication.instance().quit
        else:
            # They pressed ok but with no input, prompt again
            self.GetRegion()

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
            # Try to connect and list buckets.
            
            s3 = boto3.resource('s3', aws_access_key_id=self.s3_access_key, aws_secret_access_key=self.s3_secret_key, region_name=self.s3_region)
            # might be able to ditch client
            #client = boto3.client('s3', aws_access_key_id=self.s3_access_key, aws_secret_access_key=self.s3_secret_key, region_name=self.s3_region)

            # Create list for buckets -- this should create a drop down list
            buckets = []

            try:
                for bucket in s3.buckets.all():
                # Put existing buckets in list
                    buckets.append(bucket.name)
                #print(buckets[0])
                self.UPLOAD_BUCKET = buckets[0]
                self.fileSelector(s3)

            except botocore.exceptions.ClientError as e:
                # Cast error to a string so we can look for the reason behind the error

                ERROR_MESSAGE = str(e)
                print(ERROR_MESSAGE)
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
                self.ERROR = "Invalid Region"
                self.FULL_ERROR = ERROR_MESSAGE
                self.badCredentialsError()

            # Things got weird with urllib3
            #except urllib3.exceptions.NewConnectionError as e:
            #    print("URLLIB")
    
            except Exception as e:
                ERROR_MESSAGE = str(e)

                # Catch all
                self.ERROR = "Unknown error"
                self.FULL_ERROR = ERROR_MESSAGE
                self.badCredentialsError()
        except Exception as e:
            ERROR_MESSAGE = str(e)
            self.ERROR = "Unhandled error"
            self.FULL_ERROR = ERROR_MESSAGE
            self.badCredentialsError()
    def fileSelector(self, s3):
        UPLOAD_BUCKET = self.UPLOAD_BUCKET
        # Open window to select file, grab item at 0 index so we don't include filter
        FILES_TO_UPLOAD = QFileDialog.getOpenFileNames(self, 'Open file', DEFAULT_BROWSER_LOCATION)[0]

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
        ALERT_CREDENTIALS.exec_()
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = sftpUI()
    sys.exit(app.exec_())
