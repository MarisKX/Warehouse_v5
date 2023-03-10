
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from companies.models import Company
from real_estate.models import RealEstate, RealEstateCoordinates


@login_required
def show_map(request):
    """ A view to return the map page """

    all_coordinates = RealEstateCoordinates.objects.all()
    all_real_estates = RealEstate.objects.all()

    context = {
        'all_coordinates': all_coordinates,
        'all_real_estates': all_real_estates,
    }
    return render(request, 'real_estate/map.html', context)
