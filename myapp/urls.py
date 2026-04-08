from django.urls import path
from . import views

urlpatterns = [
    #  login
    path('', views.login_view, name='login'),         
    path('login/', views.login_view, name='login'),    
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # User CRUD
    path('users/', views.user_list, name='user_list'),
    path('user/create/', views.create_user, name='create_user'),
    path('user/edit/<int:id>/', views.edit_user, name='edit_user'),
    path('user/delete/<int:id>/', views.delete_user, name='delete_user'),

    # Project CRUD
    path('projects/', views.project_list, name='project_list'),
    path('project/add/', views.project_add, name='project_add'),
    path('project/edit/<int:id>/', views.project_edit, name='project_edit'),
    path('project/delete/<int:id>/', views.project_delete, name='project_delete'),

    # Task CRUD
    path('tasks/', views.task_list, name='task_list'),
    path('task/add/', views.task_add, name='task_add'),
    path('task/edit/<int:id>/', views.task_edit, name='task_edit'),
    path('task/delete/<int:id>/', views.task_delete, name='task_delete'),

    # Comments
    path('task/<int:task_id>/comment/', views.add_comment, name='add_comment'),
]