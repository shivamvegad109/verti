from django.urls import path
from .views import *

urlpatterns = [
    path('register/',RegisterView.as_view()),
    path("user/<uuid:id>/",UpdateView.as_view()),
    path("user/",UpdateView.as_view()),
    path("get-all/",GetAllCreateView.as_view()),
    path("entity-instance/<slug>/",CreatEntityInstanceView.as_view()),
    path("entity-instance/<slug>/<uuid:id>/",UpdateEntityInstanceView.as_view())
]
