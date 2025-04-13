from django import forms
from captcha.fields import CaptchaField

class SimpleCaptchaForm(forms.Form):
    captcha = CaptchaField()