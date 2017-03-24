import json
from rest_framework import authentication
from django.http import *
from rest_framework.authentication import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from api.serializers import RequestSerializer
from app.models import CustomUser, Message, Vehicle, VehicleSharing, Request, Follow, Profile
from broadcast.models import *
from .serializers import UserSerializer,BroadcastSerializer,MessageSerializer,VehicleSerializer, \
  VehicleSharingSerializer, VehicleSerializerAdd, VehicleSharingSerializerAdd
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token

class UserList(APIView):

    def get(self,request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users,many=True)

        return Response(serializer.data)



class UserDetail(APIView):

    authentication_classes = (BasicAuthentication,TokenAuthentication)
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user.username
        data = CustomUser.objects.get(username=user)
        serializer = UserSerializer(data)
        print(request.user)
        return JsonResponse(serializer.data)




class BroadcastList(APIView):

    def get(self,request):

        broadcasts = Broadcast.objects.select_subclasses()
        serializer = BroadcastSerializer(broadcasts,many=True)

        return Response(serializer.data)


class MessageList(APIView):

    def get(self,request):

        messages = Message.objects.all()
        serializer = MessageSerializer(messages,many=True)

        return Response(serializer.data)


class Login(APIView):
    def post(self,request):
        data = str(request.POST['json'])
        dd = json.loads(data)
        email = dd['email']
        password = dd['password']

        user = authenticate(email=email, password=password)
        if user is not None:

            token = Token.objects.get_or_create(user=user)
            print(token[0])
            login(request, user)
            data = {
            'message': 'valid',
            'token': str(token[0])

            }
        else:
            data = {
            'message': 'invalid'
            }

        return JsonResponse(data)

@api_view(['POST'])
@csrf_exempt
def process_login(request):
    data = str(request.POST['json'])
    dd = json.loads(data)
    username = dd['username']
    password = dd['password']

    user = authenticate(username=username,password=password)
    if user is not None:

        token = Token.objects.get_or_create(user=user)
        print(token[0])
        login(request,user)
        data = {
            'message':'valid',
            'token':str(token[0])

        }
    else:
        data = {
            'message':'invalid'
        }

    return JsonResponse(data)


class DashStuff(APIView):

    authentication_classes = (BasicAuthentication,TokenAuthentication)
    permission_classes = [IsAuthenticated]
    def get(self,request):
        if request.user.user_type == 'Driver':
            vehicle = Vehicle.objects.filter(user=request.user).count()
            request_in = Request.objects.filter(ride__user=request.user).count()
            # notifications = Notification.objects.filter(user=request.user).order_by('pk').reverse()
            vehicle_share = VehicleSharing.objects.filter(user=request.user).count()
            followers = Follow.objects.filter(followee=request.user).count();

            data = {
                'vehicles':vehicle,
                'ride_requests':request_in,
                'shared_rides':vehicle_share,
                'followers':followers,

            }


            return JsonResponse(data)


@api_view(['POST'])
@authentication_classes((BasicAuthentication,TokenAuthentication))
@permission_classes((IsAuthenticated,))
@csrf_exempt
def addride(request):
    print(request.user)
    params = request.POST['data']
    params = json.loads(params)
    params['user'] = request.user.id
    serializer = VehicleSerializerAdd(data=params)
    result = "0"
    if serializer.is_valid():
        result = "1"
        serializer.save()
        print(serializer.errors)
    else:
        result = "-1"
    return HttpResponse(str(serializer.error_messages))

class UserVehicles(APIView):

    authentication_classes = (SessionAuthentication, BasicAuthentication,TokenAuthentication)
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user
        data = Vehicle.objects.filter(user=user)

        serializer = VehicleSerializer(data,many=True)

        return Response(serializer.data)

    def delete(self,request):
        params = request.data
        params = json.loads(params['data'])
        ride_id = params['id']

        vehicle = Vehicle.objects.get(pk=ride_id)
        result = 0
        if vehicle:
          if vehicle.user == request.user:
            vehicle.delete()
            result = 1
          else:
            result = -1

        return HttpResponse(result)


