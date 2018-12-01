#!/usr/bin/env python3
"""
A wrapper for the S3 API

Regretful Developer: Mitch Anderson

Virtualenv steps: python3 -m virtualenv <Virtual env name>
In virtualenv : pip3 install boto3; pip3 install pyqt5; pip3 install botocore; pip3 install ntpath

"""
import boto3, PyQt5, sys, os, json, getpass, botocore, ntpath
from botocore import *

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QPushButton, QToolTip, QMessageBox, QInputDialog, QDesktopWidget, QMainWindow, QStatusBar, 
    QLineEdit, QTextEdit, QGridLayout, QHBoxLayout, QFrame, QSplitter, QStyleFactory, QFileDialog, QAction)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont, QImage, QPalette, QBrush

KEYS_FILE = "key_secret.py"
APP_ICON = "include/bhi.png"
# Set these here so we can change for different business units
WINDOW_TITLE="BHI SFTP"
MAIN_TOOLTIP = "BHI Born and Raised SFTP Program"
UPLOAD_TOOLTIP = "Securely upload files to BHI"
QUIT_TOOLTIP = "Quit the program"
CLEAR_CREDS_TOOLTIP = "Delete your SFTP credentials"
CREDS_PROMPT_TITLE = "BHI SFTP CREDENTIALS"
BUSINESS_UNIT = "BHI"

# Default credential location
USER = getpass.getuser()
MAC_LOCATION = "/Users/{}/.bhi/".format(USER)
WIN_LOCATION = "C:\\Users\\{}\\.bhi\\".format(USER)
LINUX_LOCATION = "/home/{}/.bhi/".format(USER)
#KEYS_FILE = os.path.join(xxx_LOCATION, "key_secret.py")

