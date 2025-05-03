# pokemon_project/urls.py

from django.contrib import admin
from django.urls import path, include # Deja estas importaciones aquí
from django.shortcuts import redirect # <-- Importa 'redirect' desde shortcuts

# Define una vista simple de redirección
def root_redirect(request):
    # La función redirect funciona igual una vez importada correctamente
    return redirect('/api/pokemon/')

urlpatterns = [
    path('', root_redirect, name='root-redirect'),

    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # ... otras URLs de proyecto ...
]