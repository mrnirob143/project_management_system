from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User, Project, Task, Task_Comment, Project_Assignment
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
        recent_tasks = Task.objects.all().order_by('-ID')[:5]

    elif user.Role == 'MANAGER':
        total_users = None

        total_projects = Project.objects.filter(
            Q(Created_By=user) | Q(Created_By__Role='ADMIN')
        ).count()

        total_tasks = Task.objects.filter(
            P_ID__Created_By__in=User.objects.filter(
                Q(id=user.id) | Q(Role='ADMIN')
            )
        ).count()

        recent_tasks = Task.objects.filter(
            P_ID__Created_By__in=User.objects.filter(
                Q(id=user.id) | Q(Role='ADMIN')
            )
        ).order_by('-ID')[:5]

    else:
        employee_tasks = Task.objects.filter(Assigned_To=user)

        total_users = None
        total_projects = Project_Assignment.objects.filter(U_ID=user).count()

        total_tasks = employee_tasks.count()   

        recent_tasks = employee_tasks.order_by('-ID')[:5]

    return render(request, 'dashboard.html', {
        'user_role': user.Role,
        'total_users': total_users,
        'total_projects': total_projects,
        'total_tasks': total_tasks,
        'recent_tasks': recent_tasks,
    })
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

@login_required
def user_detail(request, id):
    if request.user.Role != 'ADMIN':
        return redirect('dashboard')

    user_obj = get_object_or_404(User, id=id)
    return render(request, 'user_detail.html', {
        'user_obj': user_obj,
        'user_role': request.user.Role
    })


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

@login_required
def project_detail(request, id):
    project = get_object_or_404(Project, ID=id)

    tasks = Task.objects.filter(P_ID=project)
    assignments = Project_Assignment.objects.filter(P_ID=project)

    employees = [a.U_ID for a in assignments]

    return render(request, 'project_detail.html', {
        'project': project,
        'tasks': tasks,
        'employees': employees,
        'user_role': request.user.Role
    })


# ================= TASK CRUD =================
@login_required
def task_list(request):
    user = request.user

    if user.Role == 'ADMIN':
        tasks = Task.objects.all()

    elif user.Role == 'MANAGER':
        tasks = Task.objects.filter(
            P_ID__Created_By__in=User.objects.filter(
                Q(id=user.id) | Q(Role='ADMIN')
            )
        )

    else:
        tasks = Task.objects.filter(Assigned_To=user)

    return render(request, 'task_list.html', {
        'tasks': tasks,
        'user_role': user.Role
    })
@login_required
def task_add(request):
    if request.user.Role not in ['ADMIN', 'MANAGER']:
        return redirect('dashboard')

    project_id = request.GET.get('project_id')

    form = TaskForm(request.POST or None)

    form.fields['P_ID'].queryset = Project.objects.all()
    form.fields['Assigned_To'].queryset = User.objects.filter(Role='EMPLOYEE')

    if form.is_valid():
        task = form.save(commit=False)

        if project_id:
            project = get_object_or_404(Project, ID=project_id)
            task.P_ID = project

        task.save()
        form.save_m2m()

        if task.P_ID:
            return redirect('project_detail', id=task.P_ID.ID)

        return redirect('task_list')

    return render(request, 'task_form.html', {
        'form': form,
        'user_role': request.user.Role
    })
@login_required
def task_edit(request, id):
    task = get_object_or_404(Task, ID=id)

    if request.user.Role not in ['ADMIN', 'MANAGER']:
        return redirect('dashboard')

    form = TaskForm(request.POST or None, instance=task)

    form.fields['P_ID'].queryset = Project.objects.all()
    form.fields['Assigned_To'].queryset = User.objects.filter(Role='EMPLOYEE')

    if form.is_valid():
        task = form.save(commit=False)
        task.save()

        form.save_m2m()

        messages.success(request, "Task updated successfully!")
        return redirect('task_list')

    return render(request, 'task_form.html', {'form': form})
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


# ================= ADD MEMBER TO PROJECT =================
@login_required
def add_member_to_project(request, project_id):
    project = get_object_or_404(Project, ID=project_id)

    if request.user.Role not in ['ADMIN', 'MANAGER']:
        messages.error(request, "You are not allowed to access this page.")
        return redirect('dashboard')

    if request.user.Role == 'MANAGER':
        if project.Created_By != request.user and project.Created_By.Role != 'ADMIN':
            messages.error(request, "Not allowed for this project.")
            return redirect('dashboard')

    if request.method == 'POST':
        user_ids = request.POST.getlist('user_ids')

        for user_id in user_ids:
            user = get_object_or_404(User, id=user_id)

            if not Project_Assignment.objects.filter(P_ID=project, U_ID=user).exists():
                Project_Assignment.objects.create(
                    P_ID=project,
                    U_ID=user,
                    Assigned_By=request.user,
                    Assigned_Date=request.user.JoinDate
                )

        messages.success(request, "Members added successfully!")
        return redirect('project_detail', id=project.ID)

    unassigned_users = User.objects.exclude(
        id__in=Project_Assignment.objects.filter(P_ID=project).values('U_ID')
    ).filter(Role='EMPLOYEE')

    return render(request, 'add_member_to_project.html', {
        'project': project,
        'unassigned_users': unassigned_users,
        'user_role': request.user.Role
    })