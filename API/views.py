from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from datetime import datetime,timezone
from .models import User, Item, Game, GameReward, Probability, UserInventory, DailyLogin
from .serializers import UserSerializer, ItemSerializer, GameSerializer, GameRewardSerializer, ProbabilitySerializer, UserInventorySerializer
from django.db.models import Q
import random
import string
import smtplib
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.http import HttpResponse
# Create your views here.

base_url = "http://25.22.20.44:8000"
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


@api_view(['POST'])
def register(request):
    body = json.loads(request.body.decode('utf-8'))
    jsonResponse = {}
    status = ""
    query = list(User.objects.filter(
        Q(email=body.get("email")) | Q(username=body.get("username"))
    ).values().all())
    print(query)
    if len(query) == 0:
        User.objects.create(
            email=body.get("email"),
            username=body.get("username"),
            password=body.get("password"),
            first_name=body.get("first_name"),
            last_name=body.get("last_name"),
            point=10000,
            repetitive_login=0,
            token=randomString(20)
        )
        user = User.objects.get(email=body.get("email"))
        serializer = UserSerializer(user, many=False)
        status = "Success"
        jsonResponse.update({
            "data": serializer.data,
        })
    else:
        if query[0]['email'] == body.get("email"):
            status = "Email already exist"
        else:
            status = "Username already exist"
    jsonResponse.update({
        "status": status
    })      
    return Response(jsonResponse)


@api_view(['POST'])
def login(request):
    body = json.loads(request.body.decode('utf-8'))
    jsonResponse = {}
    try:
        # Metadata for response
        metadata = {}
        # get time now
        now = datetime.now(timezone.utc)
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        # get user object
        user = User.objects.get(
            username=body.get("username"),
            password=body.get("password")
        )
        # check first login user on cache
        if body.get("username")+"firstlogin" in cache:
            # check daily login
            login_info = DailyLogin.objects.filter(user=user).latest('created_at')
            datediff = now.replace(hour=0, minute=0, second=0, microsecond=0) - login_info.created_at.replace(hour=0, minute=0, second=0, microsecond=0)
            day_diff = datediff.days
            if day_diff > 0:
                if day_diff == 1:
                    user.repetitive_login += 1
                elif day_diff > 1:
                    user.repetitive_login = 1
                user.point += 500
                user.save()
                metadata['dailylogin'] = "Yes"
        else:
            # set first login on cache
            cache.set(body.get("username")+"firstlogin", formatted_date, timeout=CACHE_TTL)
        # insert user login info
        DailyLogin.objects.create(user=user)
        # get user inventory
        items_owned = []
        inventory = UserInventory.objects.filter(user=user)
        for item in inventory:
            items_owned.append(item.item)
        metadata['user'] = UserSerializer(user, many=False).data
        metadata['inventory'] = ItemSerializer(items_owned, many=True).data
        metadata['dailylogin'] = "No"
        jsonResponse.update({
            "data": metadata,
            "status": "Success"
        })
        return Response(jsonResponse)
    except User.DoesNotExist:
        jsonResponse.update({
            "status": "Failed"
        })
        return Response(jsonResponse)


@api_view(['POST'])
def forgetPassword(request):
    body = json.loads(request.body.decode('utf-8'))
    jsonResponse = {}
    try:
        user = User.objects.get(
            username=body.get("username"),
            email=body.get("email")
        )
        URL = """%s/forgetPasswordValidation?username=%s&token=%s
        """ % (base_url, user.username, user.token)
        message = """Hello %s if you are trying to reset password please click link below
        %s
        If you are not trying, please ignore this email.

        Regard Greedisgood, Keep gambling :)
        """ % (user.first_name + " " + user.last_name, URL)
        sendEmail(user.email, "Forget Password", message)
        jsonResponse.update({
            "status": "Success"
        })
        return Response(jsonResponse)
    except User.DoesNotExist:
        jsonResponse.update({
            "status": "Failed"
        })
        return Response(jsonResponse)


