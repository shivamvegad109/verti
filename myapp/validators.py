from rest_framework.exceptions import APIException
from rest_framework import status
from django.core.validators import validate_email
from .models import *
import re
from datetime import datetime


class EntityPayloadValidators:
    def validate_payload(self, request, schema, entity_instance_id =None):
        process_meta = {}
        process_paylod = []
        payload = request.data
        request_type = (
            request.method if request.method == "PATCH" else None
        )

        for group in schema["field_groups"]:
            for field in group["fields"]:
                field_slug = field.get("slug")
                field_value = payload.get(field_slug)
                field_type = field.get("type", None)
                required_field = field.get("is_required", False)

            
                if required_field and field_slug not in request.data and request_type is None:
                    raise APIException(
                        {
                            "error": {
                                "ref": "MISSING_REQUIRED_FIELD",
                                "message": f"Missing required field: {field.get('slug')}",
                            }
                        }
                    )

                # Use Case : DATA_TYPE -> TEXT or TEXT_AREA
                if field_type in ["TEXT", "TEXT_AREA"] and (
                    (request_type is None) or (request_type is not None and payload.get(field_slug))
                ):
                    max_length = field.get("max_length", None)
                    if (
                        (field_value is not None)
                        and (max_length is not None)
                        and (len(field_value) > max_length)
                    ):
                        raise APIException(
                            {
                                "error": {
                                    "ref": "TOO_SHORT_FIELD_VALUE",
                                    "message": f"too short value supplied for the field: {field_slug}",
                                }
                            }
                        )
                    min_length = field.get("min_length", None)
                    if (
                        (field_value is not None)
                        and (min_length is not None)
                        and (len(field_value) < min_length)
                    ):
                        raise APIException(
                            {
                                "error": {
                                    "ref": "TOO_SHORT_FIELD_VALUE",
                                    "message": f"too short value supplied for the field: {field_slug}",
                                }
                            }
                        )
                    # and (len(field_value) < min_length)
                    if (type(field_value) is not str) and (required_field == True):
                        raise APIException(
                            {
                                "error": {
                                    "ref": "INVALID_FIELD_VALUE_TYPE",
                                    "message": f"invalid field value type: {field.get('slug')} -> {field_value}",
                                }
                            }
                        )
                    process_meta = {"meta_key": field_slug, "val_string": field_value}
                    
                    
                # Use Case : DATA_TYPE -> INTEGER
                if field_type in ["INTEGER"] and (
                    (request_type is None) or (request_type is not None and payload.get(field_slug))
                ):
                    if (type(field_value) is not int) and required_field == True:
                        raise APIException(
                            {
                                "error": {
                                    "ref": "INVALID_FIELD_VALUE_TYPE",
                                    "message": f"invalid field value type: {field.get('slug')} -> {field_value}",
                                }
                            }
                        )
                    process_meta = {"meta_key": field_slug, "val_integer": field_value}
                    
                # Use Case : DATA_TYPE -> FLOAT
                if field_type in ["FLOAT"] and (
                    (request_type is None) or (request_type is not None and payload.get(field_slug))
                ):
                    if (type(field_value) is not float) and required_field == True:
                        raise APIException(
                            {
                                "error": {
                                    "ref": "INVALID_FIELD_VALUE_TYPE",
                                    "message": f"invalid field value type: {field.get('slug')} -> {field_value}",
                                }
                            }
                        )
                    process_meta = {"meta_key": field_slug, "val_decimal": field_value}

                # Use Case : DATA_TYPE -> EMAIL
                if field_type in ["EMAIL"] and (
                    (request_type is None) or (request_type is not None and payload.get(field_slug))
                ):
                    try:
                        validate_email(field_value)
                    except:
                        raise APIException(
                            {
                                "error": {
                                    "ref": "INVALID_FIELD_VALUE_TYPE",
                                    "message": f"invalid field value type: {field.get('slug')} -> {field_value}",
                                }
                            }
                        )
                    process_meta = {"meta_key": field_slug, "val_text": field_value}
                    
                # Use Case : DATA_TYPE -> DATE
                if field_type in ["DATE"]and (
                    (request_type is None) or (request_type is not None and payload.get(field_slug))
                ):
                    formate = "%Y-%m-%d"
                    try:
                        datetime.strptime(field_value, formate)
                    except:
                        raise APIException(
                            {
                                "error": {
                                    "ref": "INVALID_FIELD_VALUE_TYPE",
                                    "message": f"invalid field value type: {field.get('slug')} -> {field_value}",
                                }
                            }
                        )
                    process_meta = {"meta_key": field_slug, "val_date": field_value}

                # Use Case : DATA_TYPE -> TIME
                if field_type in ["TIME"]and (
                    (request_type is None) or (request_type is not None and payload.get(field_slug))
                ):
                    try:
                        datetime.strptime(field_value, "%H:%M:%S")
                    except:
                        raise APIException(
                            {
                                "error": {
                                    "ref": "INVALID_FIELD_VALUE_TYPE",
                                    "message": f"invalid field value type: {field.get('slug')} -> {field_value}",
                                }
                            }
                        )
                    process_meta = {"meta_key": field_slug, "val_time": field_value}

                # Use Case : DATA_TYPE -> DATE_TIME
                if field_type in ["DATE_TIME"]and (
                    (request_type is None) or (request_type is not None and payload.get(field_slug))
                ):
                    formate1 = "%Y-%m-%d T%H:%M:%S"
                    formate2 = "%Y-%m-%d %H:%M:%S"
                    try:
                        datetime.strptime(
                            field_value,
                            formate1 if len(field_value.split("T")) == 2 else formate2,
                        )
                    except Exception as e:
                        raise APIException(
                            {
                                "error": {
                                    "ref": "INVALID_FIELD_VALUE_TYPE",
                                    "message": f"invalid field value type: {field.get('slug')} -> {field_value}",
                                },
                                "ee": f"{e}",
                            }
                        )
                    process_meta = {
                        "meta_key": field_slug,
                        "val_date_time": field_value,
                    }
                process_paylod.append(process_meta)
                
                if field.get("is_unique") and (
                    (request_type is None) or (request_type is not None and payload.get(field_slug))
                ):
                    duplicate_records = EntityInstanceMeta.objects.filter(
                        **process_meta,entity_Instance_id__in=entity_instance_id
                    )
                    if len(duplicate_records) != 0:
                        raise APIException(
                            {
                                "error": {
                                    "ref": "DUPLICATE_FIELD_VALUE",
                                    "message": f"Duplicate value supplied for unique field: {field_slug}.{field_value}",
                                }
                            }
                        )
        return process_paylod
    
    
