import requests
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .forms import ProductForm, UpdateProductForm


# URL base de la API de productos
API_BASE_URL = "https://api.escuelajs.co/api/v1/products/"
API_CATEGORIES_URL = "https://api.escuelajs.co/api/v1/categories/"

def home(request):
    """
    Vista principal que muestra la página de inicio con botones
    de navegación hacia las funcionalidades principales.
    """
    return render(request, 'home.html')

def consult_products(request):
    """
    Vista que consulta todos los productos de la API externa
    y los muestra en una plantilla.
    Maneja errores de conexión y de la API.
    Incluye funcionalidad de filtrado por categoría.
    """
    products = []
    categories = []
    error_message = None
    category_filter = request.GET.get('category')
    
    try:
        # Obtener categorías para el filtro
        categories_response = requests.get(API_CATEGORIES_URL, timeout=10)
        if categories_response.status_code == 200:
            categories = categories_response.json()
        
        # Construir URL para productos con filtro opcional
        api_url = API_BASE_URL
        if category_filter:
            api_url += f"?categoryId={category_filter}"
            
        # Realizar solicitud GET a la API
        response = requests.get(api_url, timeout=10)
        
        # Verificar si la respuesta fue exitosa
        if response.status_code == 200:
            products = response.json()
        else:
            error_message = f"Error en la API: Código {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        error_message = "Error de conexión: No se pudo conectar con la API"
    except requests.exceptions.Timeout:
        error_message = "Error de tiempo: La API tardó demasiado en responder"
    except requests.exceptions.RequestException as e:
        error_message = f"Error en la solicitud: {str(e)}"
    
    context = {
        'products': products,
        'categories': categories,
        'error_message': error_message,
        'selected_category': int(category_filter) if category_filter else None
    }
    
    return render(request, 'consult_products.html', context)


def create_product(request):
    """
    Vista para crear un nuevo producto.
    Maneja el envío de datos a la API de productos.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            # Construir el JSON de los datos del producto
            product_data = {
                'title': form.cleaned_data['title'],
                'price': float(form.cleaned_data['price']),
                'description': form.cleaned_data['description'],
                'images': [form.cleaned_data['images']],
                'categoryId': 1 # Categoría predeterminada si se requiere
            }
            
            try:
                # Enviar solicitud POST a la API
                response = requests.post(
                    API_BASE_URL,
                    json=product_data,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 201:
                    # Producto creado exitosamente
                    messages.success(request, 'Producto creado exitosamente')
                    return redirect('consult_products')
                else:
                    # Error en la creación
                    messages.error(request, f'Error al crear el producto: Código {response.status_code}')
                    
            except requests.exceptions.ConnectionError:
                messages.error(request, 'Error de conexión: No se pudo conectar con la API')
            except requests.exceptions.Timeout:
                messages.error(request, 'Error de tiempo: La API tardó demasiado en responder')
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Error en la solicitud: {str(e)}')
            except Exception as e:
                messages.error(request, f'Error inesperado: {str(e)}')
    else:
        # Mostrar formulario vacío para GET
        form = ProductForm()
    
    return render(request, 'create_product.html', {'form': form})


def detail_product(request, pk):
    """
    Vista que consulta un producto específico por su ID.
    Maneja errores de conexión y de la API.
    """
    product = None
    try:
        # Realizar solicitud GET a la API para un producto específico
        api_url = f"{API_BASE_URL}{pk}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            product = response.json()
        else:
            messages.error(request, f'Error al obtener el producto: Código {response.status_code}')
            return redirect('consult_products')
            
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Error al obtener el producto: {str(e)}')
        return redirect('consult_products')
    
    return render(request, 'detail_product.html', {'product': product})


def update_product(request, pk):
    """
    Vista para actualizar un producto existente.
    Maneja el envío de datos a la API de productos.
    """
    api_url = f"{API_BASE_URL}{pk}"
    
    try:
        # Obtener los datos actuales del producto para rellenar el formulario
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            messages.error(request, f'Error al obtener el producto para actualizar: Código {response.status_code}')
            return redirect('consult_products')
        
        product_data = response.json()

    except requests.exceptions.RequestException as e:
        messages.error(request, f'Error al conectar con la API para actualizar: {str(e)}')
        return redirect('consult_products')
    
    if request.method == 'POST':
        form = UpdateProductForm(request.POST)
        if form.is_valid():
            updated_data = {
                'title': form.cleaned_data['title'],
                'price': float(form.cleaned_data['price']),
                'description': form.cleaned_data['description'],
                'images': [form.cleaned_data['images']],
            }
            
            try:
                response = requests.put(api_url, json=updated_data, timeout=10)
                
                if response.status_code == 200:
                    messages.success(request, 'Producto actualizado exitosamente')
                    return redirect('detail_product', pk=pk)
                else:
                    messages.error(request, f'Error al actualizar el producto: Código {response.status_code}')
            
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Error de solicitud al actualizar: {str(e)}')
    else:
        # Si es un GET, inicializar el formulario con los datos existentes
        form = UpdateProductForm(initial={
            'title': product_data.get('title'),
            'price': product_data.get('price'),
            'description': product_data.get('description'),
            'images': product_data.get('images')[0] if product_data.get('images') else ''
        })
    
    context = {
        'form': form,
        'product': product_data,
    }
    
    return render(request, 'update_product.html', context)


def delete_product(request, pk):
    """
    Vista para eliminar un producto.
    Maneja la confirmación y la solicitud DELETE a la API.
    """
    api_url = f"{API_BASE_URL}{pk}"
    
    # Obtener el producto para mostrar sus detalles en la página de confirmación
    product = None
    try:
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            messages.error(request, f'Error al obtener el producto para eliminar: Código {response.status_code}')
            return redirect('consult_products')
            
        product = response.json()
        
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Error al obtener el producto: {str(e)}')
        return redirect('consult_products')
    
    if request.method == 'POST':
        try:
            # Enviar solicitud DELETE a la API
            response = requests.delete(api_url, timeout=10)
            
            if response.status_code == 200:
                # Producto eliminado exitosamente
                messages.success(request, 'Producto eliminado exitosamente')
                return redirect('consult_products')
            else:
                # Error en la eliminación
                messages.error(request, f'Error al eliminar el producto: Código {response.status_code}')
                
        except requests.exceptions.ConnectionError:
            messages.error(request, 'Error de conexión: No se pudo conectar con la API')
        except requests.exceptions.Timeout:
            messages.error(request, 'Error de tiempo: La API tardó demasiado en responder')
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Error en la solicitud: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
    
    context = {
        'product': product,
    }
    
    return render(request, 'delete_product.html', context)