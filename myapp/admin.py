from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Project, Task, Task_Comment, Project_Assignment

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    model = User
   
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Task_Comment)
admin.site.register(Project_Assignment)