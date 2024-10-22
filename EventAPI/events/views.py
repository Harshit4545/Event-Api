from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import User, Event, Ticket
from .serializers import UserSerializer, EventSerializer, TicketSerializer
from django.db import transaction
from django.db import connection
from rest_framework.views import APIView


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'ADMIN'

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]
    



class TicketPurchaseView(generics.CreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        event_id = self.kwargs.get('event_id')
        quantity = request.data.get('quantity')

        try:
            event = Event.objects.select_for_update().get(id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        if event.tickets_sold + quantity > event.total_tickets:
            return Response({"error": "Not enough tickets available"}, status=status.HTTP_400_BAD_REQUEST)

        ticket = Ticket.objects.create(user=request.user, event=event, quantity=quantity)
        event.tickets_sold += quantity
        event.save()

        serializer = self.get_serializer(ticket)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class TopEventsView(APIView):

    def get(self, request):
        top_events = self.get_top_events()
        return Response(top_events)

    def get_top_events(self):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT e.id, e.name, e.date, e.total_tickets, e.tickets_sold
                FROM events_event e
                ORDER BY e.tickets_sold DESC
                LIMIT 3
            """)
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]    