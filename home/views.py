from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
# from companies.models import Company
# from .models import AppSettings

# Create your views here.
@login_required
def index(request):
    """ A view to return the index page """
    owner = request.user
    context = {
        'owner': owner,
    }

    return render(request, 'home/index.html', context)
