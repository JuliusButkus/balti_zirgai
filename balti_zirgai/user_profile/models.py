from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from PIL import Image


User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        verbose_name=_("user"), 
        on_delete=models.CASCADE,
        related_name="profile",
        null=True, blank=True
    )
    photo = models.ImageField(("photo"), upload_to="user/profile/img/", null=True, blank=True)

    class Meta:
        verbose_name =_("profile")
        verbose_name_plural =_("profiles")

    def save(self, args, **kwargs) -> None:
        super().save(args, **kwargs)
        if self.photo:
            photo = Image.open(self.photo.path)
            if photo.height > 300 or photo.width > 500:
                resized_dimensions = (800, 300)
                photo.thumbnail(resized_dimensions)
                photo.save(self.photo.path)

    def str(self):
        return f"{self.user}"

    def get_absolute_url(self):
        return reverse("profile_detail", kwargs={"pk": self.pk})


