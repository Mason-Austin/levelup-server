from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event
from ..models import Gamer, Game

class EventView(ViewSet):
    """Level up Event view"""
    
    def retrieve(self, request, pk):
        """Handle GET requests for single game type

        Returns:
            Response -- JSON serialized game type
        """
        try:
          event = Event.objects.get(pk=pk)
          serializer = EventSerializer(event)
          return Response(serializer.data)
        except Event.DoesNotExist as ex:
          return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
    def list(self, request):
        """Handle GET requests for single game type

        Returns:
            Response -- JSON serialized game type
        """
        events = Event.objects.all()
        game = request.query_params.get('game', None)
        if game is not None:
            events = events.filter(game_id=game)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """Handle POST operations

        Returns
            Response -- JSON serialized game instance
        """
        organizer = Gamer.objects.get(uid=request.data["userId"])
        game = Game.objects.get(pk=request.data["gameId"])

        event = Event.objects.create(
            description=request.data["description"],
            date=request.data["date"],
            time=request.data["time"],
            game=game,
            organizer=organizer,
        )
        serializer = EventSerializer(event)
        return Response(serializer.data)

class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events"""
    class Meta:
        model = Event
        fields = ("id", "game", "description", "date", "time", "organizer")
        depth = 2
