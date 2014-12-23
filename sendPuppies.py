#!/usr/bin/env python

# Steven Schmatz
# December 10, 2014
# The things I do instead of studying for finals... :D

import urllib, json, pycurl
import os, re, sys, smtplib
import random

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Example SMTP server – gmail.com
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
DIRECTORY = "/Directory/to/save/image/temporarily"

SENDER_EMAIL_ADDRESS = 'xxxxxx@mail.com'
SENDER_EMAIL_SECRET = "xxxxxx"
RECIPIENT_ADDRESSES = ["address1@mail.org"]

EMAIL_SENDING_HOUR = 8 # 8:00am
EMAIL_SUBJECT = "Rise and Shine!"


"""
=================
class EmailSender
=================
"""

class EmailSender():
	"""	An SMTP email sending client that can send an email with
		attachments to multiple people.
	"""

	# =======
	# PRIVATE
	# =======

	def __init__(self, subject):
		# Authentication information
		self._sender = SENDER_EMAIL_ADDRESS
		self._password = SENDER_EMAIL_SECRET

		# Message contents
		self._subject = subject
		self._initMessage()

	"""
	MODIFIES: self.msg
	EFFECTS:  Creates an email message with the given subject and message.
	"""
	def _initMessage(self):
		self.msg = MIMEMultipart()
		self.msg['Subject'] = self._subject
		self.msg['From'] = self._sender

	"""
	MODIFIES: self.msg
	EFFECTS:  Attaches the given text to the email message.
	"""
	def _attachMessageText(self, htmlMessage):
		part = MIMEText('html', "html")
		part.set_payload(htmlMessage)
		self.msg.attach(part)

	# ======
	# PUBLIC
	# ======

	"""
	REQUIRES: imageFilename is a file that exists in the current directory
	MODIFIES: self.msg
	EFFECTS:  Attaches the image with the given filename to self.msg.
	"""
	def attachImage(self, imageFilename):
		path = os.path.join(DIRECTORY, imageFilename)

		img = MIMEImage(open(path, 'rb').read(), _subtype="gif")
		img.add_header('Content-Disposition', 'attachment', filename=imageFilename)
		self.msg.attach(img)

	"""
	REQUIRES: Valid connection to the Gmail SMTP server
	EFFECTS:  Sends the message to the given recipient.
	"""
	def createSessionAndSend(self):
		session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
 
		session.ehlo()
		session.starttls()
		session.ehlo
		session.login(self._sender, self._password)

		for recipient in RECIPIENT_ADDRESSES:
			self.msg['To'] = recipient
			session.sendmail(self._sender, recipient, self.msg.as_string())

		session.quit()

"""
===================
Class RepeatedTimer
===================
"""

from threading import Timer
import datetime
import threading

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

"""
==========================
Class MorningPuppiesSender
==========================
"""

class MorningPuppiesSender(EmailSender):
	""" MorningPuppies supplies all the methods to send an email of a cute
		animal each morning to everyone on an email list.
	"""

	# =======
	# PRIVATE
	# =======

	def __init__(self, subject):
		EmailSender.__init__(self, subject)
		self.cutePictureFilename = ''
		self.extension = ''
		self.caption = ''

	"""	
	REQUIRES: Connection to the internet is good.
	MODIFIES: The file cutePicture
	EFFECTS:  Saves the top imgur post from r/aww into the current 
			  directory,
	"""
	def _retrieveDailyPicture(self):
		# URL of the top r/aww posts from Reddit
		awwURL = "http://www.reddit.com/r/aww/top.json"
		response = urllib.urlopen(awwURL)
		data = json.loads(response.read())

		# Retrieve picture link and reate filename
		imgurLink = data["data"]["children"][0]["data"]["url"]
		self.caption = "<h3>\"" + data["data"]["children"][0]["data"]["title"] + "\"</h3>"
		self.extension = imgurLink[imgurLink.rfind('.'):]
		self.cutePictureFilename = "cutePicture" + self.extension

		# Save the picture
		urllib.urlretrieve(imgurLink, filename=self.cutePictureFilename)

	"""
	REQUIRES: cutePictureFilename is not empty
	MODIFIES: current directory
	EFFECTS:  Removes the imgur picture from the current directory.

	"""
	def _removePicture(self):
		if self.cutePictureFilename != '':
			os.remove(self.cutePictureFilename)

	def _attachFooterText(self):
		adjectives = ["good", "great", "spectacular", "magnificent", "splendid", "dazzling", 
			"sensational", "remarkable", "outstanding", "memorable", "unforgettable"]
		footer = "Have a " + random.choice(adjectives) + " day!"
		footerHTML = "<h3 style=\"font-weight: normal; font-style: oblique;\">" + footer + "</h3>"
		self._attachMessageText(footerHTML)

	# ======
	# PUBLIC
	# ======

	"""
	EFFECTS:  Downloads the picture, and sends an email to the given person.
	"""
	def sendEmails(self):
		self._retrieveDailyPicture()
		self.attachImage(self.cutePictureFilename)
		self._attachMessageText(self.caption)
		self._attachFooterText()
		self.createSessionAndSend()
		self._removePicture()

		print "Sent emails!"

	def initDailyEmails(self):
		SECOND = 1
		MINUTE = 60 * SECOND
		HOUR = 60 * MINUTE
		DAY = 24 * HOUR

		self.sendEmails()
		rt = RepeatedTimer(DAY, self.sendEmails)

	def initEmailSender(self, email_sending_hour):
		now = datetime.datetime.now()
		nextTimeDay = datetime.datetime.now().day

		# Ensures that emails are sent at proper time
		if now.hour >= email_sending_hour:
			nextTimeDay += 1

		nextTime = datetime.datetime(now.year, now.month, 23, 17, 43, 0)
		timeInterval = (nextTime - now).total_seconds()
		threading.Timer(timeInterval, self.initDailyEmails).start()

"""
======
main()
======
"""

def main():
	morningPuppiesSender = MorningPuppiesSender(EMAIL_SUBJECT)
	morningPuppiesSender.initEmailSender(EMAIL_SENDING_HOUR)

if __name__ == '__main__':
	main()