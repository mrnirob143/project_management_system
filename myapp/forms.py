from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.hashers import make_password
from .models import User, Project, Task, Task_Comment


# ================= USER CREATE FORM =================
class UserCreateForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(),
        required=True
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'Role', 'Phone',
            'JoinDate', 'Dept', 'Post'
        ]

        widgets = {
            'JoinDate': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user


# ================= USER UPDATE FORM =================
class UserUpdateForm(UserChangeForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(),
        required=False
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'Role', 'Phone',
            'JoinDate', 'Dept', 'Post', 'password'
        ]

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
        fields = [
            'Name', 'Start', 'End',
            'Status', 'P_ID', 'Assigned_To'
        ]

        widgets = {
            'Start': forms.DateInput(attrs={'type': 'date'}),
            'End': forms.DateInput(attrs={'type': 'date'}),
            'Assigned_To': forms.SelectMultiple(),
        }


# ================= COMMENT FORM =================
class CommentForm(forms.ModelForm):
    class Meta:
        model = Task_Comment
        fields = ['Text']

        widgets = {
            'Text': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Add your comment...'
            }),
        }