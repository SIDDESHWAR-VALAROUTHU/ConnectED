# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Project, Experience, Achievement ,CustomUser

User = get_user_model()



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'uid',
            'username',
            'email',
            'department',
            'batch',
            'role',
            'password1',
            'password2',
        ]


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'email',
            'department',
            'batch',
            'location',
            'current_designation',
            'company',
            'about',
            'contact_number',
            'linkedin',
            'github',
            'portfolio',
            'profile_pic',
            'cover_pic',
        ]

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "link"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Enter project title"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Brief project description"}),
            "link": forms.URLInput(attrs={"placeholder": "Project link (optional)"}),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ["title", "company", "start_date", "end_date", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Enter role title"}),
            "company": forms.TextInput(attrs={"placeholder": "Company name"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Work details or achievements"}),
        }


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ["title", "description", "date"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Enter achievement title"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Achievement description"}),
            "date": forms.DateInput(attrs={"type": "date"}),
 
 
 
        }



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['uid', 'email', 'department', 'batch', 'role', 'password1', 'password2']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
        }