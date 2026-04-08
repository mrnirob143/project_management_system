from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.hashers import make_password
from .models import User, Project, Task, Task_Comment

# ================= USER FORMS =================

class UserCreateForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(),
        required=True,
        help_text="Enter a password for the new user."
    )
  
    class Meta:
        model = User
        fields = ['username', 'email', 'Role', 'Phone', 'JoinDate', 'Dept', 'Post', 'password1',]
        widgets = {
            'JoinDate': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            return make_password(password)
        return None

class UserUpdateForm(UserChangeForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(),
        required=False,  
        help_text="Enter a new password/old."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'Role', 'Phone', 'JoinDate', 'Dept', 'Post', 'password']
        widgets = {
            'JoinDate': forms.DateInput(attrs={'type': 'date'}),
        }

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
            'Start': forms.DateInput(attrs={'type': 'date'}),
            'End': forms.DateInput(attrs={'type': 'date'}),
            'Desc': forms.Textarea(attrs={'rows': 3}),
        }


# ================= TASK FORM =================
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['Name', 'Start', 'End', 'Status', 'P_ID', 'Assigned_To']
        widgets = {
            'Start': forms.DateInput(attrs={'type': 'date'}),
            'End': forms.DateInput(attrs={'type': 'date'}),
        }


# ================= COMMENT FORM =================
class CommentForm(forms.ModelForm):
    class Meta:
        model = Task_Comment
        fields = ['Text']
        widgets = {
            'Text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add your comment...'}),
        }