from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Project, Task, Task_Comment
from django.forms import CheckboxSelectMultiple
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div

User = get_user_model()


class UserCreateForm(forms.Form):

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    Role = forms.ChoiceField(
        choices=[
            ("", "Select Role"),
            ("ADMIN", "Admin"),
            ("MANAGER", "Manager"),
            ("EMPLOYEE", "Employee"),
        ],
        required=False
    )

    Phone = forms.CharField(required=False)

    JoinDate = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )

    Dept = forms.CharField(required=False)

    password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput()
    )

    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput()
    )

    # ✅ CRISPY PART
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_tag = True

        self.helper.layout = Layout(

            Div(
                Row(
                    Column("first_name", css_class="col-md-6"),
                    Column("last_name", css_class="col-md-6"),
                ),
                css_class="mb-2"
            ),

            "email",

            Div(
                Row(
                    Column("Role", css_class="col-md-6"),
                    Column("Phone", css_class="col-md-6"),
                ),
                css_class="mb-2"
            ),

            Div(
                Row(
                    Column("JoinDate", css_class="col-md-6"),
                    Column("Dept", css_class="col-md-6"),
                ),
                css_class="mb-2"
            ),

            Div(
                Row(
                    Column("password1", css_class="col-md-6"),
                    Column("password2", css_class="col-md-6"),
                ),
                css_class="mb-3"
            ),

            Submit(
                "submit",
                "Create User",
                css_class="btn btn-primary w-100"
            )
        )

    def clean(self):
        cleaned_data = super().clean()

        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        email = cleaned_data.get("email")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        phone = cleaned_data.get("Phone")

        errors = {}

        if not first_name:
            errors["first_name"] = "First name is required"

        if not last_name:
            errors["last_name"] = "Last name is required"

        if not email:
            errors["email"] = "Email is required"
        elif User.objects.filter(email=email).exists():
            errors["email"] = "Email already exists"

        if not phone:
            errors["Phone"] = "Phone number is required"
        if first_name and last_name:

         if User.objects.filter(first_name=first_name, last_name=last_name).exists():
            errors["first_name"] = "User with this name already exists"

        if not password1:
            errors["password1"] = "Password is required"

        if not password2:
            errors["password2"] = "Confirm password is required"

        if password1 and password2 and password1 != password2:
            errors["password2"] = "Passwords do not match"

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data



class UserUpdateForm(UserChangeForm):
    password = None  # ⭐ IMPORTANT (remove Django password field)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name',
            'email', 'Role', 'Phone',
            'JoinDate', 'Dept'
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'Role': forms.Select(attrs={'class': 'form-select'}),
            'Phone': forms.TextInput(attrs={'class': 'form-control'}),
            'JoinDate': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Dept': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # disable logic (safe)
        if request and request.user.Role != 'ADMIN':
            self.fields['first_name'].disabled = True
            self.fields['last_name'].disabled = True

        self.fields['email'].disabled = True

        # ⭐ CRISPY FIX
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_tag = True

        self.helper.layout = Layout(

            Div(
                Row(
                    Column("first_name", css_class="col-md-6"),
                    Column("last_name", css_class="col-md-6"),
                ),
                css_class="mb-2"
            ),

            "email",

            Div(
                Row(
                    Column("Role", css_class="col-md-6"),
                    Column("Phone", css_class="col-md-6"),
                ),
                css_class="mb-2"
            ),

            Div(
                Row(
                    Column("JoinDate", css_class="col-md-6"),
                    Column("Dept", css_class="col-md-6"),
                ),
                css_class="mb-3"
            ),

            Submit(
                "submit",
                "Update User",
                css_class="btn btn-primary w-100"
            )
        )

class UserSelfUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'Phone', 'Dept', 'Post']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'Phone': forms.TextInput(attrs={'class': 'form-control'}),
            'Dept': forms.TextInput(attrs={'class': 'form-control'}),
            'Post': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ================= CRISPY =================
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_tag = True

        self.helper.layout = Layout(

            Row(
                Column("first_name", css_class="col-md-6"),
                Column("last_name", css_class="col-md-6"),
            ),

            "email",

            Row(
                Column("Phone", css_class="col-md-6"),
                Column("Dept", css_class="col-md-6"),
            ),

            "Post",

            Submit(
                "submit",
                "Update Profile",
                css_class="btn btn-primary w-100 mt-3"
            )
        )

        # ================= READONLY FIELDS =================
        self.fields['first_name'].disabled = True
        self.fields['last_name'].disabled = True
        self.fields['email'].disabled = True
        self.fields['Post'].disabled = True

    def clean(self):
        cleaned_data = super().clean()

        # prevent override of disabled fields
        if self.instance:
            cleaned_data['first_name'] = self.instance.first_name
            cleaned_data['last_name'] = self.instance.last_name
            cleaned_data['email'] = self.instance.email
            cleaned_data['Post'] = self.instance.Post

        return cleaned_data
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'Name','Desc','Start', 'End', 'Status', 'Managed_By','Created_By','Members',
        ]
        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control'}),
            'Desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'Start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'End': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Status': forms.Select(attrs={'class': 'form-select'}),
            'Managed_By': forms.Select(attrs={'class': 'form-select'}),
            'Created_By': forms.Select(attrs={'class': 'form-select'}),
            'Members': CheckboxSelectMultiple(), }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Managed_By'].queryset = User.objects.filter(Role='MANAGER')
        self.fields['Members'].queryset = User.objects.filter(Role='EMPLOYEE')
        self.fields.pop('Members', None)
        if not (self.instance and self.instance.pk):
            self.fields.pop('Created_By', None)
        else:
            self.fields['Created_By'].disabled = True
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