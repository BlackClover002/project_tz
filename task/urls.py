from django.urls import path
from .views import task_create, register, task_update, task_delete, profile, task_list, edit_profile, logout_view, \
    CustomPasswordChangeView, task_complete, completed_tasks
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('', task_list, name='task_list'),
    path('register/', register, name='register'),
    path('create/', task_create, name='task_create'),
    path('task/completed/', completed_tasks, name='completed_tasks'),
    path("task/<int:task_id>/delete/", task_delete, name="task_delete"),
    path('<int:task_pk>/update/', task_update, name='task_update'),
    path('<int:task_id>/delete/', task_delete, name='task_delete'),
    path('<int:task_pk>/complete/', task_complete, name='task_complete'),
    path('<int:task_pk>/complete/', task_complete, name='task_complete'),




    path('profile', profile, name='profile'),
    path('edit_profile', edit_profile, name='edit_profile'),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", logout_view,  name="logout"),


    path("password_change/", CustomPasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/", auth_views.PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"), name="password_change_done"),

    path("password_reset/", CustomPasswordChangeView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]