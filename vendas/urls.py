from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('produto/add/', views.ProdutoCreateView.as_view(), name='produto-add'),
    path('fabricante/add/', views.FabricanteCreateView.as_view(), name='fabricante-add'),
    path('grupo/add/', views.GrupoCreateView.as_view(), name='grupo-add'),
    path('subgrupo/add/', views.SubGrupoCreateView.as_view(), name='subgrupo-add'),
    path('venda/add/', views.VendaCreateView.as_view(), name='venda-add'),
    path('produtos/', views.lista_produtos, name='lista_produtos'),
    path('visualizar_vendas/', views.visualizar_vendas, name='visualizar_vendas'),
]
