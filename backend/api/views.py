# -*- coding: utf-8 -*-
# @Author: Carlos Galeano
# @Date:   2025-05-02 02:09:36
# @Last Modified by:   Carlos Galeano
# @Last Modified time: 2025-05-02 12:59:44
# api/views.py

import requests
from rest_framework import viewsets, status, pagination
from rest_framework.response import Response
# from rest_framework.decorators import action # Si añades acciones custom
from django.core.cache import cache # Importa el sistema de cache de Django
import traceback # Para imprimir errores detallados

from .serializers import PokemonSerializer # Importa tu Serializer

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/"
CACHE_TTL = 60 * 15 # Tiempo de vida del cache en segundos (15 minutos)


class PokemonPagination(pagination.PageNumberPagination):
    """
    Clase de paginación custom que hereda de PageNumberPagination.
    Define tamaño de página por defecto y permite cambiarlo vía query param.
    """
    page_size = 20 # Número de items por página por defecto
    page_size_query_param = 'page_size' # Permite al cliente cambiar el tamaño: ?page_size=X
    max_page_size = 100 # Tamaño máximo permitido


class PokemonViewSet(viewsets.ViewSet):
    """
    ViewSet para listar y recuperar Pokémon desde PokeAPI con cache.
    """
    serializer_class = PokemonSerializer # Para documentación/Browsable API en DRF
    pagination_class = PokemonPagination # Aplica la paginación a esta vista

    def list(self, request):
        """
        Lista Pokémon con paginación, obteniendo datos de PokeAPI (con cache).
        Implementa paginación manual usando el conteo total y calculando offset/limit para la API externa.
        """
        pokeapi_list_url = f"{POKEAPI_BASE_URL}pokemon/"

        paginator = self.pagination_class()

        # --- 1. Obtener Conteo Total (desde cache o API) ---
        # Necesitamos el conteo total para que el paginador sepa cuántas páginas existen.
        count_cache_key = 'pokeapi_total_count'
        total_count = cache.get(count_cache_key)

        if total_count is None:
            print("Fetching total count from PokeAPI...")
            try:
                # Hacemos una solicitud mínima solo para obtener el campo 'count'
                count_response = requests.get(f"{POKEAPI_BASE_URL}pokemon/?limit=1")
                count_response.raise_for_status()
                total_count_data = count_response.json()
                total_count = total_count_data.get('count', 0)
                # Cacheamos el conteo total por un tiempo más largo
                cache.set(count_cache_key, total_count, timeout=60 * 60 * 24) # Cachear por 24 horas
                print(f"Cached total count: {total_count}")
            except requests.exceptions.RequestException as e:
                 print(f"Error fetching total item count from PokeAPI: {e}")
                 return Response(
                    {"error": "Could not fetch total item count from external API."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                 )

        # Manejar caso de que no haya ítems
        if total_count == 0:
             # Si el conteo total es 0, simplemente retornamos una respuesta paginada vacía.
            # No necesitamos llamar paginate_queryset en este caso.
            return paginator.get_paginated_response([])


        # --- 2. Configurar el Paginador para que Calcule Offset/Limit y Estado Interno ---
        # Creamos una lista ficticia (dummy) con la longitud igual al conteo total.
        # Esto permite que el paginador de DRF (PageNumberPagination) calcule
        # correctamente el offset y limit para la página solicitada y configure
        # su estado interno, incluyendo el objeto 'page'.
        dummy_queryset = [None] * total_count

        # Llamamos a paginate_queryset. Aunque no usamos directamente su retorno,
        # esta llamada es ESENCIAL para que el paginador configure su estado interno
        # (especialmente el atributo 'page') necesario para get_paginated_response.
        page_slice_of_dummy = paginator.paginate_queryset(dummy_queryset, request, view=self)

        # --- 3. Obtener Offset y Limit Calculados por el Paginador ---
        # Después de llamar a paginate_queryset, el paginador ya calculó cuál
        # es el offset y el limit para la página solicitada.
        # Los obtenemos del objeto 'page' que ahora reside en el paginador.
        try:
            # El offset para la llamada a la API es el índice de inicio de la página menos 1.
            offset = paginator.page.start_index() - 1
            # El limit para la llamada a la API es simplemente el tamaño de página configurado.
            limit = paginator.page_size

            # Ajustes de seguridad/lógica (aunque paginator ya debería manejarlos)
            offset = max(0, offset)
            limit = max(1, limit) # El limit debe ser al menos 1 para la API

        except AttributeError:
             # Esto NO debería ocurrir si total_count > 0 y paginate_queryset se llamó.
             # Si ocurre, es un error inesperado en la paginación.
            print(f"Error accessing paginator page state after paginate_queryset.")
            traceback.print_exc()
            return Response(
                {"error": "Pagination calculation failed internally."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


        # --- 4. Buscar la Respuesta de esta Página Específica en Cache ---
        # La clave de cache usa el offset y limit reales que usaremos para la API externa.
        cache_key = f'pokeapi_list_offset_{offset}_limit_{limit}'
        cached_response_data = cache.get(cache_key)

        if cached_response_data:
            print(f"Serving list page (offset={offset}, limit={limit}) from cache: {cache_key}")
            # Cache hit: Servir los datos procesados que ya están en el formato de respuesta paginada de DRF
            return Response(cached_response_data)


        ##print(f"Fetching list page (offset={offset}, limit={limit}) from PokeAPI: {pokeapi_list_url}?offset={offset}&limit={limit}")
        print(f"Fetching list page (offset={offset}, limit={limit}) from PokeAPI: {pokeapi_list_url}?offset={offset}&limit={limit}")
 
        # --- 5. Obtener Datos Reales de la Página Específica desde PokeAPI ---
        try:
            response_list = requests.get(f"{pokeapi_list_url}?offset={offset}&limit={limit}")
            response_list.raise_for_status() # Lanza excepción para 4xx/5xx
            list_data = response_list.json()

            # pokemon_basic_list contiene la lista de {"name": "...", "url": "..."} para esta página.
            pokemon_basic_list = list_data.get('results', [])

            # --- 6. Obtener Detalles para Cada Pokémon de Esta Página (usando cache individual) ---
            # Este bucle sigue siendo necesario porque el endpoint de lista de PokeAPI no da todos los detalles.
            detailed_pokemon_list = []
            for entry in pokemon_basic_list:
                 # --- Lógica para obtener detalles de un Pokémon individual (con cache) ---
                 # (Copiada/reutilizada de la versión anterior y del método retrieve)
                try:
                    url_parts = entry['url'].rstrip('/').split('/')
                    pokemon_id = int(url_parts[-1])
                except (IndexError, ValueError):
                    print(f"Could not parse ID from URL: {entry.get('url')}")
                    continue

                detail_cache_key = f'pokeapi_detail_{pokemon_id}'
                cached_detail = cache.get(detail_cache_key)

                if cached_detail:
                    # print(f"  Serving detail {pokemon_id} from cache")
                    detailed_pokemon_list.append(cached_detail)
                else:
                     print(f"  Fetching detail {pokemon_id} from PokeAPI for list page")
                     try:
                        detail_response = requests.get(entry['url'])
                        detail_response.raise_for_status()
                        detail_data = detail_response.json()
                        processed_detail_data = {
                            'id': detail_data.get('id'), 'name': detail_data.get('name'),
                            'height': detail_data.get('height'), 'weight': detail_data.get('weight'),
                            # Procesar la lista 'types', asegurando que data.get('types') no sea None
                            'types': [t['type']['name'] for t in detail_data.get('types', [])] if detail_data.get('types') is not None else [],
                             # Procesar sprite anidado, asegurando que data.get('sprites') no sea None
                            'front_default_sprite': detail_data.get('sprites', {}).get('front_default'),
                            # Procesa aquí otros campos que hayas definido en tu Serializer
                        }
                        detailed_pokemon_list.append(processed_detail_data)
                        cache.set(detail_cache_key, processed_detail_data, timeout=CACHE_TTL)
                        # print(f"  Cached detail {pokemon_id}")

                     except requests.exceptions.RequestException as detail_e:
                         print(f"Error fetching detail {pokemon_id} for list: {detail_e}")
                         detailed_pokemon_list.append({'id': pokemon_id, 'name': entry.get('name', 'Unknown'), 'error': 'Details unavailable'})
                     except Exception as process_e:
                          print(f"Error processing detail {pokemon_id} for list: {process_e}")
                          detailed_pokemon_list.append({'id': pokemon_id, 'name': entry.get('name', 'Unknown'), 'error': 'Details processing failed'})
                 # --- Fin de la lógica de detalle individual ---


            # --- 7. Generar la Respuesta Paginada Final ---
            # El objeto paginador (`paginator`) ya tiene el conteo total, la solicitud, la vista,
            # y el estado de la página actual (`paginator.page`) configurados desde el paso 2.
            # Llamamos a get_paginated_response con los *datos procesados reales* para esta página.
            response_data = paginator.get_paginated_response(detailed_pokemon_list).data


            # --- 8. Cachear la Respuesta Final Formateada ---
            # Cacheamos la respuesta completa y formateada para esta página específica (offset/limit)
            cache.set(cache_key, response_data, timeout=CACHE_TTL)
            print(f"Cached formatted list response with key: {cache_key}")

            # --- 9. Retornar la Respuesta ---
            return Response(response_data)


        except requests.exceptions.RequestException as e:
            print(f"Error fetching list page data from PokeAPI: {e}")
            # Si la PokeAPI devuelve un error (ej: 404, 500)
            status_code = e.response.status_code if e.response is not None else status.HTTP_503_SERVICE_UNAVAILABLE
            return Response(
                {"error": f"Could not fetch list data from external API: {e}"},
                status=status_code
            )
        except Exception as e:
            print(f"An unexpected error occurred in list view: {e}")
            traceback.print_exc() # Imprime la traza completa para depuración en la consola del servidor
            return Response(
                {"error": f"An internal error occurred: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # --- Método retrieve (Probablemente no necesite cambios si el de arriba funciona) ---
    def retrieve(self, request, pk=None):
        """
        Recupera detalles para un solo Pokémon por ID, obteniendo de PokeAPI (con cache).
        """
        # Validar que pk es proporcionado y es un número entero
        if pk is None:
             return Response(
                {"detail": "Pokémon ID not provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            pokemon_id = int(pk)
        except ValueError:
             return Response(
                {"detail": f"Invalid Pokémon ID format: '{pk}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- 1. Buscar en Cache o Fetch de PokeAPI ---
        cache_key = f'pokeapi_detail_{pokemon_id}' # Clave de cache para el detalle individual
        cached_data = cache.get(cache_key)

        if cached_data:
            print(f"Serving detail {pokemon_id} from cache")
            # Cache hit: Servir los datos procesados que estaban en cache
            serializer = PokemonSerializer(cached_data) # Serializar los datos procesados
            return Response(serializer.data)

        print(f"Fetching detail {pokemon_id} from PokeAPI: {POKEAPI_BASE_URL}pokemon/{pokemon_id}/")

        try:
            # Paso A: Fetch data from PokeAPI for the specific ID
            response = requests.get(f"{POKEAPI_BASE_URL}pokemon/{pokemon_id}/")
            response.raise_for_status() # Lanza excepción para 404, 500, etc.
            data = response.json() # Esto es el diccionario con los datos del Pokémon

            # Paso B: Procesar los datos para que coincidan con tu Serializer
            processed_data = {
                'id': data.get('id'),
                'name': data.get('name'),
                'height': data.get('height'),
                'weight': data.get('weight'),
                 # Procesar la lista 'types', asegurando que data.get('types') no sea None
                'types': [t['type']['name'] for t in data.get('types', [])] if data.get('types') is not None else [],
                 # Procesar sprite anidado, asegurando que data.get('sprites') no sea None
                'front_default_sprite': data.get('sprites', {}).get('front_default'),
                # Procesa aquí otros campos que hayas definido en tu Serializer
            }

            # Paso C: Guardar en cache los datos procesados
            cache.set(cache_key, processed_data, timeout=CACHE_TTL)
            print(f"Cached detail data with key: {cache_key}")

            # Paso D: Serializar y retornar los datos procesados
            serializer = PokemonSerializer(processed_data)
            return Response(serializer.data)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching detail for ID {pokemon_id} from PokeAPI: {e}")
            # Si la PokeAPI devuelve un 404 para este ID
            if e.response and e.response.status_code == 404:
                 return Response(
                    {"detail": f"Pokémon with ID {pokemon_id} not found in external API."},
                    status=status.HTTP_404_NOT_FOUND
                )
            # Otros errores de la API externa
            status_code = e.response.status_code if e.response is not None else status.HTTP_503_SERVICE_UNAVAILABLE
            return Response(
                {"error": f"Could not fetch detail data for {pokemon_id} from external API: {e}"},
                status=status_code
            )
        except Exception as e:
            print(f"An unexpected error occurred in retrieve view: {e}")
            traceback.print_exc()
            return Response(
                {"error": f"An internal error occurred: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # --- Implementación de Búsqueda (Opcional y Compleja) ---
    # La búsqueda directa contra PokeAPI sin un endpoint de búsqueda dedicado es difícil.
    # Si la necesitas, requerirá una estrategia como la descrita antes (obtener todos/muchos nombres y filtrar).
    # @action(detail=False, methods=['get'])
    # def search(self, request):
    #     ... (implementación de búsqueda) ...
    #     pass # Elimina o implementa si la necesitas