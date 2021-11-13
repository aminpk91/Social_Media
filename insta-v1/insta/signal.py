from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save

from .models import Profile
### create Profile for each user


@receiver(post_save, sender=User)
def create_profile(sender, instance, created=True, **kwargs):
    if created:
        try:
            Profile.objects.create(user=instance)
            print("signal create instance")
        except:
            print("SOME THING WRONG::::::: signal delete instance")
            instance.delete()

# @receiver(pre_save, sender=User)
# def build_profile_on_user_creation(sender, instance, **kwargs):
#     profile = Profile(user=instance)
#     profile.save(profile,**kwargs)
#     User.save()
@receiver(post_save, sender=Profile.fw)
def fw_fg(sender, instance, created=True, **kwargs):
    if created:
        try:
            Profile.objects.create(user=instance)
            print("signal create instance")
        except:
            print("SOME THING WRONG::::::: signal delete instance")
            instance.delete()
