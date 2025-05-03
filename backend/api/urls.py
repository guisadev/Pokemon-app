# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PokemonViewSet # Importa tu ViewSet

# Crea un router por defecto.
# Este router genera automáticamente las rutas para listar (/pokemon/)
# y detallar (/pokemon/{pk}/) para tu ViewSet.
router = DefaultRouter()
router.register(r'pokemon', PokemonViewSet, basename='pokemon')
# 'basename' es importante si tu ViewSet no tiene un .queryset definido.

# Los urlpatterns de esta app incluyen las URLs generadas por el router.
urlpatterns = [
    # Esto incluye /pokemon/ (list) y /pokemon/{pk}/ (detail)
    path('', include(router.urls)),
    # Si implementaste la acción custom 'search', podrías añadirla aquí si no la manejó el router:
    # path('pokemon/search/', PokemonViewSet.as_view({'get': 'search'}), name='pokemon-search'),
    # ... otras rutas de tu app si tienes ...
]