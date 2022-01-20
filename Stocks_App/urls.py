from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('Query_Results/', views.Query_Results, name='Query_Results'),
    path('Add_Transactions/', views.Add_Transactions, name='Add_Transaction'),
    path('Buy_Stocks/', views.Buy_Stocks, name='Buy_Stocks')
    ]