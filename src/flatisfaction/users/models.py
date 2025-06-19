from django.db import models
from django.contrib.auth.models import User

def user_avatar_directory_path(instance, filename):
    return f"user_avatars/user_{instance.user.id}/{filename}"

# Create your models here.
class UserProfile(models.Model):

    avatar = models.ImageField(
        upload_to=user_avatar_directory_path,
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
    )