@api_view(['GET'])
def forgetPasswordValidation(request):
    status = ""
    user = User.objects.filter(
        username=request.GET['username'],
        token=request.GET['token']
    )
    if len(user) > 0:
        newPassword = randomString(7)
        user.update(password=newPassword, token=randomString(20))
        status = "Success"
    else:
        status = "Invalid"
    html = """
            <html>
                <body><h4>%s reset password, new password is %s</h4>
                </body>
            </html>""" % (status, newPassword)
    return HttpResponse(html)


@api_view(['POST'])
def editProfile(request):
    body = json.loads(request.body.decode('utf-8'))
    jsonResponse = {}
    user = User.objects.filter(
        username=body.get("username"), password=body.get("password")
    )
    if len(user) > 0:
        user.update(
            first_name=body.get("first_name"),
            last_name=body.get("last_name"),
        )
        jsonResponse.update({
            "status": "Success"
        })
    else:
        jsonResponse.update({
            "status": "Invalid"
        })
    return Response(jsonResponse)


@api_view(['POST'])
def changePassword(request):
    body = json.loads(request.body.decode('utf-8'))
    jsonResponse = {}
    user = User.objects.filter(
        username=body.get("username"), password=body.get("old_password")
    )
    if len(user) > 0:
        user.update(
            password=body.get("new_password")
        )
        jsonResponse.update({
            "status": "Success"
        })
    else:
        jsonResponse.update({
            "status": "Invalid"
        })
    return Response(jsonResponse)


def randomString(stringLength):
    return ''.join(random.choice(
        string.ascii_lowercase + string.ascii_uppercase + string.digits
    ) for _ in range(stringLength))


def sendEmail(to, subject, body):
    gmail_user = "hireme.customerservice@gmail.com"
    gmail_password = "b!Nu$20111998"
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    text = """\
        Subject: %s

        %s
    """ % (subject, body)
    server.sendmail(gmail_user, to, text)
    print("Email sent successfully")
    server.close()


@api_view(['POST'])
def addNewItem(request):
    body = json.loads(request.body.decode('utf-8'))
    jsonResponse = {}
    item = Item.objects.filter(name=body.get("name"))
    if len(item) > 0:
        jsonResponse.update({
            "status": "Item already exist"
        })
    else:
        Item.objects.create(
            name=body.get("name"),
            image_url=body.get("image_url"),
            rarity=body.get("rarity"),
        )
        item = Item.objects.get(name=body.get("name"))
        serializer = ItemSerializer(item, many=False)
        jsonResponse.update({
            "data": serializer.data,
            "status": "Success"
        })
    return Response(jsonResponse)


@api_view(['POST'])
def addNewGame(request):
    body = json.loads(request.body.decode('utf-8'))
    jsonResponse = {}
    game = Game.objects.filter(name=body.get("name"))
    if len(game) > 0:
        jsonResponse.update({
            "status": "Game already exist"
        })
    else:
        Game.objects.create(
            name=body.get("name"),
            description=body.get("description"),
        )
        game = Game.objects.get(name=body.get("name"))
        serializer = GameSerializer(game, many=False)
        jsonResponse.update({
            "data": serializer.data,
            "status": "Success"
        })
    return Response(jsonResponse)


@api_view(['POST'])
def addGameReward(request):
    body = json.loads(request.body.decode('utf-8'))
    jsonResponse = {}
    gameReward = GameReward.objects.filter(
        game=body.get("game_id"),
        item=body.get("item_id")
    )
    if len(gameReward) == 0:
        gameObject = Game.objects.get(id=body.get("game_id"))
        itemObject = Item.objects.get(id=body.get("item_id"))
        GameReward.objects.create(
            game=gameObject,
            item=itemObject
        )
        gameReward = GameReward.objects.get(
            game=body.get("game_id"),
            item=body.get("item_id")
        )
        serializer = GameRewardSerializer(gameReward, many=False)
        jsonResponse.update({
            "data": serializer.data,
            "status": "Success"
        })
    else:
        jsonResponse.update({
            "status": "Reward already listed"
        })
    return Response(jsonResponse)


