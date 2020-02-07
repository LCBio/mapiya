from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.validators import MinLengthValidator
from mapserver.utils import random_string


class UserSession(models.Model):
    """M2M model binding users with sessions"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} - {self.session}'


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    UserSession.objects.get_or_create(
        user=user,
        session_id=request.session.session_key
    )


def random_id():
    # TODO: checking if new id is available
    return random_string(16)


class Identity(models.Model):
    """Wrapper model around user and session objects"""

    # TODO: manage.py command to run in cron which would remove unused identities or timer on anonymous identitites

    id = models.CharField(
        primary_key=True,
        max_length=16,
        default=random_id,
        validators=[MinLengthValidator(16)]
    )
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    session = models.OneToOneField(Session, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'identities'

    def __str__(self):
        return self.user.username if self.user else self.id
