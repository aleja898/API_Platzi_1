from django import forms

class ProductForm(forms.Form):
    """
    Formulario para crear un nuevo producto.
    Campos requeridos por la API de productos.
    """
    title = forms.CharField(
        max_length=200,
        label='Título del Producto',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa el título del producto'
        })
    )
    
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='Precio',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Precio en USD',
            'step': '0.01'
        })
    )
    
    description = forms.CharField(
        label='Descripción',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe el producto'
        })
    )
    
    images = forms.URLField(
        label='URL de la Imagen',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://ejemplo.com/imagen.jpg'
        }),
        help_text='Proporciona la URL de una imagen del producto'
    )