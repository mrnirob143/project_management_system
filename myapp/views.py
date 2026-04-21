from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User, Project, Task, Task_Comment
from .forms import UserUpdateForm, ProjectForm, TaskForm, CommentForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from .forms import UserCreateForm, UserUpdateForm, UserSelfUpdateForm

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

        # ✅ IMPORTANT: match EXACT model values
        done_tasks = Task.objects.filter(Status='Done').count()
        in_progress_tasks = Task.objects.filter(Status='In Progress').count()
        pending_tasks = Task.objects.filter(Status='Pending').count()

        recent_tasks = Task.objects.all().order_by('-ID')[:5]

    elif user.Role == 'MANAGER':

        projects = Project.objects.filter(
            Q(Created_By=user) | Q(Created_By__Role='ADMIN')
        )

        total_users = None
        total_projects = projects.count()
        total_tasks = Task.objects.filter(P_ID__in=projects).count()

        recent_tasks = Task.objects.filter(
            P_ID__in=projects
        ).order_by('-ID')[:5]

        done_tasks = in_progress_tasks = pending_tasks = None

    else:

        employee_tasks = Task.objects.filter(Assigned_To=user)

        total_users = None
        total_projects = Project.objects.filter(Members=user).count()
        total_tasks = employee_tasks.count()

        recent_tasks = employee_tasks.order_by('-ID')[:5]

        done_tasks = in_progress_tasks = pending_tasks = None

    return render(request, 'dashboard.html', {
        'user_role': user.Role,
        'total_users': total_users,
        'total_projects': total_projects,
        'total_tasks': total_tasks,
        'recent_tasks': recent_tasks,

        'done_tasks': done_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_tasks': pending_tasks,
    })
# ================= USER=================
@login_required
def user_list(request):
    if request.user.Role != 'ADMIN':
        return redirect('dashboard')
    users = User.objects.all()
    return render(request, 'users.html', {
        'users': users,
        'user_role': request.user.Role
    })
@login_required
def create_user(request):
    if request.user.Role != 'ADMIN':
        return redirect('dashboard')
    form = UserCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "User created successfully!")
        return redirect('user_list')
    return render(request, 'user_form.html', {
        'form': form,
        'user_role': request.user.Role
    })
@login_required
def edit_user(request, id):
    user_obj = get_object_or_404(User, id=id)
    if request.user.Role != 'ADMIN' and request.user.id != user_obj.id:
        return redirect('dashboard')
    if request.user.Role == 'ADMIN':
        form = UserUpdateForm(request.POST or None, instance=user_obj)
        if request.user.id != user_obj.id or request.user.id == user_obj.id:
            form.fields.pop('password', None)
    else:
        form = UserSelfUpdateForm(request.POST or None, instance=user_obj)
    if form.is_valid():
        user = form.save()
        if request.user.id == user.id:
            update_session_auth_hash(request, user)
        messages.success(request, "Profile updated successfully!")
        return redirect('user_detail', id=user_obj.id)
    return render(request, 'user_form.html', {
        'form': form,
        'user_role': request.user.Role
    })
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
    user_obj = get_object_or_404(User, id=id)
    if request.user.Role != 'ADMIN' and request.user.id != user_obj.id:
        return redirect('dashboard')
    show_reset_button = not (request.user.Role == 'ADMIN' and request.user.id != user_obj.id)
    return render(request, 'user_detail.html', {
        'user_obj': user_obj,
        'user_role': request.user.Role,
        'show_reset_button': show_reset_button
    })
# ================= PROJECT =================
@login_required
def project_list(request):
    if request.user.Role == 'ADMIN':
        projects = Project.objects.all()
    elif request.user.Role == 'MANAGER':
        projects = Project.objects.filter(
            Q(Created_By=request.user) | Q(Created_By__Role='ADMIN')
        )
    else:
        projects = Project.objects.filter(Members=request.user)
    return render(request, 'project_list.html', {
        'projects': projects,
        'user_role': request.user.Role
    })
@login_required
def project_add(request):
    if request.user.Role not in ['ADMIN', 'MANAGER']:
        return redirect('dashboard')
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.Created_By = request.user
        obj.save()
        form.save_m2m()
        obj.Members.add(request.user)
        messages.success(request, "Project added successfully!")
        return redirect('project_list')
    return render(request, 'project_form.html', {
        'form': form,
        'user_role': request.user.Role
    })
@login_required
def project_edit(request, id):
    project = get_object_or_404(Project, ID=id)
    if request.user.Role not in ['ADMIN', 'MANAGER']:
        return redirect('dashboard')
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        messages.success(request, "Project updated successfully!")
        return redirect('project_list')
    return render(request, 'project_form.html', {
        'form': form,
        'user_role': request.user.Role
    })
@login_required
def project_delete(request, id):
    project = get_object_or_404(Project, ID=id)

    if request.user.Role not in ['ADMIN', 'MANAGER']:
        return redirect('dashboard')
    Task.objects.filter(P_ID=project).delete()
    project.delete()
    messages.success(request, "Project and all related tasks deleted successfully!")
    return redirect('project_list')