@api_view(['POST'])
def removeGameReward(request):
    body = json.loads(request.body.decode('utf-8'))
    jsonResponse = {}
    gameReward = GameReward.objects.filter(
        game=body.get("game_id"),
        item=body.get("item_id")
    )
    if len(gameReward) > 0:
        gameReward.delete()
        jsonResponse.update({
            "status": "Success"
        })
    else:
        jsonResponse.update({
            "status": "Reward not found"
        })
    return Response(jsonResponse)


@api_view(['POST'])
def clearGameReward(request):
    body = json.loads(request.body.decode('utf-8'))
    jsonResponse = {}
    gameReward = GameReward.objects.filter(game=body.get("game_id"))
    if len(gameReward) == 0:
        jsonResponse.update({
            "status": "No reward on specific game"
        })
    else:
        gameReward.delete()
        jsonResponse.update({
            "status": "Success"
        })
    return Response(jsonResponse)


@api_view(['POST'])
def addNewProbability(request):
    body = json.loads(request.body.decode('utf-8'))
    jsonResponse = {}
    probability = Probability.objects.filter(rarity=body.get("rarity"))
    if len(probability) == 0:
        Probability.objects.create(
            rarity=body.get("rarity"),
            chance=body.get("chance")
        )
        probability = Probability.objects.get(
            rarity=body.get("rarity"),
            chance=body.get("chance")
        )
        serializer = ProbabilitySerializer(probability, many=False)
        jsonResponse.update({
            "data": serializer.data,
            "status": "Success"
        })
    else:
        jsonResponse.update({
            "status": "Probability already exist"
        })
    return Response(jsonResponse)


@api_view(['POST'])
def updateProbability(request):
    body = json.loads(request.body.decode('utf-8'))
    jsonResponse = {}
    probability = Probability.objects.filter(rarity=body.get("rarity"))
    if len(probability) == 0:
        jsonResponse.update({
            "status": "Probability not found"
        })
    else:
        now = datetime.now(timezone.utc)
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        probability.update(
            chance=body.get("chance"),
            updated_at=formatted_date
        )
        probability = Probability.objects.get(rarity=body.get("rarity"))
        serializer = ProbabilitySerializer(probability, many=False)
        jsonResponse.update({
            "data": serializer.data,
            "status": "Success"
        })
    return Response(jsonResponse)


@api_view(['POST'])
def openTheBox(request):
    body = json.loads(request.body.decode('utf-8'))
    jsonResponse = {}
    if 'probability' in cache:
        probability = cache.get('probability')
    else:
        probability = list(Probability.objects.values().all())
        cache.set("probability", probability, timeout=CACHE_TTL)

    rarity = weighted_pick_item(probability)[0]["rarity"]
    if 'openboxrewardpool'+str(rarity) in cache:
        reward_pool = cache.get('openboxrewardpool'+str(rarity))
    else:
        reward_pool = list(
            GameReward.objects.filter(item__rarity=rarity).values().all()
        )
        cache.set("openboxrewardpool"+str(rarity), reward_pool, timeout=CACHE_TTL)

    reward = random.choice(reward_pool)
    userObject = User.objects.get(id=body.get("user_id"))
    itemObject = Item.objects.get(id=reward["item_id"])
    UserInventory.objects.create(
        user=userObject,
        item=itemObject,
    )
    serializer = ItemSerializer(itemObject, many=False)
    jsonResponse.update({
        "data": serializer.data,
        "status": "Success"
    })
    return Response(jsonResponse)


def weighted_pick_item(chances: list):
    chance_pool = [chance["chance"] for chance in chances]
    return random.choices(chances, chance_pool)
