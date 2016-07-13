from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _

from .models import *


class CustomUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    username = forms.RegexField(label=_("Username"), max_length=30,
                                regex=r'^[\w.@+-]+$',
                                help_text=_("Required. 30 characters or fewer. Letters, digits and "
                                            "@/./+/-/_ only."),
                                error_messages={
                                    'invalid': _("This value may contain only letters, numbers and "
                                                 "@/./+/-/_ characters.")})

    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    sex = forms.ChoiceField(choices=(('Male','Male'),('Female','Female')))

    user_type = forms.ChoiceField(choices=(('Driver', 'Driver'), ('Passenger', 'Passenger')))


    class Meta:
        # Point to our CustomUser here instead of default `User`
        model = CustomUser
        fields = ('full_name', 'short_name', 'email', 'sex','phone_number','user_type', 'address','username')

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            # Refer to our CustomUser here instead of default `User`
            CustomUser._default_manager.get(username=username)
        except CustomUser.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        # Make sure we pass back in our CustomUserCreationForm and not the
        # default `UserCreationForm`
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    username = forms.RegexField(
        label=_("Username"), max_length=30, regex=r"^[\w.@+-]+$",
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                    "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_("Raw passwords are not stored, so there is no way to see "
                                                     "this user's password, but you can change the password "
                                                     "using <a href=\"password/\">this form</a>."))

    class Meta:
        # Point to our CustomUser here instead of default `User`

        model = CustomUser
        fields = ('full_name', 'short_name', 'email', 'sex','phone_number','user_type', 'address','username','password')


    def __init__(self, *args, **kwargs):
        # Make sure we pass back in our CustomUserChangeForm and not the
        # default `UserChangeForm`
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class VehicleAddForm(forms.ModelForm):
    type = forms.ChoiceField(choices=(('private', 'private'), ('hired', 'hired')))

    category = forms.ChoiceField(choices=(('Car', 'Car'), ('Bus', 'Bus'),  ('Coaster', 'Coaster'),  ('Truck', 'Truck')))

    class Meta:
        model = Vehicle
        fields = ['year', 'make', 'model', 'seats', 'type', 'category']


class VehicleShare(forms.ModelForm):

    date = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker','required':True,'readonly':True,'placeholder':'mm/dd/yyyy'}))
    start_time = forms.TimeField(widget=forms.TextInput(attrs={'type':'time','required':True}))
    arrival_time = forms.TimeField(widget=forms.TextInput(attrs={'type':'time','required':True}))
    arrival_time.error_messages = 'Nodndhhj'

    start = forms.CharField(widget=forms.TextInput(attrs={'required':True}))
    dest = forms.CharField(widget=forms.TextInput(attrs={'required':True}))


    class Meta:
        model = VehicleSharing
        fields = ['start', 'dest', 'cost', 'date', 'start_time', 'arrival_time', 'no_pass', 'sex']

    def __init__(self, *args, **kwargs):
        super(VehicleShare, self).__init__(*args, **kwargs)


class RequestForm(forms.ModelForm):

    class Meta:
        model = Request
        fields = ['pick', 'dest', 'bearable']



