@login_required
def project_detail(request, id):
    project = get_object_or_404(Project, ID=id)
    if request.user.Role == 'EMPLOYEE':
        if request.user not in project.Members.all():
            return redirect('dashboard')
    tasks = Task.objects.filter(P_ID=project)
    employees = User.objects.filter(Role='EMPLOYEE')
    members = project.Members.all()
    return render(request, 'project_detail.html', {
        'project': project,
        'tasks': tasks,
        'employees': employees,
        'members': members,   
        'user_role': request.user.Role
    })
# ================= TASK=================
@login_required
def task_list(request):
    user = request.user
    if user.Role == 'ADMIN':
        tasks = Task.objects.all()
    elif user.Role == 'MANAGER':
        tasks = Task.objects.filter(
            P_ID__Created_By__in=User.objects.filter(
                Q(id=user.id) | Q(Role='ADMIN')
            ))
    else:
     tasks = Task.objects.filter(Assigned_To=user)
    return render(request, 'task_list.html', {
        'tasks': tasks,
        'user_role': user.Role
    })
@login_required
def task_add(request):
    if request.user.Role != 'MANAGER':
        return redirect('dashboard')
    project_id = request.GET.get('project_id')
    if not project_id:
        return redirect('dashboard')
    project = get_object_or_404(Project, ID=project_id)
    form = TaskForm(request.POST or None)
    form.fields['Assigned_To'].queryset = User.objects.filter(Role='EMPLOYEE')
    if form.is_valid():
        task = form.save(commit=False)
        task.P_ID = project
        task.save()
        messages.success(request, "Task created successfully!")
        return redirect('project_detail', id=project.ID)
    return render(request, 'task_form.html', {
        'form': form,
        'project': project,
        'user_role': request.user.Role
    })
@login_required
def task_edit(request, id):
    task = get_object_or_404(Task, ID=id)
    if request.user.Role == 'EMPLOYEE':
        if request.method == "POST":
            status = request.POST.get("Status")
            if status:
                task.Status = status
                task.save()
                messages.success(request, "Task status updated successfully!")
        return redirect('project_detail', id=task.P_ID.ID)
    if request.user.Role == 'MANAGER':
        if request.method == "POST":
            if request.POST.get("remove_member"):
                task.delete()
                messages.success(request, "Task deleted successfully!")
                return redirect('project_detail', id=task.P_ID.ID)
            if task.Status == "In Progress":
                messages.error(
                    request,
                    "Cannot change member while task is In Progress!"  )
                return redirect('project_detail', id=task.P_ID.ID)
            if task.Status == "Done":
                messages.error(
                    request,
                    "Cannot assign member. Task already completed!" )
                return redirect('project_detail', id=task.P_ID.ID)
            assigned_to = request.POST.get("assigned_to")
            if assigned_to:
                user = User.objects.get(id=assigned_to)
                if user.Role == "EMPLOYEE":
                    task.Assigned_To = user
                else:
                    task.Assigned_To = None
                task.save()
                messages.success(request, "Task assigned successfully!")
                return redirect('project_detail', id=task.P_ID.ID)
    return redirect('task_list')
@login_required
def task_delete(request, id):
    task = get_object_or_404(Task, ID=id)
    if request.user.Role not in ['ADMIN', 'MANAGER']:
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
    return render(request, 'comment_form.html', {
        'form': form,
        'user_role': request.user.Role
    })
# ================= ADD MEMBER =================
@login_required
def add_member_to_project(request, project_id):
    project = get_object_or_404(Project, ID=project_id)
    if request.user.Role not in ['ADMIN', 'MANAGER']:
        return redirect('dashboard')
    if request.method == 'POST':
        user_ids = request.POST.getlist('user_ids')
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                project.Members.add(user)
            except User.DoesNotExist:
                continue
        messages.success(request, "Members added successfully!")
        return redirect('project_detail', id=project.ID)
    unassigned_users = User.objects.filter(Role='EMPLOYEE').exclude(
        id__in=project.Members.values_list('id', flat=True)
    )
    return render(request, 'add_member_to_project.html', {
        'project': project,
        'unassigned_users': unassigned_users,
        'user_role': request.user.Role
    })
@login_required
def reset_user_password(request, id):
    user_obj = get_object_or_404(User, id=id)
    if request.user.Role != 'ADMIN' and request.user.id != user_obj.id:
        return redirect('dashboard')
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        if not new_password or not confirm_password:
            messages.error(request, "Fields cannot be empty!")
            return redirect('reset_user_password', id=id)
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('reset_user_password', id=id)
        if request.user.Role != 'ADMIN':
            if not check_password(old_password, user_obj.password):
                messages.error(request, "Old password is incorrect!")
                return redirect('reset_user_password', id=id)
        user_obj.set_password(new_password)
        user_obj.save()
        if request.user.id == user_obj.id:
            update_session_auth_hash(request, user_obj)
        messages.success(request, f"Password updated for {user_obj.username}")
        return redirect('user_list')
    return render(request, 'reset_user_password.html', {
        'user_obj': user_obj,
        'user_role': request.user.Role
    })