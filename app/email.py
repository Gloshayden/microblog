from threading import Thread  # Import Thread for asynchronous email sending
from flask import current_app  # Import current_app to access Flask application context
from flask_mail import Message  # Import Message for email creation
from app import mail  # Import mail to send the email
from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    # Send email asynchronously within application context
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    # Create and send an email using a separate thread for asynchronous delivery
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()