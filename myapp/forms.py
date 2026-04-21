from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Project, Task, Task_Comment
from django.forms import CheckboxSelectMultiple


# ================= USER CREATE =================
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
class UserUpdateForm(UserChangeForm):

    class Meta:
        model = User
        fields = [
            'username', 'email', 'Role', 'Phone',
            'JoinDate', 'Dept', 'Post'
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
class UserSelfUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'Phone', 'Dept', 'Post']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'Phone': forms.TextInput(attrs={'class': 'form-control'}),
            'Dept': forms.TextInput(attrs={'class': 'form-control'}),
            'Post': forms.TextInput(attrs={'class': 'form-control'}),
        }
# ================= PROJECT=================
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
            'Members': CheckboxSelectMultiple(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import User
        self.fields['Created_By'].queryset = User.objects.filter(Role='ADMIN')
        self.fields['Managed_By'].queryset = User.objects.filter(Role='MANAGER')
        self.fields['Members'].queryset = User.objects.filter(Role='EMPLOYEE')
        if self.instance and self.instance.pk:
            self.fields['Created_By'].widget = forms.HiddenInput()
# ================= TASK =================
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['Name', 'Start', 'Status', 'Assigned_To']
        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Status': forms.Select(attrs={'class': 'form-select'}),
            'Assigned_To': forms.Select(attrs={'class': 'form-select'}),
        }
# ================= COMMENT =================
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