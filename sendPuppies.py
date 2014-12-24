#!/usr/bin/env python

"""
Steven Schmatz
December 10, 2014
The things I do instead of studying for finals... :D
"""

import urllib, json
import os, smtplib
import random

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Example SMTP server - gmail.com
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
DIRECTORY = "/Directory/to/save/image/temporarily"

SENDER_EMAIL_ADDRESS = 'xxxxxx@mail.com'
SENDER_EMAIL_SECRET = "xxxxxx"
RECIPIENT_ADDRESSES = ["address1@mail.org"]

EMAIL_SENDING_HOUR = 8 # 8:00am
EMAIL_SUBJECT = "Rise and Shine!"

SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR

"""
=================
class EmailSender
=================
"""

class EmailSender(object):
    """    An SMTP email sending client that can send an email with
        attachments to multiple people.
    """

    def __init__(self, subject):
        # Authentication information
        self._sender = SENDER_EMAIL_ADDRESS
        self._password = SENDER_EMAIL_SECRET

        # Message contents
        self._subject = subject
        self._init_message()

    # =======
    # PRIVATE
    # =======

    def _init_message(self):
        """
        MODIFIES: self.msg
        EFFECTS:  Creates an email message with the given subject and message.
        """
        self.msg = MIMEMultipart()
        self.msg['Subject'] = self._subject
        self.msg['From'] = self._sender

    def _attach_message_text(self, html_message):
        """
        MODIFIES: self.msg
        EFFECTS:  Attaches the given text to the email message.
        """
        part = MIMEText('html', "html")
        part.set_payload(html_message)
        self.msg.attach(part)

    # ======
    # PUBLIC
    # ======

    def attach_image(self, image_filename):
        """
        REQUIRES: image_filename is a file that exists in the current directory
        MODIFIES: self.msg
        EFFECTS:  Attaches the image with the given filename to self.msg.
        """
        path = os.path.join(DIRECTORY, image_filename)

        img = MIMEImage(open(path, 'rb').read(), _subtype="gif")
        img.add_header('Content-Disposition', 'attachment', filename=image_filename)
        self.msg.attach(img)

    def create_session_and_send(self):
        """
        REQUIRES: Valid connection to the Gmail SMTP server
        EFFECTS:  Sends the message to the given recipient.
        """
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

        session.ehlo()
        session.starttls()
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
    """RepeatedTimer repeats a function call at a given interval of time,
    until stopped.
    """
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        """Runs the function."""
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        """Starts the function calls."""
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        """Stops the function calls."""
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
        self.cute_picture_filename = ''
        self.extension = ''
        self.caption = ''

    def _retrieve_daily_picture(self):
        """
        REQUIRES: Connection to the internet is good.
        MODIFIES: The file cutePicture
        EFFECTS:  Saves the top imgur post from r/aww into the current
                  directory,
        """
        # URL of the top r/aww posts from Reddit
        aww_url = "http://www.reddit.com/r/aww/top.json"
        response = urllib.urlopen(aww_url)
        data = json.loads(response.read())

        # Retrieve picture link and reate filename
        imgur_link = data["data"]["children"][0]["data"]["url"]
        self.caption = "<h3>\"" + data["data"]["children"][0]["data"]["title"] + "\"</h3>"
        self.extension = imgur_link[imgur_link.rfind('.'):]
        self.cute_picture_filename = "cutePicture" + self.extension

        # Save the picture
        urllib.urlretrieve(imgur_link, filename=self.cute_picture_filename)

    def _remove_picture(self):
        """
        REQUIRES: cutePictureFilename is not empty
        MODIFIES: current directory
        EFFECTS:  Removes the imgur picture from the current directory.
        """
        if self.cute_picture_filename != '':
            os.remove(self.cute_picture_filename)

    def _attach_footer_text(self):
        """
        MODIFIES: msg
        EFFECTS:  Attaches the footer text in HTML.
        """
        adjectives = ["good", "great", "spectacular", "magnificent", "splendid", "dazzling",
                      "sensational", "remarkable", "outstanding", "memorable", "unforgettable"]
        footer = "Have a " + random.choice(adjectives) + " day!"
        footer_html = "<h3 style=\"font-weight: normal; font-style: oblique;\">" + footer + "</h3>"
        self._attach_message_text(footer_html)

    # ======
    # PUBLIC
    # ======

    def send_emails(self):
        """
        EFFECTS:  Downloads the picture, and sends an email to the given person.
        """
        self._retrieve_daily_picture()
        self.attach_image(self.cute_picture_filename)
        self._attach_message_text(self.caption)
        self._attach_footer_text()
        self.create_session_and_send()
        self._remove_picture()

        print "Sent emails!"

    def init_daily_emails(self):
        """
        MODIFIES: SMTP
        EFFECTS:  Initializes the daily email sending.
        """
        self.send_emails()
        RepeatedTimer(DAY, self.send_emails)

    def init_email_sender(self, email_sending_hour):
        """
        EFFECTS: Begins the daily email sending procedure, at the starting hour.
        """
        now = datetime.datetime.now()
        next_time_day = datetime.datetime.now().day

        # Ensures that emails are sent at proper time
        if now.hour >= email_sending_hour:
            next_time_day += 1

        next_time = datetime.datetime(now.year, now.month, next_time_day, EMAIL_SENDING_HOUR, 0, 0)
        time_interval = (next_time - now).total_seconds()
        threading.Timer(time_interval, self.init_daily_emails).start()

"""
======
main()
======
"""

def main():
    """Runs the Morning Puppies Sender."""
    morning_puppies_sender = MorningPuppiesSender(EMAIL_SUBJECT)
    morning_puppies_sender.init_email_sender(EMAIL_SENDING_HOUR)

if __name__ == '__main__':
    main()
    