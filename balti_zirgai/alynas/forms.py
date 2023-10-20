from django import forms
from . import models


class BeerReviewForm(forms.ModelForm):
    class Meta:
        model = models.BeerReview
        fields = ("content", "beer", "reviewer")
        widgets = {
            "beer": forms.HiddenInput(),
            "reviewer": forms.HiddenInput(),
        }