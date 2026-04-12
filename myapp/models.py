from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
    )
    Phone = models.CharField(max_length=20, blank=True, null=True)
    Role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='EMPLOYEE')
    JoinDate = models.DateField(blank=True, null=True)
    Dept = models.CharField(max_length=100, blank=True, null=True)
    Post = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'user'

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.Role = 'ADMIN'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Project(models.Model):
    ID = models.BigAutoField(primary_key=True)
    Name = models.CharField(max_length=200)
    Desc = models.TextField()
    Start = models.DateField()
    End = models.DateField()
    Status = models.CharField(max_length=50)
    Created_By = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    Managed_By = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_projects')

    class Meta:
        db_table = 'project'

    def __str__(self):
        return self.Name


class Task(models.Model):
    ID = models.BigAutoField(primary_key=True)
    Name = models.CharField(max_length=200)
    Start = models.DateField()
    End = models.DateField()
    Status = models.CharField(max_length=50)
    P_ID = models.ForeignKey(Project, on_delete=models.CASCADE)

    # ✅ IMPORTANT FIX: better reverse access name
    Assigned_To = models.ManyToManyField(User, related_name='assigned_tasks', blank=True)

    class Meta:
        db_table = 'task'

    def __str__(self):
        return self.Name


class Task_Comment(models.Model):
    ID = models.BigAutoField(primary_key=True)
    Text = models.TextField()
    DateTime = models.DateTimeField(auto_now_add=True)
    T_ID = models.ForeignKey(Task, on_delete=models.CASCADE)
    U_ID = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'task_comment'

    def __str__(self):
        return f"Comment {self.ID}"


class Project_Assignment(models.Model):
    ID = models.BigAutoField(primary_key=True)
    P_ID = models.ForeignKey(Project, on_delete=models.CASCADE)
    U_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    Assigned_By = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_projects')
    Assigned_Date = models.DateField()

    class Meta:
        db_table = 'project_assignment'

    def __str__(self):
        return f"{self.P_ID} -> {self.U_ID}"