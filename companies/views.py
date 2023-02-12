from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

# All Products view
@login_required
def all_companies(request):
    """ A view to show all companies including their warehouses and search queries """

    def is_ajax(request):
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    if is_ajax(request):
        print(request)

    context = {

    }

    return render(request, 'products/products.html', context)
