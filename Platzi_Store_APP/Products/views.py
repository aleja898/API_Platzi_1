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
            # Limitar a 50 productos para mejor rendimiento
            products = products[:50]
        else:
            error_message = f"Error en la API: Código {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        error_message = "Error de conexión: No se pudo conectar con la API"
    except requests.exceptions.Timeout:
        error_message = "Error de tiempo: La API tardó demasiado en responder"
    except requests.exceptions.RequestException as e:
        error_message = f"Error en la solicitud: {str(e)}"
    except Exception as e:
        error_message = f"Error inesperado: {str(e)}"
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_filter,
        'error_message': error_message
    }
    
    return render(request, 'consult_products.html', context)

def detail_product(request, pk):
    """
    Vista que obtiene los detalles de un producto específico de la API.
    """
    try:
        # Construye la URL para el producto específico
        api_url = f"{API_BASE_URL}{pk}"
        response = requests.get(api_url, timeout=10)

        # Si la solicitud es exitosa, obtén los datos del producto
        if response.status_code == 200:
            product = response.json()
            return render(request, 'detail_product.html', {'product': product})
        elif response.status_code == 404:
            # Si el producto no se encuentra en la API, muestra un error 404
            return render(request, 'error_404.html', {'message': 'Producto no encontrado.'}, status=404)
        else:
            # Maneja otros códigos de error de la API
            return render(request, 'error.html', {'message': 'Error al conectar con la API.'})
    except requests.exceptions.RequestException as e:
        # Captura errores de red, como problemas de conexión
        return render(request, 'error.html', {'message': f"Error de conexión: {e}"})

def create_product(request):
    """
    Vista que maneja la creación de nuevos productos.
    GET: Muestra el formulario vacío
    POST: Procesa los datos y envía la solicitud a la API
    """
    if request.method == 'POST':
        form = ProductForm(request.POST)
        
        if form.is_valid():
            # Preparar datos para enviar a la API
            product_data = {
                'title': form.cleaned_data['title'],
                'price': float(form.cleaned_data['price']),
                'description': form.cleaned_data['description'],
                'images': [form.cleaned_data['images']],  # La API espera una lista
                'categoryId': 1  # Valor fijo como se requiere
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

def update_product(request, pk):
    """
    Vista que maneja la actualización de productos existentes.
    GET: Muestra el formulario pre-poblado con los datos actuales
    POST: Procesa los datos y envía la solicitud de actualización a la API
    """
    # Primero obtener el producto actual
    try:
        api_url = f"{API_BASE_URL}{pk}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            messages.error(request, 'Producto no encontrado')
            return redirect('consult_products')
            
        product = response.json()
        
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Error al obtener el producto: {str(e)}')
        return redirect('consult_products')
    
    if request.method == 'POST':
        form = UpdateProductForm(request.POST)
        
        if form.is_valid():
            # Preparar datos para enviar a la API
            product_data = {
                'title': form.cleaned_data['title'],
                'price': float(form.cleaned_data['price']),
                'description': form.cleaned_data['description'],
                'images': [form.cleaned_data['images']],
                'categoryId': product.get('category', {}).get('id', 1)  # Mantener categoría original
            }
            
            try:
                # Enviar solicitud PUT a la API
                response = requests.put(
                    api_url,
                    json=product_data,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    # Producto actualizado exitosamente
                    messages.success(request, 'Producto actualizado exitosamente')
                    return redirect('detail_product', pk=pk)
                else:
                    # Error en la actualización
                    messages.error(request, f'Error al actualizar el producto: Código {response.status_code}')
                    
            except requests.exceptions.ConnectionError:
                messages.error(request, 'Error de conexión: No se pudo conectar con la API')
            except requests.exceptions.Timeout:
                messages.error(request, 'Error de tiempo: La API tardó demasiado en responder')
            except requests.exceptions.RequestException as e:
                messages.error(request, f'Error en la solicitud: {str(e)}')
            except Exception as e:
                messages.error(request, f'Error inesperado: {str(e)}')
    else:
        # Mostrar formulario pre-poblado para GET
        initial_data = {
            'title': product.get('title', ''),
            'price': product.get('price', 0),
            'description': product.get('description', ''),
            'images': product.get('images', [''])[0] if product.get('images') else '',
        }
        form = UpdateProductForm(initial=initial_data)
    
    context = {
        'form': form,
        'product': product,
    }
    
    return render(request, 'update_product.html', context)

def delete_product(request, pk):
    """
    Vista que maneja la eliminación de productos.
    GET: Muestra la página de confirmación de eliminación
    POST: Procesa la eliminación del producto
    """
    # Primero obtener el producto para mostrar sus detalles
    try:
        api_url = f"{API_BASE_URL}{pk}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            messages.error(request, 'Producto no encontrado')
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