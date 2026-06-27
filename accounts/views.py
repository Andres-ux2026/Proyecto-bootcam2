from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm

    def form_invalid(self, form):
        from django.contrib import messages
        messages.error(self.request, "Usuario o contraseña incorrectos.")
        return super().form_invalid(form)
