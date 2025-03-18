from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.contrib.auth import logout
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .forms import RegisterForm, Task, TaskForm, ProfileForm, UserUpdateForm
from .models import CustomUser
from django.utils.timezone import now, timedelta



@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id,user=request.user)

    if request.method == "POST":
        task.delete()
        return redirect("task_list")

    return render(request, "task/task_delete.html", {"task": task})


@login_required
def task_update(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'task/task_update.html', {'form': form, 'task': task})


@login_required
def task_complete(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk, user=request.user)
    task.status = "Done"
    task.save()
    return redirect("task_list")

@login_required
def completed_tasks(request):
    tasks = Task.objects.filter(user=request.user, status="Done")

    return render(request, "task/completed_tasks.html", {"tasks": tasks})

@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect("task_list")
    else:
        form = TaskForm()

    return render(request, "task/task_form.html", {"form": form})





@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)

    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")
    priority_filter = request.GET.get("priority", "")
    deadline_filter = request.GET.get("deadline", "")

    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    if deadline_filter == "today":
        tasks = tasks.filter(deadline=now().date())
    elif deadline_filter == "this_week":
        tasks = tasks.filter(deadline__range=[now().date(), now().date() + timedelta(days=7)])
    elif deadline_filter == "this_month":
        tasks = tasks.filter(deadlinemonth=now().month, deadlineyear=now().year)

    return render(request, "task/task_list.html", {
        "tasks": tasks,
        "search_query": search_query,
        "status_filter": status_filter,
        "priority_filter": priority_filter,
        "deadline_filter": deadline_filter,
    })

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'status', 'deadline']
    template_name = 'task/task_form.html'
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'status', 'deadline',]
    template_name = 'task/task_form.html'
    success_url = reverse_lazy('task_list')

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'task/task_delete.html'
    success_url = reverse_lazy('task_list')

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()


            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            activation_link = f"http://{domain}/activate/{uid}/{token}"


            subject = "Подтверждение регистрации"
            message = f"Привет, {user.username}! Перейдите по ссылке, чтобы активировать аккаунт: {activation_link}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

            messages.success(request, "На вашу почту отправлена ссылка для активации.")
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Ваш аккаунт активирован! Теперь вы можете войти.")
        return redirect("login")
    else:
        messages.error(request, "Ссылка для активации недействительна.")
        return redirect("register")


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('login')



@login_required
def profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, "registration/profile.html", {"form": form})




@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'registration/edit_profile.html', {'form': form})


class CustomPasswordChangeView( PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('password_change_done')


class CustomPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.html"
    success_url = reverse_lazy("password_reset_done")