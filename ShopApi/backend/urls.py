from backend.views import RegisterAccount, LoginAccount, ContactView, AccountDetails, ShopView, CategoryView,\
    PartnerUpdate, ShopDetailsView, PartnerState, ProductInfoView, BasketView, OrderView, PartnerOrders

from django.urls import path

app_name = 'backend'

urlpatterns = [
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path('user/login', LoginAccount.as_view(), name='user-login'),

    #For any authorized user
    path('user/contact', ContactView.as_view(), name='user-contact'),
    path('user/details', AccountDetails.as_view(), name='user-details'),
    path('shops', ShopView.as_view(), name='shops'),
    path('categories', CategoryView.as_view(), name='categories'),
    path('products', ProductInfoView.as_view(), name='shops'),
    path('basket', BasketView.as_view(), name='basket'),
    path('order', OrderView.as_view(), name='order'),

    #Only for authorized shops
    path('partner/shop-details', ShopDetailsView.as_view(), name='partner-shop-details'),
    path('partner/state', PartnerState.as_view(), name='partner-state'),
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('partner/orders', PartnerOrders.as_view(), name='partner-orders'),
]