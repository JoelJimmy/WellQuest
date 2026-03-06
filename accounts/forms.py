from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'your@email.com',
        'autocomplete': 'email',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Choose a username',
        'autocomplete': 'username',
    }))
    avatar = forms.ChoiceField(choices=[
        ('🧘', '🧘'), ('💪', '💪'), ('🌱', '🌱'), ('🦋', '🦋'),
        ('🌟', '🌟'), ('🔥', '🔥'), ('🌈', '🌈'), ('🐢', '🐢'),
    ], widget=forms.RadioSelect)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm your password',
    }))

    class Meta:
        model = User
        fields = ('email', 'username', 'avatar', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.avatar = self.cleaned_data['avatar']
        if commit:
            user.save()
        return user
    

class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'your@email.com',
        'autocomplete': 'email',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your password',
    }))