from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User, Project, Task, Task_Comment
from .forms import UserUpdateForm, ProjectForm, TaskForm, CommentForm

# ================= LOGIN =================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, "All fields are required!")
            return redirect('login')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Invalid username or password")
    return render(request, 'login.html')


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect('login')


# ================= DASHBOARD =================
@login_required
def dashboard(request):
    user = request.user

    if user.Role == 'ADMIN' or user.is_superuser:
        total_users = User.objects.count()
        total_projects = Project.objects.count()
        total_tasks = Task.objects.count()
    elif user.Role == 'MANAGER':
        total_users = None
        total_projects = Project.objects.filter(
            Q(Created_By=user) | Q(Created_By__Role='ADMIN')
        ).count()
        total_tasks = Task.objects.filter(
            P_ID__Created_By__in=User.objects.filter(Q(id=user.id) | Q(Role='ADMIN'))
        ).count()
    else:  
        total_users = None
        total_projects = Task.objects.filter(Assigned_To=user).count()
        total_tasks = total_projects

    context = {
        'user_role': user.Role,
        'total_users': total_users,
        'total_projects': total_projects,
        'total_tasks': total_tasks,
    }
    return render(request, 'dashboard.html', context)


# ================= USER CRUD =================
@login_required
def user_list(request):
    if request.user.Role != 'ADMIN':
        return redirect('dashboard')
    users = User.objects.all()
    return render(request, 'users.html', {'users': users, 'user_role': request.user.Role})


@login_required
def create_user(request):
    if request.user.Role != 'ADMIN':
        return redirect('dashboard')
    form = UserUpdateForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "User created successfully!")
        return redirect('user_list')
    return render(request, 'user_form.html', {'form': form, 'user_role': request.user.Role})


@login_required
def edit_user(request, id):
    if request.user.Role != 'ADMIN':
        return redirect('dashboard')
    user_obj = get_object_or_404(User, id=id)
    form = UserUpdateForm(request.POST or None, instance=user_obj)
    if form.is_valid():
        form.save()
        messages.success(request, "User updated successfully!")
        return redirect('user_list')
    return render(request, 'user_form.html', {'form': form, 'user_role': request.user.Role})


@login_required
def delete_user(request, id):
    if request.user.Role != 'ADMIN':
        return redirect('dashboard')
    user_obj = get_object_or_404(User, id=id)
    if user_obj != request.user:
        user_obj.delete()
        messages.success(request, "User deleted successfully!")
    return redirect('user_list')


# ================= PROJECT CRUD =================
@login_required
def project_list(request):
    if request.user.Role == 'ADMIN':
        projects = Project.objects.all()
    elif request.user.Role == 'MANAGER':
        projects = Project.objects.filter(Q(Created_By=request.user) | Q(Created_By__Role='ADMIN'))
    else:
        projects = Project.objects.none()
    return render(request, 'project_list.html', {'projects': projects, 'user_role': request.user.Role})


@login_required
def project_add(request):
    if request.user.Role not in ['ADMIN', 'MANAGER']:
        return redirect('dashboard')
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.Created_By = request.user
        obj.save()
        messages.success(request, "Project added successfully!")
        return redirect('project_list')
    return render(request, 'project_form.html', {'form': form, 'user_role': request.user.Role})


@login_required
def project_edit(request, id):
    project = get_object_or_404(Project, ID=id)
    if request.user.Role not in ['ADMIN', 'MANAGER'] or (request.user.Role == 'MANAGER' and project.Created_By != request.user and project.Created_By.Role != 'ADMIN'):
        return redirect('dashboard')
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        messages.success(request, "Project updated successfully!")
        return redirect('project_list')
    return render(request, 'project_form.html', {'form': form, 'user_role': request.user.Role})


@login_required
def project_delete(request, id):
    project = get_object_or_404(Project, ID=id)
    if request.user.Role not in ['ADMIN', 'MANAGER'] or (request.user.Role == 'MANAGER' and project.Created_By != request.user and project.Created_By.Role != 'ADMIN'):
        return redirect('dashboard')
    project.delete()
    messages.success(request, "Project deleted successfully!")
    return redirect('project_list')


# ================= TASK CRUD =================
@login_required
def task_list(request):
    if request.user.Role == 'ADMIN':
        tasks = Task.objects.all()
    elif request.user.Role == 'MANAGER':
        tasks = Task.objects.filter(
            P_ID__Created_By__in=User.objects.filter(Q(id=request.user.id) | Q(Role='ADMIN'))
        )
    else:
        tasks = Task.objects.filter(Assigned_To=request.user)
    return render(request, 'task_list.html', {'tasks': tasks, 'user_role': request.user.Role})


@login_required
def task_add(request):
    if request.user.Role not in ['ADMIN', 'MANAGER']:
        return redirect('dashboard')
    form = TaskForm(request.POST or None)
    if request.user.Role == 'ADMIN':
        form.fields['P_ID'].queryset = Project.objects.all()
    elif request.user.Role == 'MANAGER':
        form.fields['P_ID'].queryset = Project.objects.filter(Q(Created_By=request.user) | Q(Created_By__Role='ADMIN'))
    form.fields['Assigned_To'].queryset = User.objects.filter(Role='EMPLOYEE')
    if form.is_valid():
        form.save()
        messages.success(request, "Task added successfully!")
        return redirect('task_list')
    return render(request, 'task_form.html', {'form': form, 'user_role': request.user.Role})


@login_required
def task_edit(request, id):
    task = get_object_or_404(Task, ID=id)
    if request.user.Role not in ['ADMIN', 'MANAGER'] or (request.user.Role == 'MANAGER' and task.P_ID.Created_By != request.user and task.P_ID.Created_By.Role != 'ADMIN'):
        return redirect('dashboard')
    form = TaskForm(request.POST or None, instance=task)
    if request.user.Role == 'ADMIN':
        form.fields['P_ID'].queryset = Project.objects.all()
    elif request.user.Role == 'MANAGER':
        form.fields['P_ID'].queryset = Project.objects.filter(Q(Created_By=request.user) | Q(Created_By__Role='ADMIN'))
    form.fields['Assigned_To'].queryset = User.objects.filter(Role='EMPLOYEE')
    if form.is_valid():
        form.save()
        messages.success(request, "Task updated successfully!")
        return redirect('task_list')
    return render(request, 'task_form.html', {'form': form, 'user_role': request.user.Role})


@login_required
def task_delete(request, id):
    task = get_object_or_404(Task, ID=id)
    if request.user.Role not in ['ADMIN', 'MANAGER'] or (request.user.Role == 'MANAGER' and task.P_ID.Created_By != request.user and task.P_ID.Created_By.Role != 'ADMIN'):
        return redirect('dashboard')
    task.delete()
    messages.success(request, "Task deleted successfully!")
    return redirect('task_list')


# ================= COMMENTS =================
@login_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, ID=task_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.T_ID = task
        obj.U_ID = request.user
        obj.save()
        messages.success(request, "Comment added!")
        return redirect('task_list')
    return render(request, 'comment_form.html', {'form': form, 'user_role': request.user.Role})