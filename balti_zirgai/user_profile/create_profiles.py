from django.contrib.auth import get_user_model
from .models import Profile  

User = get_user_model()
unassigned = User.objects.filter(profile__isnull=True)
for user in unassigned:
    Profile.objects.create(user=user)