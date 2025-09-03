import requests
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .forms import ProductForm


# URL base de la API de productos
API_BASE_URL = "https://api.escuelajs.co/api/v1/products/"

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
    """
    products = []
    error_message = None
    
    try:
        # Realizar solicitud GET a la API
        response = requests.get(API_BASE_URL, timeout=10)
        
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
    except Exception as e:
        error_message = f"Error inesperado: {str(e)}"
    
    context = {
        'products': products,
        'error_message': error_message
    }
    
    return render(request, 'consult_products.html', context)

def detail_product(request, pk):
    """
    Vista que obtiene los detalles de un producto de la API de Platzi FakeStore.
    """
    try:
        # Construye la URL para el producto específico
        api_url = f"{API_BASE_URL}{pk}"
        response = requests.get(api_url)

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