from rest_framework import serializers

from reviews.models import Category, Genre, Title
from reviews.utils import check_year_availability


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Категория."""
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Жанр."""
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Произведение."""
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['genre'] = GenreSerializer(
            instance.genre.all(), many=True
        ).data
        representation['category'] = CategorySerializer(instance.category).data
        return representation

    def validate(self, attrs):
        year = attrs.get('year')
        check_year_availability(year)
        return attrs
