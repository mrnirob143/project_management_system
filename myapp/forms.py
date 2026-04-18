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
            'JoinDate', 'Dept', 'Post',
            'password1', 'password2'
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
        self.fields['username'].help_text = ""
        self.fields['password1'].help_text = ""
        self.fields['password2'].help_text = ""


# ================= USER UPDATE FORM =================
class UserUpdateForm(UserChangeForm):

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
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

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return make_password(password) if password else self.initial.get('password', '')


# ================= PROJECT FORM (FIXED RESPONSIVE) =================
class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = '__all__'

        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'Start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'End': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Status': forms.Select(attrs={'class': 'form-select'}),
            'Created_By': forms.Select(attrs={'class': 'form-select'}),
            'Managed_By': forms.Select(attrs={'class': 'form-select'}),

            # ✅ FIXED (IMPORTANT FOR RESPONSIVE)
            'Members': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['Created_By'].queryset = User.objects.filter(Role='ADMIN')
        self.fields['Managed_By'].queryset = User.objects.filter(Role='MANAGER')
        self.fields['Members'].queryset = User.objects.filter(Role='EMPLOYEE')

        if self.instance and self.instance.pk:
            self.fields['Created_By'].widget = forms.HiddenInput()


# ================= TASK FORM =================
class TaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # MANAGER restriction
        if self.user and self.user.Role == 'MANAGER':
            self.fields.pop('P_ID', None)
            self.fields.pop('End', None)

    class Meta:
        model = Task
        fields = '__all__'

        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'End': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Status': forms.Select(attrs={'class': 'form-select'}),
            'P_ID': forms.Select(attrs={'class': 'form-select'}),
            'Assigned_To': forms.Select(attrs={'class': 'form-select'}),
        }


# ================= COMMENT FORM =================
class CommentForm(forms.ModelForm):

    class Meta:
        model = Task_Comment
        fields = ['Text']

        widgets = {
            'Text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
        }