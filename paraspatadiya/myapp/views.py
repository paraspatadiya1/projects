
import json
import logging

from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import ContactMessage


logger = logging.getLogger(__name__)


def index(request):
    return render(request, "index.html")


@require_POST
def contact_submit(request):

    # 1. Read contact form data
    try:
        data = json.loads(request.body.decode("utf-8"))

    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {
                "status": "error",
                "message": "Invalid request. Please try again.",
            },
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {
                "status": "error",
                "message": "Invalid request data.",
            },
            status=400,
        )

    # 2. Get form fields
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()

    # 3. Validate required fields
    if not all([name, email, subject, message]):
        return JsonResponse(
            {
                "status": "error",
                "message": "Please fill in all fields.",
            },
            status=400,
        )

    try:
        validate_email(email)

    except ValidationError:
        return JsonResponse(
            {
                "status": "error",
                "message": "Please enter a valid email address.",
            },
            status=400,
        )

    # 4. Save message in database
    contact = ContactMessage.objects.create(
        name=name,
        email=email,
        subject=subject,
        message=message,
    )

    # 5. Prepare email notification for Paras
    owner_subject = f"New Portfolio Message: {subject}"

    owner_message = f"""
Hello Paras,

You have received a new message through your portfolio website!

========================================
CONTACT DETAILS
========================================

Name: {name}
Email: {email}
Subject: {subject}
Message ID: #{contact.id}

========================================
MESSAGE
========================================

{message}

========================================

You can directly reply to this email to contact {name}.

This message was submitted through your portfolio contact form.

Best regards,
Your Portfolio Website
"""

    # 6. Prepare thank-you email for visitor
    visitor_subject = "Thank You for Contacting Me!"

    visitor_message = f"""
Hello {name},

Thank you for visiting my portfolio and taking the time
to contact me!

I have successfully received your message.

Here is a copy of your submitted message:

----------------------------------------
Subject: {subject}

Message:
{message}
----------------------------------------

I appreciate your interest and will review your message.

I'll get back to you as soon as possible.

Thank you once again for reaching out!

Best regards,

Paras Patadiya
Python Backend Developer
Portfolio Website
"""

    # 7. Send both emails
    try:

        # Email 1: Notification to Paras
        owner_email = EmailMessage(
            subject=owner_subject,
            body=owner_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=["paraspatadiya6@gmail.com"],
            reply_to=[email],
        )

        owner_email.send(fail_silently=False)

        # Email 2: Thank-you email to visitor
        send_mail(
            subject=visitor_subject,
            message=visitor_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

    except Exception:
        logger.exception(
            "Email delivery failed for contact message ID %s",
            contact.id,
        )

        return JsonResponse(
            {
                "status": "saved",
                "message": (
                    "Your message has been saved, "
                    "but email delivery failed. Please try again later."
                ),
            },
            status=201,
        )

    # 8. Return success response
    return JsonResponse(
        {
            "status": "ok",
            "message": (
                "Thank you for contacting me! "
                "A confirmation email has been sent to your email address. "
                "I'll get back to you soon."
            ),
        },
        status=201,
    )
