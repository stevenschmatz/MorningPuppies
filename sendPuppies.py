#!/usr/bin/python

# Steven Schmatz
# December 10, 2014
# The things I do instead of studying for finals... :D

import urllib, json, pycurl
import os, re, sys, smtplib
import random

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
DIRECTORY = "/Your/Directory"

class EmailSender():
	"""	An SMTP email sending client that can send an email with
		attachments to multiple people.
	"""

	# =======
	# PRIVATE
	# =======

	def __init__(self, subject):
		# Authentication information
		self._sender = 'senderAddress@mail.com'
		self._password = "yourPassword"

		# Message contents
		self._recipient = 'some-dude723@mail.com'
		self._subject = subject
		self._initMessage()

	"""
	MODIFIES: self.msg
	EFFECTS:  Creates an email message with the given subject and message.
	"""
	def _initMessage(self):
		self.msg = MIMEMultipart()
		self.msg['Subject'] = self._subject
		self.msg['To'] = self._recipient
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
	 
		session.sendmail(self._sender, self._recipient, self.msg.as_string())
		session.quit()

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
 
def main():
	morningPuppiesSender = MorningPuppiesSender("Rise and Shine!")
	morningPuppiesSender.sendEmails()
 
if __name__ == '__main__':
	main()