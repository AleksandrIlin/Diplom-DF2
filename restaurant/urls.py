from django.urls import path
from restaurant.apps import RestaurantConfig
from restaurant.views import HomePageView, ContactsView, AboutRestaurantView, ReservationView, ConfirmReservationView, \
    CancelReservationView, ReservationUpdateView, ReservationListView, ReservationDetailView, ReservationDeleteView, \
    UpdateReservationStatusView

app_name = RestaurantConfig.name

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path('reservation/', ReservationView.as_view(), name='reservation'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('about_restaurant/', AboutRestaurantView.as_view(), name='about_restaurant'),
    path('confirm_reservation/<int:reservation_id>/', ConfirmReservationView.as_view(), name='confirm_reservation'),
    path('cancel_reservation/<int:pk>/', CancelReservationView.as_view(), name='cancel_reservation'),
    path("reservation/<int:pk>/update/", ReservationUpdateView.as_view(), name="reservation_update"),
    path('list/', ReservationListView.as_view(), name='reservation_list'),
    path('detail/<int:id>', ReservationDetailView.as_view(), name='reservation_detail'),
    path('delete/<int:pk>/', ReservationDeleteView.as_view(), name='reservation_delete'),
    path('update_status/<int:reservation_id>/', UpdateReservationStatusView.as_view(), name='update_status'),
]