# class EntityPatchPayloadValidators:
#     def validate_payload(self, request, schema, entity_instance_id=None):
#         process_meta = {}
#         process_paylod = []
#         payload = request.data

#         for group in schema["field_groups"]:
#             for field in group["fields"]:
#                 field_slug = field.get("slug")
#                 field_value = payload.get(field_slug)
#                 field_type = field.get("type", None)
#                 required_field = field.get("is_required", False)

#                 if field_value is not None:
#                     if field_type in ["TEXT", "TEXT_AREA"]:
#                         max_length = field.get("max_length", None)
#                         if max_length is not None and len(field_value) > max_length:
#                             raise APIException(
#                                 {
#                                     "error": {
#                                         "ref": "TOO_SHORT_FIELD_VALUE",
#                                         "message": f"Too short value supplied for the field: {field_slug}",
#                                     }
#                                 }
#                             )
#                         min_length = field.get("min_length", None)
#                         if min_length is not None and len(field_value) < min_length:
#                             raise APIException(
#                                 {
#                                     "error": {
#                                         "ref": "TOO_SHORT_FIELD_VALUE",
#                                         "message": f"Too short value supplied for the field: {field_slug}",
#                                     }
#                                 }
#                             )
#                         if type(field_value) is not str and required_field:
#                             raise APIException(
#                                 {
#                                     "error": {
#                                         "ref": "INVALID_FIELD_VALUE_TYPE",
#                                         "message": f"Invalid field value type: {field_slug} -> {field_value}",
#                                     }
#                                 }
#                             )
#                         process_meta = {"meta_key": field_slug, "val_string": field_value}
#                     elif field_type in ["INTEGER"]:
#                         if type(field_value) is not int and required_field:
#                             raise APIException(
#                                 {
#                                     "error": {
#                                         "ref": "INVALID_FIELD_VALUE_TYPE",
#                                         "message": f"Invalid field value type: {field_slug} -> {field_value}",
#                                     }
#                                 }
#                             )
#                         process_meta = {"meta_key": field_slug, "val_integer": field_value}
#                     elif field_type in ["FLOAT"]:
#                         if type(field_value) is not float and required_field:
#                             raise APIException(
#                                 {
#                                     "error": {
#                                         "ref": "INVALID_FIELD_VALUE_TYPE",
#                                         "message": f"Invalid field value type: {field_slug} -> {field_value}",
#                                     }
#                                 }
#                             )
#                         process_meta = {"meta_key": field_slug, "val_decimal": field_value}
#                     elif field_type in ["EMAIL"]:
#                         try:
#                             validate_email(field_value)
#                         except:
#                             raise APIException(
#                                 {
#                                     "error": {
#                                         "ref": "INVALID_FIELD_VALUE_TYPE",
#                                         "message": f"Invalid field value type: {field_slug} -> {field_value}",
#                                     }
#                                 }
#                             )
#                         process_meta = {"meta_key": field_slug, "val_text": field_value}
#                     elif field_type in ["DATE"]:
#                         format = "%Y-%m-%d"
#                         try:
#                             datetime.strptime(field_value, format)
#                         except:
#                             raise APIException(
#                                 {
#                                     "error": {
#                                         "ref": "INVALID_FIELD_VALUE_TYPE",
#                                         "message": f"Invalid field value type: {field_slug} -> {field_value}",
#                                     }
#                                 }
#                             )
#                         process_meta = {"meta_key": field_slug, "val_date": field_value}
#                     elif field_type in ["TIME"]:
#                         try:
#                             datetime.strptime(field_value, "%H:%M:%S")
#                         except:
#                             raise APIException(
#                                 {
#                                     "error": {
#                                         "ref": "INVALID_FIELD_VALUE_TYPE",
#                                         "message": f"Invalid field value type: {field_slug} -> {field_value}",
#                                     }
#                                 }
#                             )
#                         process_meta = {"meta_key": field_slug, "val_time": field_value}
#                     elif field_type in ["DATE_TIME"]:
#                         format1 = "%Y-%m-%d T%H:%M:%S"
#                         format2 = "%Y-%m-%d %H:%M:%S"
#                         try:
#                             datetime.strptime(
#                                 field_value,
#                                 format1 if len(field_value.split("T")) == 2 else format2,
#                             )
#                         except Exception as e:
#                             raise APIException(
#                                 {
#                                     "error": {
#                                         "ref": "INVALID_FIELD_VALUE_TYPE",
#                                         "message": f"Invalid field value type: {field_slug} -> {field_value}",
#                                     },
#                                     "ee": f"{e}",
#                                 }
#                             )
#                         process_meta = {
#                             "meta_key": field_slug,
#                             "val_date_time": field_value,
#                         }
#                     process_paylod.append(process_meta)

#                     if field.get("is_unique"):
#                         duplicate_records = EntityInstanceMeta.objects.filter(
#                             **process_meta, entity_Instance_id__in=entity_instance_id
#                         )
#                         if len(duplicate_records) != 0:
#                             raise APIException(
#                                 {
#                                     "error": {
#                                         "ref": "DUPLICATE_FIELD_VALUE",
#                                         "message": f"Duplicate value supplied for unique field: {field_slug}.{field_value}",
#                                     }
#                                 }
#                             )
        
#         if len(process_paylod) == 0:
#             raise APIException(
#                 {
#                     "error": {
#                         "ref": "MISSING_REQUIRED_FIELD",
#                         "message": "Missing required field",
#                     }
#                 }
#             )

#         return process_paylod

