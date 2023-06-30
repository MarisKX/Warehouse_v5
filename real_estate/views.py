
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from nbtlib import File
import os

from companies.models import Company
from real_estate.models import RealEstate, RealEstateCoordinates
from .models import MinecraftMap


# def show_map(request):
    # all_coordinates = RealEstateCoordinates.objects.all()
    # all_real_estates = RealEstate.objects.all()

    # context = {
    #     'all_coordinates': all_coordinates,
    #     'all_real_estates': all_real_estates,
    # }
    # return render(request, 'real_estate/map.html', context)

@login_required
def show_map(request):
    # Get the base directory of your Django project
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(base_dir)

    # Construct the absolute file path
    file_path = os.path.join(base_dir, "workspace/Warehouse_v5/media/maps/level.dat")
    map = MinecraftMap.objects.filter().last()
    print(file_path)
    level_file = File(file_path)
    # map_width = level_file.get("Data", {}).get("Level", {}).get("Width", {}).value
    # map_height = level_file.get("Data", {}).get("Level", {}).get("Height", {}).value
    # block_data = level_file.get("Data", {}).get("Level", {}).get("Blocks", {}).value

    context = {
        'map': map,
    }
    return render(request, 'real_estate/map_new.html', context)
