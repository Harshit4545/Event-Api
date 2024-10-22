from django.urls import path
from .views import RegisterView, EventListCreateView, TicketPurchaseView ,TopEventsView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/<int:event_id>/purchase/', TicketPurchaseView.as_view(), name='ticket-purchase'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('top-events/', TopEventsView.as_view(), name='top-events'),  # New URL for top events

]