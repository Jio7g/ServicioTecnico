from django.urls import path

from . import views

app_name = "reportes"

urlpatterns = [
    path("", views.ReporteListView.as_view(), name="lista"),
    path("nuevo/", views.ReporteCreateView.as_view(), name="nuevo"),
    path("<int:pk>/", views.ReporteDetailView.as_view(), name="detalle"),
    path("<int:pk>/editar/", views.ReporteUpdateView.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.ReporteDeleteView.as_view(), name="eliminar"),
]
