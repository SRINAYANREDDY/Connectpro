from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Education, Skill, Project


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['email', 'username', 'full_name', 'password', 'password2']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'username', 'bio', 'headline', 'location', 'website', 'avatar', 'cover_photo', 'is_private']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['school', 'degree', 'field_of_study', 'start_year', 'end_year', 'description']
        widgets = {f: forms.TextInput(attrs={'class': 'form-control'}) for f in ['school', 'degree', 'field_of_study']}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_year'].widget = forms.NumberInput(attrs={'class': 'form-control'})
        self.fields['end_year'].widget = forms.NumberInput(attrs={'class': 'form-control'})
        self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 2})


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Add a skill...'})}


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'url', 'image', 'technologies']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'technologies': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, Django, React'}),
        }
