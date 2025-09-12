import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .forms import ProductForm

BASE_API_URL = "https://api.escuelajs.co/api/v1/products"
CATEGORY_API_URL = "https://api.escuelajs.co/api/v1/categories"

def home(request):
    """
    Renders the homepage.
    """
    return render(request, 'home.html')


def catalog(request):
    """
    Renders the product catalog, with optional filtering.
    """
    category_id = request.GET.get('category')
    api_url = f"{BASE_API_URL}?categoryId={category_id}" if category_id else BASE_API_URL

    try:
        products_response = requests.get(api_url)
        products_response.raise_for_status() # Raise an exception for bad status codes
        products = products_response.json()
        
        categories_response = requests.get(CATEGORY_API_URL)
        categories_response.raise_for_status()
        categories = categories_response.json()

        return render(request, 'catalog.html', {
            'products': products,
            'categories': categories,
            'selected_category': category_id
        })
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error fetching data from API: {e}", status=500)

def product_detail(request, product_id):
    """
    Renders the details of a single product.
    """
    try:
        product_response = requests.get(f"{BASE_API_URL}/{product_id}")
        product_response.raise_for_status()
        product = product_response.json()
        return render(request, 'product_detail.html', {'product': product})
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error fetching product: {e}", status=500)
@login_required
def product_add(request):
    """
    Handles the creation of a new product.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                # The API expects a list of image URLs.
                images_list = [img.strip() for img in form.cleaned_data['images'].split(',')]
                
                payload = {
                    'title': form.cleaned_data['title'],
                    'price': form.cleaned_data['price'],
                    'description': form.cleaned_data['description'],
                    'categoryId': form.cleaned_data['category_id'],
                    'images': images_list,
                }
                
                response = requests.post(BASE_API_URL, json=payload)
                response.raise_for_status()
                return redirect('catalog')
            except requests.exceptions.RequestException as e:
                form.add_error(None, f"Error creating product: {e}")
    else:
        form = ProductForm()
    
    return render(request, 'product_form.html', {'form': form, 'page_title': 'Add New Product'})

def product_edit(request, product_id):
    """
    Handles the editing of an existing product.
    """
    try:
        # Fetch the current product data
        response = requests.get(f"{BASE_API_URL}/{product_id}")
        response.raise_for_status()
        product_data = response.json()
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error fetching product data for edit: {e}", status=500)

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                images_list = [img.strip() for img in form.cleaned_data['images'].split(',')]
                
                payload = {
                    'title': form.cleaned_data['title'],
                    'price': form.cleaned_data['price'],
                    'description': form.cleaned_data['description'],
                    'categoryId': form.cleaned_data['category_id'],
                    'images': images_list,
                }
                
                response = requests.put(f"{BASE_API_URL}/{product_id}", json=payload)
                response.raise_for_status()
                return redirect('product_detail', product_id=product_id)
            except requests.exceptions.RequestException as e:
                form.add_error(None, f"Error updating product: {e}")
    else:
        # Populate the form with current product data
        initial_data = {
            'title': product_data.get('title'),
            'price': product_data.get('price'),
            'description': product_data.get('description'),
            'category_id': product_data.get('category', {}).get('id'),
            'images': ', '.join(product_data.get('images', [])),
        }
        form = ProductForm(initial=initial_data)
    
    return render(request, 'product_form.html', {'form': form, 'page_title': 'Edit Product'})


def product_delete(request, product_id):
    """
    Handles the deletion of a product.
    """
    if request.method == 'POST':
        try:
            response = requests.delete(f"{BASE_API_URL}/{product_id}")
            response.raise_for_status()
            return redirect('catalog')
        except requests.exceptions.RequestException as e:
            return HttpResponse(f"Error deleting product: {e}", status=500)
    
    return HttpResponseRedirect(reverse('product_detail', args=[product_id]))
