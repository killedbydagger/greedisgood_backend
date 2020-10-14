from django.db import models

# Create your models here.


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    email = models.CharField(unique=True, max_length=50)
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True)
    token = models.CharField(max_length=20, default="greedisgood")
    point = models.IntegerField()
    repetitive_login = models.IntegerField()

    class Meta:
        db_table = 'user'


class Item(BaseModel):
    name = models.CharField(max_length=100)
    image_url = models.CharField(max_length=255)
    rarity = models.IntegerField()

    class Meta:
        db_table = 'item'


class UserInventory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_inventory'


class Game(BaseModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = 'game'


class GameReward(BaseModel):
    game = models.ForeignKey(Game, on_delete=models.DO_NOTHING)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        db_table = 'gamereward'


class DailyLogin(BaseModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'dailylogin'


class DailyLoginReward(BaseModel):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        db_table = 'dailyloginreward'


class Probability(BaseModel):
    rarity = models.IntegerField()
    chance = models.IntegerField()

    class Meta:
        db_table = 'probability'
