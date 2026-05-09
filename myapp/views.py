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
from django.http import JsonResponse
from .models import ProjectFile
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle


from .models import Project, Task, TaskHistory, ProjectFile

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
        'user_role': request.user.Role})
@login_required
def create_user(request):
    if request.user.Role != 'ADMIN':
        return redirect('dashboard')
    form = UserCreateForm(request.POST or None)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if request.method == "POST":
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=f"{data['first_name']}_{data['last_name']}".lower(),
                email=data['email'],
                password=data['password1'],
                first_name=data['first_name'],
                last_name=data['last_name'],
            )
            user.Role = data.get("Role")
            user.Phone = data.get("Phone")
            user.JoinDate = data.get("JoinDate")
            user.Dept = data.get("Dept")
            user.save()
            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "message": "User created successfully!" })
            messages.success(request, "User created successfully!")
            return redirect('user_list')
        if is_ajax:
            errors = {
                field: error[0] for field, error in form.errors.items() }
            return JsonResponse({
                "success": False,
                "errors": errors
            })
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
        form = UserUpdateForm(
            request.POST or None,
            instance=user_obj,
            request=request   
        )
        form.fields.pop('Post', None)

        if request.user.id != user_obj.id:
            form.fields.pop('password', None)

    else:
        form = UserSelfUpdateForm(request.POST or None, instance=user_obj)

    if request.method == "POST":
        if form.is_valid():
            user = form.save()

            if request.user.id == user.id:
                update_session_auth_hash(request, user)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": True,
                    "message": "Profile updated successfully!"
                })

            messages.success(request, "Profile updated successfully!")
            return redirect('user_detail', id=user_obj.id)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "success": False,
                "errors": form.errors
            })

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
            Q(Created_By=request.user) | Q(Created_By__Role='ADMIN'))
    else:
        projects = Project.objects.filter(Members=request.user)
    return render(request, 'project_list.html', {
        'projects': projects,
        'user_role': request.user.Role})
