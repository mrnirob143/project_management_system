from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.hashers import make_password

from .models import User, Project, Task, Task_Comment


# ================= USER CREATE FORM =================
class UserCreateForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            'username', 'email', 'Role', 'Phone',
            'JoinDate', 'Dept', 'Post', 'password1', 'password2'
        ]

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'Role': forms.Select(attrs={'class': 'form-select'}),
            'Phone': forms.TextInput(attrs={'class': 'form-control'}),
            'JoinDate': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Dept': forms.TextInput(attrs={'class': 'form-control'}),
            'Post': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ❌ REMOVE default Django help text (THIS FIXES YOUR ISSUE)
        self.fields['username'].help_text = ""
        self.fields['password1'].help_text = ""
        self.fields['password2'].help_text = ""


# ================= USER UPDATE FORM =================
class UserUpdateForm(UserChangeForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'Role', 'Phone',
            'JoinDate', 'Dept', 'Post', 'password'
        ]

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'Role': forms.Select(attrs={'class': 'form-select'}),
            'Phone': forms.TextInput(attrs={'class': 'form-control'}),
            'JoinDate': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Dept': forms.TextInput(attrs={'class': 'form-control'}),
            'Post': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ❌ REMOVE help text
        self.fields['username'].help_text = ""

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            return make_password(password)
        return self.instance.password


# ================= PROJECT FORM =================
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['Name', 'Desc', 'Start', 'End', 'Status', 'Managed_By']

        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'Start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'End': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Status': forms.Select(attrs={'class': 'form-select'}),
            'Managed_By': forms.Select(attrs={'class': 'form-select'}),
        }


# ================= TASK FORM =================
class TaskForm(forms.ModelForm):

    Assigned_To = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(Role='EMPLOYEE'),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Task
        fields = [
            'Name', 'Start', 'End',
            'Status', 'P_ID', 'Assigned_To'
        ]

        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'End': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Status': forms.Select(attrs={'class': 'form-select'}),
            'P_ID': forms.Select(attrs={'class': 'form-select'}),
        }


# ================= COMMENT FORM =================
class CommentForm(forms.ModelForm):
    class Meta:
        model = Task_Comment
        fields = ['Text']

        widgets = {
            'Text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Add your comment...'
            }),
        }