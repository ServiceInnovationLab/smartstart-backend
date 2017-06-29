from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string


def build_email_message(subject, text_message, recipient_list, html_message=None):
    """
    Build a EmailMultiAlternatives object.

    To support the Return-Path email address, we have to build
    the email message in a unusual way:

    - use RETURN_PATH_EMAIL as from_email
    - use DEFAULT_FROM_EMAIL as From in header

    For more details, refer to:

        https://code.djangoproject.com/ticket/9214

    """
    mail = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=settings.RETURN_PATH_EMAIL,  # NOTE: this is unusual
        to=recipient_list,
        headers={'From': settings.DEFAULT_FROM_EMAIL}, # NOTE: this is unusual
        reply_to=[settings.REPLY_TO_EMAIL])
    if html_message:
        mail.attach_alternative(html_message, 'text/html')
    return mail


def ses_send_mail(subject, text_message, recipient_list, html_message=None):
    """
    Send email via Amazon SES and set the right sender/author/reply_to address.

    For email, except recipients, there are 3 addresses:

    1. from_email: display in `From` field
    2. reply_to_email: when user clicks reply
    3. return_path_email: if email was bounced, where should ESP return it to.

    Those 3 addresses can be all different.

    Refer to: https://code.djangoproject.com/ticket/9214
    """
    return build_email_message(subject, text_message, recipient_list, html_message=html_message).send()


def ses_send_templated_mail(template, recipient_list, context={}):
    """
    Render email template and send with ses.

    In the email template, subject and message are separated like this:

        This is email subject
        --END SUBJECT--
        This is your email body

    """
    subject, message = render_to_string(template, context).split('--END SUBJECT--')
    return ses_send_mail(subject.strip(), message, recipient_list)