class UserSharedVehicles(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = VehicleSharing.objects.filter(user=user).order_by('date').reverse()

        serializer = VehicleSharingSerializer(data, many=True)
        return Response(serializer.data)

    def post(self,request):
        params = request.POST['data']
        params = json.loads(params)

        print(params)
        serializer = VehicleSharingSerializerAdd(data=params)

        if serializer.is_valid():
          serializer.save()
          print(serializer.errors)
        else:
          print(serializer.errors)



        return HttpResponse('OK')



class Requests(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    permission_classes = [IsAuthenticated]


    def get(self, request):
        user = request.user
        user = CustomUser.objects.get(pk=request.user.id)
        print(request.GET)
        if int(request.GET['id']) > 0:
            ride = VehicleSharing.objects.get(pk=request.GET['id'])
            pass_requests = Request.objects.filter(ride__user=user,ride=ride).order_by('reg_date').reverse()
        else:
            pass_requests = Request.objects.filter(ride__user=user).order_by('reg_date').reverse()
        serializer = RequestSerializer(pass_requests, many=True,context={'request': request})
        return Response(serializer.data)



#
# def process_login(request):
#     """
#     Default handler to login user
#     :param request: HttpRequest
#     """
#     code = request.GET.get('code', '')
#     json_header = {'content-type': 'application/json'}
#     token_url = 'https://%s/oauth/token' % settings.AUTH0_DOMAIN
#
#     token_payload = {
#         'client_id': settings.AUTH0_CLIENT_ID,
#         'client_secret': settings.AUTH0_SECRET,
#         'redirect_uri': settings.AUTH0_CALLBACK_URL,
#         'code': code,
#         'grant_type': 'authorization_code'
#     }
#
#     token_info = requests.post(token_url,
#                                data=json.dumps(token_payload),
#                                headers=json_header).json()
#
#     url = 'https://%s/userinfo?access_token=%s'
#     user_url = url % (settings.AUTH0_DOMAIN, token_info['access_token'])
#     user_info = requests.get(user_url).json()
#
#     # We're saving all user information into the session
#     request.session['profile'] = user_info
#     json_data = user_info
#
#     try:
#         user = authenticate(**user_info)
#     except:
#         return redirect('app:login')
#
#
#     if user.last_login is None:
#         createuser(user,json_data)
#
#     if user:
#         login(request, user)
#
#         return redirect(settings.AUTH0_SUCCESS_URL)
#
#     return HttpResponse(status=400)
#
#
# def createuser(user,data):
#     # person = CustomUser.objects.get(user=user)
#     print('this will handle a new login')
#     print(user.last_login)
#
#     the_user = CustomUser.objects.get(pk=user.id)
#     try:
#         the_user.full_name = data['name']
#         the_user.short_name = data['given_name']
#         the_user.user_type = 'Passenger'
#         the_user.sex = str(data['gender']).capitalize()
#         the_user.address = data['location']['name']
#
#     except:
#         pass
#     the_user.save()
#
#     url = 'http://localhost:8000/api/upload/'
#     image = requests.get(data['picture_large']).content
#     files = {'file': image}
#     payload = {'name':data['context']['id']}
#     r = requests.post(url,files=files,data=payload)
#
#     profile = Profile()
#     profile.user = user
#     profile.picture.name = r.content
#
#     profile.save()
#
#
# from django.views.decorators.csrf import csrf_exempt
# @csrf_exempt
# def upload_file(request):
#     if request.method == 'POST':
#         file = request.FILES['file']
#         name = request.POST['name']
#         destination = open(settings.BASE_DIR+settings.MEDIA_URL+name, 'wb+')
#         for chunk in file.chunks():
#             destination.write(chunk)
#
#
#     return HttpResponse(name,content_type="text/plain")
