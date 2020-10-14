from rest_framework import serializers
from .models import User, Item, Game, GameReward, Probability, UserInventory


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = Item
		fields = '__all__'


class GameSerializer(serializers.ModelSerializer):
	class Meta:
		model = Game
		fields = '__all__'


class GameRewardSerializer(serializers.ModelSerializer):
	class Meta:
		model = GameReward
		fields = '__all__'


class ProbabilitySerializer(serializers.ModelSerializer):
	class Meta:
		model = Probability
		fields = '__all__'


class UserInventorySerializer(serializers.ModelSerializer):
	class Meta:
		model = UserInventory
		fields = '__all__'