@login_required
def project_add(request):
    if request.user.Role not in ['ADMIN', 'MANAGER']:
        return redirect('dashboard')
    form = ProjectForm(request.POST or None)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.Created_By = request.user
            obj.save()
            form.save_m2m()
            obj.Members.add(request.user)
            files = request.FILES.getlist('files')  # input name="files"
            for f in files:
                ProjectFile.objects.create(
                    Project=obj,
                    File=f )
            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "message": "Project added successfully!" })
            messages.success(request, "Project added successfully!")
            return redirect('project_list')
        if is_ajax:
            return JsonResponse({
                "success": False,
                "errors": form.errors
            })
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
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.Created_By = project.Created_By
            obj.save()
            form.save_m2m()
            files = request.FILES.getlist('files')
            for f in files:
                ProjectFile.objects.create(
                    Project=obj,
                    File=f  )
            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "message": "Project updated successfully!"
                })
            messages.success(request, "Project updated successfully!")
            return redirect('project_list')
        if is_ajax:
            return JsonResponse({
                "success": False,
                "errors": form.errors
            })
    return render(request, 'project_form.html', {
        'form': form,
        'user_role': request.user.Role,
        'creator': project.Created_By})
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
    members = project.Members.exclude(Role='ADMIN')
    employees = project.Members.filter(Role='EMPLOYEE')
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
                Q(id=user.id) | Q(Role='ADMIN') ) )
    else:
        project_id = request.GET.get('project_id')
        if project_id:
            tasks = Task.objects.filter(
                Assigned_To=user,
                P_ID__ID=project_id
            )
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
    form.fields['Assigned_To'].queryset = project.Members.filter(Role='EMPLOYEE')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if request.method == "POST":
        if form.is_valid():
            task = form.save(commit=False)
            task.P_ID = project
            task.save()
            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "redirect_url": f"/project/{project.ID}/"
                })
            messages.success(request, "Task created successfully!")
            return redirect('project_detail', id=project.ID)
        if is_ajax:
            return JsonResponse({
                "success": False,
                "errors": form.errors
            })
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
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        "status": "success",
                        "message": "Task status updated successfully!"
                    })
                messages.success(request, "Task status updated successfully!")
        return redirect('project_detail', id=task.P_ID.ID)
    if request.user.Role == 'MANAGER':
        if request.method == "POST":
            if request.POST.get("remove_member"):
                task.delete()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        "status": "deleted",
                        "message": "Task deleted successfully!"
                    })
                messages.success(request, "Task deleted successfully!")
                return redirect('project_detail', id=task.P_ID.ID)
            if task.Status == "Done":
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        "status": "error",
                        "message": "Task already completed. No changes allowed!"
                    })
                messages.error(request, "Task already completed. No changes allowed!")
                return redirect('project_detail', id=task.P_ID.ID)
            if task.Status == "In Progress":
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        "status": "error",
                        "message": "Cannot change member while task is In Progress!"
                    })
                messages.error(request, "Cannot change member while task is In Progress!")
                return redirect('project_detail', id=task.P_ID.ID)
            assigned_to = request.POST.get("assigned_to")
            if assigned_to:
                user = User.objects.get(id=assigned_to)
                if user.Role == "EMPLOYEE":
                    task.Assigned_To = user
                else:
                    task.Assigned_To = None
                task.save()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        "status": "success",
                        "message": "Task assigned successfully!"
                    })
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
    if request.method == 'POST' and request.POST.get('user_ids'):
        user_ids = request.POST.getlist('user_ids')
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                project.Members.add(user)
            except User.DoesNotExist:
                continue
        messages.success(request, "Members added successfully!")
        return redirect('project_detail', id=project.ID)
    if request.method == 'POST' and request.POST.get('remove_member_id'):
        user_id = request.POST.get('remove_member_id')
        try:
            user = User.objects.get(id=user_id)
            project.Members.remove(user)
            messages.success(request, "Member removed successfully!")
        except User.DoesNotExist:
            pass
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
@login_required
def project_download_pdf(request, id):

    project = get_object_or_404(Project, ID=id)

    if request.user.Role != 'MANAGER':
        return redirect('dashboard')

    tasks = Task.objects.filter(P_ID=project)
    files = ProjectFile.objects.filter(Project=project)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    brand_yellow = colors.HexColor("#FFD700")
    border_gray = colors.HexColor("#E5E7EB")
    dark = colors.HexColor("#111827")
    text = colors.HexColor("#374151")

    def draw_base():

        p.setStrokeColor(brand_yellow)
        p.setLineWidth(10)
        p.rect(20, 20, width - 40, height - 40, stroke=1, fill=0)

        p.setFillColor(dark)
        p.rect(20, height - 100, width - 40, 100, fill=1, stroke=0)

        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 22)
        p.drawCentredString(width / 2, height - 55, "PROJECT REPORT")

        p.setFont("Helvetica", 14)
        p.setFillColor(colors.HexColor("#d1d5db"))
        p.drawCentredString(width / 2, height - 80, project.Name)

        p.setFillColor(brand_yellow)
        p.roundRect(40, height - 90, 60, 30, 6, fill=1)

        p.setFillColor(dark)
        p.setFont("Helvetica-Bold", 12)
        p.drawString(55, height - 80, str(project.ID))


        logo_x = width - 75
        logo_y = height - 55
        radius = 26

        p.setFillColor(colors.HexColor("#FFD700"))
        p.circle(logo_x, logo_y, radius + 2, fill=1, stroke=0)

        p.setFillColor(colors.HexColor("#111827"))
        p.circle(logo_x, logo_y, radius, fill=1, stroke=0)

        p.setStrokeColor(colors.HexColor("#FFD700"))
        p.setLineWidth(2)
        p.circle(logo_x, logo_y, radius - 3, fill=0, stroke=1)
        p.setFillColor(colors.HexColor("#FFD700"))
        p.circle(logo_x, logo_y + 6, 3, fill=1, stroke=0)

        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 6.5)
        p.drawCentredString(logo_x, logo_y - 2, "TASK")

        p.setFont("Helvetica-Bold", 5.5)
        p.drawCentredString(logo_x, logo_y - 11, "MANAGEMENT")

        p.setFont("Helvetica-Bold", 5.5)
        p.drawCentredString(logo_x, logo_y - 20, "SYSTEM")

    def section(title, y):

        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(dark)
        p.drawCentredString(width / 2, y, title.upper())

        p.setStrokeColor(border_gray)
        p.setLineWidth(0.8)
        p.line(60, y - 5, width - 60, y - 5)

        return y - 25

    def table(data, y, col_widths):

        t = Table(data, colWidths=col_widths)

        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), brand_yellow),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),

            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),

            ('FONTSIZE', (0, 0), (-1, -1), 8),

            ('GRID', (0, 0), (-1, -1), 0.5, border_gray),

            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        t.wrapOn(p, width, height)
        w, h = t.wrap(0, 0)

        t.drawOn(p, 60, y - h)

        return y - h - 15

    draw_base()
    y = height - 130

    y = section("Project Information", y)

    manager = project.Managed_By.username if project.Managed_By else "N/A"

    info = [
        ["Field", "Value"],
        ["Project ID", project.ID],
        ["Name", project.Name],
        ["Status", project.Status],
        ["Created By", project.Created_By.username],
        ["Managed By", manager],
        ["Start Date", project.Start],
        ["End Date", project.End],
    ]

    y = table(info, y, [200, 200])

    y = section("Project Description", y)

    desc = project.Desc if project.Desc else "No description available"

    y = table(
        [["Description"], [desc]],
        y,
        [400]
    )

    y = section("Team Members", y)

    team = [["Username", "Role"]]
    for m in project.Members.all():
        team.append([m.username, m.Role])

    y = table(team, y, [200, 200])

    y = section("Tasks Overview", y)

    task_data = [["Task", "Status", "Assigned To"]]

    for t in tasks:
        assigned = t.Assigned_To.username if t.Assigned_To else "Unassigned"
        task_data.append([t.Name, t.Status, assigned])

    y = table(task_data, y, [200, 100, 150])

    y = section("Project Files", y)

    file_data = [["File Name"]]

    if files.exists():
        for f in files:
            if f.File:
                file_data.append([f.File.name.split("/")[-1]])
    else:
        file_data.append(["No files uploaded"])

    y = table(file_data, y, [350])

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Project_Report_{project.ID}.pdf"'

    return response