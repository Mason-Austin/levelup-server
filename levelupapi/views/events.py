from django.http import HttpResponseServerError
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event
from ..models import Gamer, Game, EventGamer

class EventView(ViewSet):
    """Level up Event view"""
    
    @action(methods=['post'], detail=True)
    def signup(self, request, pk):
        """Post request for a user to sign up for an event"""
        uid = request.META['HTTP_AUTHORIZATION']
        gamer = Gamer.objects.get(uid=uid)
        event = Event.objects.get(pk=pk)
        attendee = EventGamer.objects.create(
            gamer=gamer,
            event=event
        )
        return Response({'message': 'Gamer added'}, status=status.HTTP_201_CREATED)
    
    @action(methods=['delete'], detail=True)
    def leave(self, request, pk):
        """Delete a user from an event"""
        uid = request.META['HTTP_AUTHORIZATION']
        gamer = Gamer.objects.get(uid=uid)
        event = Event.objects.get(pk=pk)
        event_gamer = EventGamer.objects.get(gamer=gamer, event=event)
        event_gamer.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    def retrieve(self, request, pk):
        """Handle GET requests for single event

        Returns:
            Response -- JSON serialized event
        """
        try:
          event = Event.objects.get(pk=pk)
          serializer = EventSerializer(event)
          return Response(serializer.data)
        except Event.DoesNotExist as ex:
          return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
      
    def list(self, request):
        """Handle GET requests for all events

        Returns:
            Response -- JSON serialized event type
        """
        events = Event.objects.all()
        game = request.query_params.get('game', None)
        if game is not None:
            events = events.filter(game_id=game)
        uid = request.META['HTTP_AUTHORIZATION']
        gamer = Gamer.objects.get(uid=uid)

        for event in events:
        # Check to see if there is a row in the Event Games table that has the passed in gamer and event
            event.joined = len(EventGamer.objects.filter(
            gamer=gamer, event=event)) > 0

        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """Handle POST operations

        Returns
            Response -- JSON serialized event instance
        """
        organizer = Gamer.objects.get(id=request.data["userId"])
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
    
    def update(self, request, pk):
        """Handle PUT requests for a event

        Returns:
            Response -- Empty body with 204 status code
        """

        event = Event.objects.get(pk=pk)
        event.description = request.data["description"]
        event.date = request.data["date"]
        event.time = request.data["time"]

        organizer = Gamer.objects.get(pk=request.data["userId"])
        event.organizer = organizer
        game = Game.objects.get(pk=request.data["gameId"])
        event.game = game
        event.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk):
        event = Event.objects.get(pk=pk)
        event.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    

class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events"""
    class Meta:
        model = Event
        fields = ("id", "game", "description", "date", "time", "organizer", "joined")
        depth = 2
