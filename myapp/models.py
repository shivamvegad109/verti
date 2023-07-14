from django.db import models
import uuid
from unixtimestampfield.fields import UnixTimeStampField
from django.utils import timezone

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True)
    slug = models.CharField(unique=True,max_length=256)
    schema = models.JSONField()
    is_enabled = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_on = UnixTimeStampField(default=timezone.now)
    modifield_on = UnixTimeStampField(default=timezone.now)


class EntityInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity = models.ForeignKey(User, related_name="entity_instant",on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_on = UnixTimeStampField(default=timezone.now)
    modifield_on = UnixTimeStampField(default=timezone.now)
    
class   EntityInstanceMeta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_Instance = models.ForeignKey(EntityInstance, related_name="entity_instant_meta",on_delete=models.CASCADE)
    meta_key = models.CharField(null=True)
    val_integer = models.BigIntegerField(blank=True,null=True)
    val_decimal = models.FloatField(blank=True,null=True)
    val_string = models.CharField(max_length=256,blank=True,null=True)
    val_date = models.DateField(blank=True,null=True)
    val_time = models.TimeField(blank=True,null=True)
    val_date_time = models.DateTimeField(blank=True,null=True)
    val_text = models.TextField(blank=True,null=True)
    val_json = models.JSONField(blank=True,null=True)
    addon_data = models.JSONField(blank=True,null=True)
    create_on = UnixTimeStampField(default=timezone.now)
    modifield_on = UnixTimeStampField(default=timezone.now)     