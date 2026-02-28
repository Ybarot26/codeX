from rest_framework import serializers

from security.models import StoreAuthTokens


class StoreAuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreAuthTokens
        fields = "__all__"
