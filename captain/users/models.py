from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver


# User class extensions
def user_unicode(self):
    """Change user string representation to use the user's email address."""
    return self.email
User.add_to_class('__unicode__', user_unicode)


@property
def user_display_name(self):
    """Return this user's display name, or 'Anonymouse' if they don't have a profile."""
    try:
        return self.profile.display_name
    except UserProfile.DoesNotExist:
        return None
User.add_to_class('display_name', user_display_name)


class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name='profile')
    display_name = models.CharField(max_length=256, default='Anonymous')


@receiver(models.signals.post_save, sender=User)
def create_user_profile(sender, **kwargs):
    """Create a user profile as soon as a user is created."""
    if kwargs['created']:
        user = kwargs['instance']
        UserProfile.objects.create(user=user)
