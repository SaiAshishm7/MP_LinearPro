
from django.urls import path
from .views import OptimizationView

urlpatterns = [
    path('', OptimizationView.as_view(), name='optimize'),
]