# Default file browser location
MAC_BROWSER_LOCATION = "/Users/{}/Downloads/".format(USER)
#class sftpUI(QMainWindow, QWidget):
class sftpUI(QWidget):
    def __init__(self):
        # Inherit from class
        super().__init__()
        # Let the UI function do the heavy lifting
        self.UI()
        #self.GetCredentials()


    def UI(self):
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
                #print("no creds")
                self.GetAccessKey()
            
            # Define main window size and location
            self.setGeometry(300, 300, 450, 350)
            # Set Window Title
            self.setWindowTitle(WINDOW_TITLE)
            # Set Tray icon
            self.setWindowIcon(QIcon(APP_ICON))
            # Create boxes

            # Set tooltip font
            QToolTip.setFont(QFont('SansSerif', 10))
            # Create tooltip for app
            self.setToolTip(MAIN_TOOLTIP)
                       
            # Create quit button
            quit_button = QPushButton('Quit', self)
            # Quit button tooltip definition
            quit_button.setToolTip(QUIT_TOOLTIP)
            # Jump to confirming they want to quit
            quit_button.clicked.connect(self.ConfirmQuit)
            quit_button.resize(quit_button.sizeHint())
            quit_button.move(1, 300)

             # Create upload button
            upload_button = QPushButton('Upload', self)
            # Create tooltip for upload_button
            upload_button.setToolTip(UPLOAD_TOOLTIP)
            #upload_button.clicked.connect(self.uploadS3(s3_access_key, s3_secret_key, s3_region))
            upload_button.clicked.connect(self.uploadS3)
            # Set recommended button size
            upload_button.resize(upload_button.sizeHint())
            upload_button.move(350, 300)
            #self.statusBar().showMessage('Ready')

            # Create clear credentials button
            clear_credentials = QPushButton('Clear Credentials', self)
            clear_credentials.setToolTip(CLEAR_CREDS_TOOLTIP)
            # Jump to confirming they want to quit
            clear_credentials.clicked.connect(self.clearCredentials)
            clear_credentials.resize(clear_credentials.sizeHint())
            clear_credentials.move(150, 300)
          
            """

            # Define main window
            window_box = QHBoxLayout(self)
            # Create top left box
            topleft_box = QFrame(self)
            topleft_box.setFrameShape(QFrame.StyledPanel)

            # Create top right box
            topright_box = QFrame(self)
            topright_box.setFrameShape(QFrame.StyledPanel)

            # Create bottom box
            bottom_box = QFrame(self)
            bottom_box.setFrameShape(QFrame.StyledPanel)
            
            # Split window horizontally
            splitter1 = QSplitter(Qt.Horizontal)
            # Add topleft_box to horizontal section
            splitter1.addWidget(topleft_box)
            #splitter1.addWidget(quit_button)
            #splitter1.addWidget(upload_button)
            # Add topright_box to horizontal section
            splitter1.addWidget(topright_box)
            # Split vertically
            splitter2 = QSplitter(Qt.Vertical)
            # Add horizontal split to this splitter. Not sure why
            splitter2.addWidget(splitter1)
            #splitter2.addWidget(bottom_box)
            splitter2.addWidget(quit_button)
            splitter2.addWidget(upload_button)
            #splitter2.addWidget(quit_button)
            # Add horizontal split to window
            window_box.addWidget(splitter2)
            

            # Define window size
            
            self.setGeometry(300, 300, 400, 400)
            # Set Window Title
            self.setWindowTitle(WINDOW_TITLE)
            # Set Tray icon
            self.setWindowIcon(QIcon(APP_ICON))
            """
            
            # Not working yet

            #BACKGROUND = QImage(APP_ICON)
            #scaled_image = BACKGROUND.scaled(QSize(138, 177))
            #palette = QPalette()
            #palette.setBrush(1, QBrush(scaled_image))
            #self.setPalette(palette)

            # Generate layout
            self.layout()
            # Run it
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
            client = boto3.client('s3', aws_access_key_id=self.s3_access_key, aws_secret_access_key=self.s3_secret_key, region_name=self.s3_region)
            
            # Create list for buckets -- this should create a drop down list
            buckets = []
            for bucket in s3.buckets.all():
                # Put existing buckets in list
                buckets.append(bucket.name)
            # print first bucket in list, debugging purposes
            print(buckets[0])
            UPLOAD_BUCKET = buckets[0]
        except botocore.exceptions.ClientError as e:
            # Cast error to a string so we can look for the reason behind the error
            ERROR_MESSAGE = str(e)
            if "InvalidAccessKeyId" in ERROR_MESSAGE:
                # Need to get this into widget/alarm
                print("Invalid Access Key")
            elif "SignatureDoesNotMatch" in ERROR_MESSAGE:
                print("Invalid Secret Key")
            else:
                print("Unknown error")

        except botocore.exceptions.EndpointConnectionError as e:
            # Need to get this into a widget/alarm
            print("Invalid Region")
 
        except Exception as e:
            # Catch all
            print(e)
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
                print("DEBUG MODE: NOT UPLOADING")
                # Can comment out if not debugging
                print("Full Path: {}".format(str(FILE)))
                ### Do not comment out
                PATH, FILE_NAME = ntpath.split(str(FILE))
                # Can comment out if not debugging
                print("Uploading: {} to {}".format(FILE_NAME, UPLOAD_BUCKET))
                # Can comment out if not debugging
                ALERT_SUCCESS = QMessageBox()
                # Can comment out if not debugging
                ALERT_SUCCESS.setIcon(QMessageBox.Information)
                # Can comment out if not debugging
                ALERT_SUCCESS.setText("Successfully uploaded {} {} to {}".format(str(COUNT), FILE_PLURAL, BUSINESS_UNIT))
                # Can comment out if not debugging
                ALERT_SUCCESS.setWindowTitle(WINDOW_TITLE)
                # Can comment out if not debugging
                ALERT_SUCCESS.setStandardButtons(QMessageBox.Ok)
                # Can comment out if not debugging
                ALERT_SUCCESS.exec_()



                # Commented for debugging
                # Call s3 to upload file, parameters = Local file, Bucket to upload to, destination name
                # We want destination file name to be _just_ the filename itself, otherwise you're creating a nasty path in S3
                #try:
                    #s3.meta.client.upload_file(FILE, UPLOAD_BUCKET, FILE_NAME)
                    # Build success alert message 
                    #ALERT_SUCESS = QMessageBox()
                    #ALERT_SUCCESS.setIcon(QMessageBox.Information)
                    #ALERT_SUCCESS.setText("Successfully uploaded {} {} to {}".format(str(COUNT), FILE_PLURAL, BUSINESS_UNIT))
                    #ALERT_SUCCESS.setWindowTitle(WINDOW_TITLE)
                    #ALERT_SUCCESS.setStandardButtons(QMessageBox.Ok)
                    #ALERT_SUCCESS.exec_()
                # Generic exception, not sure what errors will be thrown here
                # except Exception as e:
                    #ALERT_FAIL = QMessageBox()
                    #ALERT_FAIL.setIcon(QMessageBox.Critical)
                    #ALERT_FAIL.setText("Failed to upload {} {} to {}".format(str(COUNT), FILE_PLURAL, BUSINESS_UNIT))
                    #ALERT_FAIL.setWindowTitle(WINDOW_TITLE)
                    #ALERT_FAIL.setStandardButtons(QMessageBox.Ok)
                    #ALERT_FAIL.exec_()

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = sftpUI()
    sys.exit(app.exec_())

"""
bad access:
An error occurred (InvalidAccessKeyId) when calling the ListBuckets operation: The request signature we calculated does not match the signature you provided. Check your key and signing method.
bad secret: 
An error occurred (SignatureDoesNotMatch) when calling the ListBuckets operation: The request signature we calculated does not match the signature you provided. Check your key and signing method.

bad region: 
botocore.exceptions.EndpointConnectionError: Could not connect to the endpoint URL: "https://s3.us-est-1.amazonaws.com/"
"""
