from django import forms
from .models import ListingCategory, ForSaleSubCategory
from django.core.mail import send_mail
from django.conf import settings

class ListingForm(forms.Form):
    title = forms.CharField(max_length=200, label='Title')
    description = forms.CharField(widget=forms.Textarea, label='Description')
    price = forms.DecimalField(max_digits=10, decimal_places=2, label='Price')
    category = forms.ChoiceField(choices=ListingCategory.choices, label='Category')
    for_sale_subcategory = forms.ChoiceField(
        choices=ForSaleSubCategory.choices,
        label='For Sale Subcategory',
        required=False
    )

# class ImageForm(forms.Form):
#     # This field is not tied to a specific model field
#     images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Your Name')
    subject = forms.CharField(max_length=100, label='Subject')
    email = forms.EmailField(label='Your Email')
    message = forms.CharField(widget=forms.Textarea, label='Message')

    def send_email(self):
        subject = f'{self.cleaned_data["name"]} : {self.cleaned_data["subject"]} : {self.cleaned_data["email"]}'
        send_mail(
            subject,
            self.cleaned_data['message'],
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )