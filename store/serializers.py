from rest_framework import serializers

from store.models import Store


class StoreRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["store_id", "store_name", "store_address",
                  "store_email", "store_password"]
