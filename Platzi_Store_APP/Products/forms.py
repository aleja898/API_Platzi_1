from django import forms
import requests

class ProductForm(forms.Form):
    title = forms.CharField(label='Producto', max_length=200)
    price = forms.IntegerField(label='Precio', min_value=0)
    description = forms.CharField(widget=forms.Textarea, label='Descripción')
    images = forms.CharField(label='Urls de las imágenes (separadas por comas)', widget=forms.Textarea)
    
    # Category field with dynamic choices
    category_id = forms.ChoiceField(label='Categoria')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            response = requests.get("https://api.escuelajs.co/api/v1/categories")
            response.raise_for_status()
            categories = response.json()
            # Create a list of tuples for the choices: (value, label)
            category_choices = [(cat['id'], cat['name']) for cat in categories]
            self.fields['category_id'].choices = category_choices
        except requests.exceptions.RequestException:
            # Handle API call failure gracefully
            self.fields['category_id'].choices = [('', 'Failed to load categories')]

    def clean_images(self):
        # Validate that each part of the comma-separated string is a URL
        images_string = self.cleaned_data.get('images', '')
        image_urls = [url.strip() for url in images_string.split(',')]
        
        # A simple check for URL format
        for url in image_urls:
            if not (url.startswith('http://') or url.startswith('https://')):
                raise forms.ValidationError("Each image URL must be a valid HTTP or HTTPS URL.")
        return images_string