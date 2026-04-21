from django.db import models
from django.contrib.auth.models import AbstractUser


# ================= USER =================
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

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.Role = 'ADMIN'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


# ================= PROJECT =================
class Project(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    )

    ID = models.BigAutoField(primary_key=True)
    Name = models.CharField(max_length=200)
    Desc = models.TextField()
    Start = models.DateField()
    End = models.DateField()

    Status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    Created_By = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_projects'
    )

    Managed_By = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='managed_projects'
    )

    Members = models.ManyToManyField(
        User,
        related_name='projects',
        blank=True
    )

    def __str__(self):
        return self.Name


# ================= TASK =================
class Task(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
    )

    ID = models.BigAutoField(primary_key=True)
    Name = models.CharField(max_length=200)

    Start = models.DateField(null=True, blank=True)
    End = models.DateField(null=True, blank=True)

    Status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    P_ID = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    Assigned_To = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )

    def __str__(self):
        return self.Name

# ================= COMMENT =================
class Task_Comment(models.Model):
    Text = models.TextField()
    DateTime = models.DateTimeField(auto_now_add=True)

    T_ID = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    U_ID = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment {self.ID}"