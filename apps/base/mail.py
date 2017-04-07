from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings


def send_mail(subject, text_message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None, html_message=None, reply_to=None, headers=None):
    """
    Override Django default send_mail to expose more parameters.

    Keep the interface compatible with django built-in one.
    """
    connection = connection or get_connection(
        username=auth_user,
        password=auth_password,
        fail_silently=fail_silently,
    )
    mail = EmailMultiAlternatives(
        subject, text_message, from_email, recipient_list,
        connection=connection, reply_to=reply_to, headers=headers
    )
    if html_message:
        mail.attach_alternative(html_message, 'text/html')

    return mail.send()


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
    from_email = settings.DEFAULT_FROM_EMAIL
    reply_to_email = settings.REPLY_TO_EMAIL
    return_path_email = settings.RETURN_PATH_EMAIL

    return send_mail(
        subject,
        text_message,
        return_path_email,
        recipient_list,
        html_message=html_message,
        reply_to=[reply_to_email],
        headers={'From': from_email}
    )
