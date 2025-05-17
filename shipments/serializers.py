from rest_framework import serializers
from .models import Shipment, Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class ShipmentSerializer(serializers.ModelSerializer):
    articles = ArticleSerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = '__all__'
