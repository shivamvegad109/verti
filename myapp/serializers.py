from rest_framework import serializers
from django.db import transaction

from entity.validators import EntityPayloadValidators
from .models import *
import time

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','name', 'slug', 'schema']
        
class EntityInstanceMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityInstanceMeta
        # fields = ['id', 'meta_key']
        fields = '__all__'
        
class EntityInstanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityInstance
        fields = ["id",'entity','is_deleted']
    
    def create(self, validated_data):
        validated_data["entity"] = self.context.get("entity")
        entity_instance_obj = EntityInstance.objects.create(**validated_data)
        return entity_instance_obj


class EntityInstanceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityInstance
        exclude = ['entity',"is_deleted", "created_on", "modifield_on"]

    # def update(self, instance, validated_data):
    #     payload_validators = EntityPayloadValidators()
    #     updated_fields = payload_validators.validate_payload(self.context.get('request'), instance.entity.schema)

    #     if updated_fields:
    #         for field in updated_fields:
    #             meta_key = field['meta_key']
    #             field_value = field[meta_key]
    #             setattr(instance, meta_key, field_value)
    #         instance.save()
    #     return instance









# class EntityInstanceUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = EntityInstance
#         fields = '__all__'
    
#     @transaction.atomic
#     def update(self, instance, validated_data):
#         print(validated_data)
#         time.sleep(10101010)
#         validated_data["modifield_on"] = time.time()
#         entity_instance_obj , created = EntityInstance.objects.update_or_create(
#             id = instance.id,defaults=validated_data
#         )
#         return entity_instance_obj