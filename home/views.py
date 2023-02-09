from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
# from companies.models import Company
from .models import AppSettings

# Index (home) view
@login_required
def index(request):
    """ A view to return the index page """
    owner = request.user
    context = {
        'owner': owner,
    }

    return render(request, 'home/index.html', context)


# Settings view
@login_required
def settings(request):
    """ A view to return the index page """
    owner = request.user
    current_settings = get_object_or_404(AppSettings, valid=True)
    settings_history = AppSettings.objects.filter(valid=False).order_by('valid_till')

    context = {
        'owner': owner,
        'current_settings': current_settings,
        'settings_history': settings_history,
    }

    return render(request, 'home/settings.html', context)
