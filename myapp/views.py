from rest_framework.response import Response
from rest_framework import status
from .serializers import EntityInstanceUpdateSerializer
from .models import EntityInstance, EntityInstanceMeta, User
from django.shortcuts import render
from rest_framework import generics, status
from .serializers import *
from rest_framework.response import Response
from django.utils import timezone
from .validators import *

class RegisterView(generics.GenericAPIView):
    serializer_class = UserSerializer
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        message = ('Register SuccessFully')
        return Response({'message':message,'data':serializer.data})
    
    def patch(self, request):
        # serializer = UserSerializer(data=request.data)
        try:
            obj = User.objects.get(name=request.data.get("name"))
        
        except User.DoesNotExist:
            msg = {"msg":"Not found error"}
            
            return Response(msg,status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(obj,data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            obj.modifield_on = timezone.now()
            obj.save()
            return Response(serializer.data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.error,status=status.HTTP_400_BAD_REQUEST)
    
    
class UpdateView(generics.GenericAPIView):
    serializer_class = UserSerializer
    
    def delete(self,request,id):
        try:
            obj = User.objects.get(id=id)
            obj.is_enabled = False
            obj.is_deleted = True
            obj.save()
        except User.DoesNotExist:
            msg = {"msg":not "found"}
            return Response(msg,status=status.HTTP_404_NOT_FOUND)
        return Response({"msg":"deleted"}, status=status.HTTP_204_NO_CONTENT)

class CreatEntityInstanceView(generics.CreateAPIView):
    def post(self, request, slug):
        try:
            entity_instance_id = []
            obj = User.objects.get(slug=slug)
            entity_instance = EntityInstance.objects.filter(entity_id = obj.pk)
            for instance in entity_instance:
                entity_instance_id.append(instance.pk)
            # entity = EntityInstance.objects.get(entity=entity)
            schema = obj.schema
            validator = EntityPayloadValidators().validate_payload(request,schema,entity_instance_id)
            entity_instance_serializer =EntityInstanceCreateSerializer(
                data = {"request":request,"entity":obj.pk},
                context = {"request":request,"entity":obj}
            )
            if entity_instance_serializer.is_valid(raise_exception=True):
                entity_instance_serializer.save()
                entity_instance_meta = []
                entity_instance_obj = entity_instance_serializer.data
                for entity_meta in validator:
                    entity_meta["entity_Instance_id"] = entity_instance_obj.get("id")
                    entity_instance_meta.append(EntityInstanceMeta(**entity_meta))
                EntityInstanceMeta.objects.bulk_create(entity_instance_meta)

            entity = UserSerializer(obj).data
            response_paylod = {
                                "Entity":entity,
                                "Entity_Instance":validator
                            }
            return Response(
                            response_paylod,
                            status=status.HTTP_200_OK
                        )
        except User.DoesNotExist:

            msg = {"error": {"ref": "INVALID ENTITY ID", "message": "Invalid entity slug supplied"}}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

class GetAllCreateView(generics.GenericAPIView):
    def get(self,requ):
        data = User.objects.all().values()
        data = data.filter(is_deleted = False,is_enabled = True)
        return Response(data,status=status.HTTP_200_OK)

class UpdateEntityInstanceView(generics.GenericAPIView):

    # Data update by PUT
    def put(self, request, slug, id):
        try:
            entity_instance_id = []
            obj = User.objects.get(slug=slug)
            entity_instance = EntityInstance.objects.filter(entity_id = obj.pk)
            for instance in entity_instance:
                entity_instance_id.append(instance.pk)
            schema = obj.schema
            validator = EntityPayloadValidators().validate_payload(request,schema,entity_instance_id)
            entity_instance_get = EntityInstance.objects.get(pk= id)

            entity_instance_serializer =EntityInstanceUpdateSerializer(
                instance=entity_instance_get.pk,
                data = {"request":request,"entity":obj.pk}
            )
            if entity_instance_serializer.is_valid(raise_exception=True):
                entity_instance_obj = entity_instance_serializer.data
    
    
                for entity_meta in validator:
                    entity_meta["entity_Instance_id"] = entity_instance_get.pk
                    EntityInstanceMeta.objects.update_or_create( 
                        entity_Instance_id = entity_instance_get.pk,
                        meta_key = entity_meta.get("meta_key"),
                        defaults= entity_meta
                    )
                data = User.objects.all().values()
                data = data.filter(is_deleted = False,is_enabled = True)
                context = {
                    "ref":"Entity_instance_updatesucessfully",
                    "message": data,
                    "data": validator
                }
                return Response(context)
        except User.DoesNotExist:
            msg = {"message": "User Not Found"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        except EntityInstanceMeta.DoesNotExist:
            msg = {"message": "Entity Instance Meta Not Found"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
    
    # Data update by PATCH    
    def patch(self, request, slug, id):
        try:
            entity_instance_id = []
            obj = User.objects.get(slug=slug)
            entity_instance = EntityInstance.objects.filter(entity_id=obj.pk)
            for instance in entity_instance:
                entity_instance_id.append(instance.pk)
            schema = obj.schema
            validator = EntityPayloadValidators().validate_payload(request, schema, entity_instance_id)
            entity_instance_get = EntityInstance.objects.get(pk=id)

            entity_instance_serializer = EntityInstanceUpdateSerializer(
                instance=entity_instance_get,
                data={"request": request, "entity": obj.pk},
                partial=True
            )
            if entity_instance_serializer.is_valid(raise_exception=True):
                entity_instance_obj = entity_instance_serializer.save()

                for entity_meta in validator:
                    entity_meta["entity_Instance_id"] = entity_instance_get.pk
                    EntityInstanceMeta.objects.update_or_create(
                        entity_Instance_id=entity_instance_get.pk,
                        meta_key=entity_meta.get("meta_key"),
                        defaults=entity_meta
                    )
                data = User.objects.all().values()
                data = data.filter(is_deleted = False,is_enabled = True)
                # return Response(data,status=status.HTTP_200_OK)
                context = {
                    "ref": "Entity_instance_updated_successfully",
                    "message": data,
                    "data": entity_meta
                }
                return Response(context)
        except User.DoesNotExist:
            msg = {"message": "User Not Found"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        except EntityInstance.DoesNotExist:
            msg = {"message": "Entity Instance Not Found"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        except EntityInstanceMeta.DoesNotExist:
            msg = {"message": "Entity Instance Meta Not Found"}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
    
    # Data Delete 
    def delete(self, request, slug, id):
        try:
            obj = User.objects.get(slug=slug)
            entity_instance = EntityInstance.objects.filter(entity_id=obj.pk)
            
        except User.DoesNotExist:
            msg = {"msg":not "found"}
            return Response(msg,status=status.HTTP_404_NOT_FOUND)
        
        entity_instance.delete()
        context = {
                    "Message": "Data_deleted_successfully"
                }
        return Response(context, status=status.HTTP_204_NO_CONTENT)
            