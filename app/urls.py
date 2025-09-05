from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('alterar_senha/', views.alterar_senha_view, name='alterar_senha'),
    path('recuperar_senha/', views.recuperar_senha_view, name='recuperar_senha'),
    path('redefinir_senha/<str:token>/', views.redefinir_senha_view, name='redefinir_senha'),
    path('nota/<int:controle>/', views.visualizar_nota, name='visualizar_nota'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<int:user_id>/', views.excluir_usuario, name='excluir_usuario'),
]
