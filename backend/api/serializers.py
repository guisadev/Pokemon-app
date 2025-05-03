# api/serializers.py

from rest_framework import serializers

class PokemonSerializer(serializers.Serializer):
    # Define los campos que esperas y quieres exponer desde los datos de PokeAPI
    # Asegúrate de que estos campos existan en los diccionarios que procesas en views.py
    id = serializers.IntegerField()
    name = serializers.CharField()
    height = serializers.IntegerField(required=False, allow_null=True) # Algunos campos pueden ser opcionales
    weight = serializers.IntegerField(required=False, allow_null=True)
    # Asumiendo que procesas los tipos a una lista de strings en la vista
    types = serializers.ListField(child=serializers.CharField())
    # Asumiendo que procesas el sprite a una URL directa en la vista
    front_default_sprite = serializers.URLField(required=False, allow_null=True)

    # Añade más campos según los detalles que extraigas de la PokeAPI
    # stats = serializers.ListField(...) # Ejemplo si serializas stats
    # abilities = serializers.ListField(...) # Ejemplo si serializas abilities

    # Si necesitas extraer datos anidados o procesarlos de forma compleja:
    # Por ejemplo, si quisieras acceder a sprites.other."official-artwork".front_default
    # official_artwork_sprite = serializers.SerializerMethodField()
    # def get_official_artwork_sprite(self, obj):
    #    sprites = obj.get('sprites', {})
    #    other = sprites.get('other', {})
    #    official_artwork = other.get('official-artwork', {})
    #    return official_artwork.get('front_default')