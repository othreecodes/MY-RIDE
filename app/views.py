from django.contrib.auth.decorators import login_required
from django.core.management.commands.loaddata import humanize
from django.http.response import JsonResponse
from django.shortcuts import render
from django.template.context_processors import request
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.generic import *
from django.shortcuts import *
from django.forms import model_to_dict
from .forms import *
from django import forms as fm
from notifications.signals import notify
from django.template import defaultfilters
from django.contrib import messages as pop

# import pusher
#
# pusher_client = pusher.Pusher(
#     app_id='228750',
#     key='528a97eda2db586836e3',
#     secret='a5ad15c14704167945ed',
#     ssl=True
# )


# Create your views here.


class IndexView(View):

    def get(self, request):
        if request.user.is_authenticated():
            # pusher_client.trigger('test_channel', 'my_event', {'message': 'hello world'})
            return render(request, 'app/user/user_home.html', {'user': request.user})
        else:
            return render(request, template_name='app/index.html')


class CreateUser(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'app/user/user_form.html'
    # fields = ['full_name', 'short_name', 'email', 'sex','phone_number','user_type', 'address','username','password']

    success_url = reverse_lazy('app:index')


def create_profile(request):
    prof = Profile()
    prof.user = request.user
    prof.picture.name = 'user.png'
    prof.save()



    if request.user.user_type == 'Driver':
        dri = DriverInfo()
        dri.driver = request.user
        dri.save()

    return redirect('app:index')


class ViewUser(DetailView):
    model = CustomUser
    context_object_name = 'user'
    template_name = 'app/user/user_profile.html'


def view_user_id(request,pk):
    user = get_object_or_404(CustomUser,pk=pk)
    broadcasts = Broadcast.objects.filter(user=user).order_by('pk').reverse().select_subclasses()

    if request.is_ajax():
        return render_to_response(template_name='broadcast/broadcast_template.html',context={'user':user,'broadcasts':broadcasts},
                                  context_instance=RequestContext(request))
    return render(request,'app/user/user_profile.html',{'user':user,'broadcasts':broadcasts},)


@login_required
def view_user_name(request,user_id):
    user = get_object_or_404(CustomUser,username=user_id)
    broadcasts = Broadcast.objects.filter(user=user).order_by('pk').reverse().select_subclasses()

    if request.is_ajax():
        return render_to_response(template_name='broadcast/broadcast_template.html',context={'user':user,'broadcasts':broadcasts},
                                  context_instance=RequestContext(request))
    return render(request,'app/user/user_profile.html',{'user':user,'broadcasts':broadcasts},)


class EditUser(UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    context_object_name = 'user'
    template_name = 'app/user/edit_profile.html'
    success_url = reverse_lazy('app:index')



def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        username = username.lower()

        try:
            user = authenticate(username=username, password=password)
        except:
            return render(request, 'app/login.html', context={'error_message': 'Invalid login details'})

        to = request.POST.get('next')

        if user is not None:
            if user.is_active:
                if user.last_login is None:
                    prof = Profile()
                    prof.user = user
                    prof.picture.name = 'user.png'
                    prof.save()
                    login(request, user)
                    return redirect('app:index')
                login(request,user)

                try:
                    return redirect(request.POST.get('next'),'/')
                except Exception:
                    return redirect('app:index')
            else:
                return render(request, 'app/login.html', {'error_message': 'Your account is not enabled.\nyou need To verify your email'})

        else:
            return render(request, 'app/login.html', context={'error_message': 'Invalid login details'})
    return render(request, 'app/login.html')


def logout_user(request):
    logout(request)
    form = CustomUserCreationForm(request.POST or None)
    context = {
        "form": form,
    }
    return redirect('app:index')


def about(request):
    if request.user.is_authenticated():
        return render(request, 'app/about_loggedin.html')
    else:
        return render(request, 'app/about.html')




def contact(request):
    if request.method == 'POST':
        name = request.POST['username']
        email = request.POST['email']
        website = request.POST['website']
        message = request.POST['message']

        send_message = '''
        Name : %s
        Email : %s
        Website : %s
        Message : %s

        ''' % (name, email, website, message)

        send_mail('Contact Form Message From My Ride', send_message, 'daviduchenna@outlook.com', ['daviduchenna@outlook.com'])
        if request.user.is_authenticated():
            return render(request, 'app/contact_loggedin.html',{'done':True})
        else:
            return render(request, 'app/contact.html',{'done':True})

    if request.user.is_authenticated():
        return render(request, 'app/contact_loggedin.html')
    else:
        return render(request, 'app/contact.html')

def do_login(request):
    if request.user.is_authenticated():
        return redirect('app:index')

    return render(request, 'app/login.html')

@login_required
def vehicle_create(request, user_id):
    form = VehicleAddForm(request.POST or None, request.FILES or None)
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.user != user:
        raise Http404
    if user.user_type == 'Passenger':
        raise Http404
    if form.is_valid():
        ride = form.save(commit=False)
        ride.user = user
        ride.save()

        rides = Vehicle.objects.filter(user=user).order_by('pk').reverse()
        ride = Vehicle.objects.filter(user=user).latest('pk')

        notify.send(user, recipient=user, verb='Added a Ride', level='success', action_object=ride,description='Ride Created Sucessfully')
        return render(request, 'app/vehicles/view_vehicles.html',
                      {'user': user,
                     'rides': rides,
                       'message':True,
                       'message_title':'Ride Added Successfully.',
                       'message_body':'Your ride has been added successfully, view more options below',
                       })

    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'app/vehicles/vehicle_form.html', context)

@login_required
def vehicle_view(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.user != user:
        raise Http404
    if user.user_type == 'Passenger':
        raise Http404
    rides = Vehicle.objects.filter(user=user).order_by('pk').reverse()

    context = {
        'user': user,
        'rides': rides,
    }
    return render(request, 'app/vehicles/view_vehicles.html', context)

@login_required
def vehicle_delete(request, user_id, vehicle_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.user != user:
        raise Http404
    if user.user_type == 'Passenger':
        raise Http404
    ride = Vehicle.objects.get(pk=vehicle_id)

    notify.send(user, recipient=user, verb='Deleted a Ride', level='success',description='Ride Deleted Sucessfully')

    ride.delete()

    return redirect('app:view_rides', request.user.id)

@login_required
def vehicle_share(request, user_id, vehicle_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    form = VehicleShare(request.POST or None)
    if request.user != user:
        raise Http404
    if user.user_type == 'Passenger':
        raise Http404
    ride = Vehicle.objects.get(pk=vehicle_id, user=user)

    if request.method == "POST":
        if form.is_valid():
            share = form.save(commit=False)
            share.user = user

            share.start_time = request.POST['start_time']

            share.vehicle = ride
            share.save()
            rides = Vehicle.objects.filter(user=user).order_by('pk').reverse()
            shared = VehicleSharing.objects.filter(user=user).order_by('date').reverse()
            share = VehicleSharing.objects.filter(user=user).latest('pk')
            notify.send(user, recipient=user, verb='Shared a Ride', level='success', action_object=share,description='Ride Shared Sucessfully', target=ride)
            context = {
                'user': user,
                'rides': rides,
                'shared': shared,
                'message':True,
                'message_heading':'Ride Shared Successfully',
                'message_body':'Your ride has been shared successfully, make sure to end sharing when done.',
            }


            return render(request, 'app/vehicles/view_shared.html', context)


        else:
            form.fields['no_pass'] = fm.IntegerField(widget=forms.TextInput(attrs={'max':ride.seats,'type':'number', 'min':"1",'required':True,'class':'form-control'}))
            form.fields['no_pass'].label = 'Number of Passengers'
            form.fields['cost'] = fm.IntegerField(widget=forms.TextInput(attrs={'type':'number', 'min':"10", 'required':True,'placeholder':'In Naira (₦) ','class':'form-control'}))

            return render(request, 'app/vehicles/share_ride.html', {'user': user, 'ride': ride, 'form':form})
        pass

    else:

        form.fields['no_pass'] = fm.IntegerField(widget=forms.TextInput(attrs={'max':ride.seats,'type':'number', 'min':"1",'class':'form-control'}))
        form.fields['no_pass'].label = 'Number of Passengers'
        form.fields['cost'] = fm.IntegerField(widget=forms.TextInput(attrs={'type':'number', 'min':"10", 'required':True,'placeholder':'In Naira (₦) ','class':'form-control'}))

        return render(request, 'app/vehicles/share_ride.html', {'user': user, 'ride': ride, 'form':form})

@login_required
def vehicle_shared_view(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.user != user:
        raise Http404
    if user.user_type == 'Passenger':
        raise Http404
    rides = Vehicle.objects.filter(user=user).order_by('pk').reverse()
    shared = VehicleSharing.objects.filter(user=user).order_by('date').reverse()
    requests = Request.objects.filter(ride=shared).order_by('reg_date')
    context = {
        'user': user,
        'rides': rides,
        'shared': shared,
        'requests': requests,
    }
    return render(request, 'app/vehicles/view_shared.html', context)

@login_required
def vehicle_search(request, user_id):
    if not request.user.is_authenticated():
        redirect('app:sign_up')
    user = get_object_or_404(CustomUser, pk=user_id)

    allrides = VehicleSharing.objects.filter(ended=False).order_by('date').reverse()

    if request.method == 'POST':
        size = 0
        source = request.POST['source']
        date = request.POST['date']
        vehicle_type = request.POST['vehicle_type']
        if vehicle_type == 'default':
            vehicle_type = ''
        # print(date)
        if date == '' and source == '':
            from itertools import chain
            rides = VehicleSharing.objects.filter(
                vehicle__category__contains=vehicle_type,ended=False
            ).order_by('date').reverse()

            size = rides.count()

        elif date == '' and not source == '':
            from itertools import chain
            rides1 = VehicleSharing.objects.filter(
                  vehicle__category__contains=vehicle_type,start__icontains=source, ended=False
            ).order_by('date').reverse()
            rides2 = VehicleSharing.objects.filter(
                  vehicle__category__contains=vehicle_type,dest__icontains=source,ended=False
            ).order_by('date').reverse()
            rides = chain(rides1, rides2)
            size = rides1.count()+rides2.count()

        elif date != '' and source == '':
            from itertools import chain
            rides = VehicleSharing.objects.filter(
                date=date,vehicle__category__contains=vehicle_type, ended=False
            ).order_by('date').reverse()

            size = rides.count()


        elif date != '' and source != '':
            from itertools import chain
            rides1 = VehicleSharing.objects.filter(
                date=date, vehicle__category__contains=vehicle_type,start__icontains=source, ended=False
            ).order_by('date').reverse()
            rides2 = VehicleSharing.objects.filter(
                date=date, vehicle__category__contains=vehicle_type,dest__icontains=source,ended=False
            ).order_by('date').reverse()
            rides = chain(rides1, rides2)
            size = rides1.count()+rides2.count()
        else:
            from itertools import chain
            rides1 = VehicleSharing.objects.filter(
                 date=date, vehicle__category__contains=vehicle_type,start__icontains=source, ended=False
            ).order_by('date').reverse()
            rides2 = VehicleSharing.objects.filter(
                date=date, vehicle__category__contains=vehicle_type,dest__icontains=source,ended=False
            ).order_by('date').reverse()
            rides = chain(rides1, rides2)
            size = rides1.count()+rides2.count()

        allrides = VehicleSharing.objects.filter(ended=False).order_by('date').reverse()
        context = {
            'user': user,
            'rides': rides,
            'allrides':allrides,
            'size':size,
        }

        return render(request, 'app/vehicles/vehicle_search.html', context)

    else:
        if request.user != user:
            raise Http404
        context = {
            'user': user,
            'allrides': allrides,
        }

        return render(request, 'app/vehicles/vehicle_search.html', context)

@login_required
def request_ride(request,user_id, ride_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    ride = get_object_or_404(VehicleSharing, pk=ride_id)

    form = RequestForm(request.POST or None)

    if request.user != user:
        raise Http404

    if request.method == "POST":
        if form.is_valid():
            ride_request = form.save(commit=False)
            ride_request.user = user

            ride_request.ride = ride

            ride_request.save()

            notify.send(user, recipient=user, verb='Request', level='info', action_object=ride_request,description='Ride Request is Pending',target=ride)
            notify.send(user, recipient=ride.user, verb='Request', level='info', action_object=ride_request,description='Ride Request From '+user.username,target=ride)

            return redirect('app:requests_user_view',user_id )

@login_required
def view_single_ride(request,vehicle_share_id):
    ride = get_object_or_404(VehicleSharing, pk=vehicle_share_id)

    return render(request, 'app/vehicles/view_single_ride.html', {'ride': ride})

@login_required
def view_single_vehicle(request, ride_id):
    if  not request.user.is_authenticated():
        raise Http404
    ride = get_object_or_404(Vehicle, pk=ride_id)

    return render(request, 'app/vehicles/ride_view.html', {'ride': ride})

@login_required
def vehicle_share_delete(request, user_id, vehicle_share_id):

    user = get_object_or_404(CustomUser, pk=user_id)
    if request.user != user:
        raise Http404
    if user.user_type == 'Passenger':
        raise Http404
    ride = get_object_or_404(VehicleSharing, pk=vehicle_share_id, user=user)
    notify.send(user, recipient=user, verb='End', level='success', action_object=ride,description='Ride Sharing Ended',target=ride.vehicle)
    ride.ended = True
    ride.save()

    return redirect('app:view_shared',user_id)

@login_required
def requests_driver_view(request,user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    req = request.POST['share_id']
    shared_veh = VehicleSharing.objects.filter(pk=req).order_by('date').reverse()
    pass_requests = Request.objects.filter(ride=shared_veh).order_by('reg_date')


    context = {
        'user': user,
        'pass_requests': pass_requests,
        'info': shared_veh[0],
    }
    return render(request, 'app/request/requests_view.html', context)

@login_required
def request_approve(request,request_id):
    pass_requests = Request.objects.get(pk=request_id)
    back = request.META.get('HTTP_REFERER','/')


    if pass_requests.ride.user == request.user:
        pass_requests.status = 'approved'
        pass_requests.save()

        notify.send(pass_requests.ride.user, recipient=pass_requests.user, verb='Approved', level='success', action_object=pass_requests,description='Ride Request Approved',target=pass_requests.ride)

        if str(back).endswith('/requests/all'):
            return redirect('app:view_ride_requests')
        return request_view_hack(request,request.user.id,pass_requests.ride.id)

    else:
        raise Http404

@login_required
def request_view_hack(request, user_id,req_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    shared_veh = VehicleSharing.objects.filter(pk=req_id).order_by('date').reverse()

    pass_requests = Request.objects.filter(ride=shared_veh).order_by('reg_date')


    context = {
        'user': user,
        'pass_requests': pass_requests,
    }


    return render(request, 'app/request/requests_view.html', context)

@login_required
def request_deny(request,request_id):
    pass_requests = Request.objects.get(pk=request_id)
    back = request.META.get('HTTP_REFERER','/')

    if pass_requests.ride.user == request.user:
        pass_requests.status = 'denied'
        pass_requests.save()

        notify.send(pass_requests.ride.user, recipient=pass_requests.user, verb='Denied', level='danger', action_object=pass_requests,description='Ride Request Denied',target=pass_requests.ride)
        if str(back).endswith('/requests/all'):
            return redirect('app:view_ride_requests')
        return request_view_hack(request,request.user.id,pass_requests.ride.id)

    else:
        raise Http404

@login_required
def requests_user_view(request,user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.user != user:
        raise Http404

    all_user_requests = Request.objects.filter(user=user).order_by('reg_date').reverse()

    context = {
        'user': user,
        'all_user_requests': all_user_requests,
    }

    return render(request, 'app/request/requester_requests.html', context)

@login_required
def request_view(request,request_id):
    req = get_object_or_404(Request, pk=request_id)

    if request.user == req.user :
        context = {

            'user_requests': req,
        }

        return render(request, 'app/request/single_request.html', context)

    elif request.user.user_type == 'Driver':
        context = {

            'user_requests': req,
        }

        return render(request, 'app/request/single_request.html', context)

    else:
        raise Http404

@login_required
def request_delete(request, request_id):
    req = get_object_or_404(Request, pk=request_id)

    if request.user == req.user :
        user = get_object_or_404(CustomUser,pk=req.user.id)

        notify.send(user, recipient=user, verb='Canceled', level='info', action_object=req,description='Ride Request Canceled',target=req.ride)

        notify.send(user, recipient=req.ride.vehicle.user, verb='Canceled', level='info', action_object=req,description='Ride Request Canceled',target=req.ride)

        req.status = 'canceled'
        req.save()
        return redirect('app:requests_user_view',user.id)

    else:
        raise Http404


def ride(request):
    if not request.user.is_authenticated():
        return redirect('app:sign_up')
    else:
        return redirect('app:search_ride',request.user.id)

@login_required
def dashboard(request):
    if request.user.is_authenticated():
        vehicle = Vehicle.objects.filter(user=request.user).order_by('pk').reverse()
        request_out = Request.objects.filter(user=request.user).order_by('pk').reverse()
        message_in = Message.objects.filter(recipient=request.user,read=False).order_by('pk').reverse()
        message_out = Message.objects.filter(sender=request.user).order_by('pk').reverse()
        request_in = Request.objects.filter(ride__user=request.user).order_by('pk').reverse()
        # notifications = Notification.objects.filter(user=request.user).order_by('pk').reverse()
        vehicle_share = VehicleSharing.objects.filter(user=request.user).order_by('pk').reverse()



        context = {

            'vehicle' : vehicle,
            'request_out' : request_out,
            'message_in':message_in,
            'message_out':message_out,
            'request_in':request_in,
            'notific':request.user.notifications.unread(),
            'vehicle_share':vehicle_share,
        }


        return render(request, 'app/dashboard/dashboard_home.html',context=context)

    else:
        raise Http404


@login_required
def mark_as_read(request):
    id = request.GET['id']
    notification = get_object_or_404(
        Notification, recipient=request.user, id=id)
    notification.mark_as_read()

    return HttpResponse('OK')

@login_required
def unread_messages(request):
    if not request.user.is_authenticated():
        data = {
            'unread_count':0,
            'unread_list':[]
        }
        return JsonResponse(data)

    unread_list = []
    messages = Message.objects.filter(recipient=request.user,read=False,deleted=False).order_by('date').reverse()
    for n in messages:
        struct = model_to_dict(n)
        if n.sender:
            struct['sender'] = str(n.sender)
        if n.recipient:
            struct['recipient'] = str(n.recipient)
        if n.date:
            struct['date'] = defaultfilters.timesince(n.date)
        if n.message:
            struct['message'] = str(n.message)
        struct['link'] = n.url()

        unread_list.append(struct)
    data = {
        'unread_count': messages.count(),
        'unread_list': unread_list
    }
    return JsonResponse(data)

@login_required
def do_follow(request,followee,follower):

    foll = CustomUser.objects.get(pk=follower)   #followed user
    fole = CustomUser.objects.get(pk=followee)   #who to follow

    check = Follow.objects.filter(follower=foll,followee=fole)
    if not check.exists():
        f = Follow(follower=foll,followee=fole)
        f.save()

        notify.send(foll, recipient=fole, verb='Follow', level='info', action_object=f,description=str(foll.username)+' followed you')

    else:

        check.delete()

    return redirect('app:profile',followee)

@login_required
def all_ride_requests(request):
    user = get_object_or_404(CustomUser,pk=request.user.id)
    requests = Request.objects.filter(ride__user=user).order_by('pk')
    context ={
        'requests':requests,

    }

    return render(request,'app/request/all_requests.html',context)

@login_required
def preferences(request):

    return render(request,'app/dashboard/preferences.html')

@login_required
def messages(request):
    messages = Message.objects.filter(recipient=request.user,deleted=False).order_by('date').reverse()
    context = {
        'messages':messages,
    }
    return render(request,'app/dashboard/dashboard_messages.html',context)

@login_required
def messages_read(request,message_id):
    message = get_object_or_404(Message,recipient=request.user,pk=message_id)
    message.read = True
    message.save()
    context ={
        'message':message,
        'recipient':True,

    }

    return render(request,'app/dashboard/dashboard_messages_read.html',context)

@login_required
def messages_compose(request):

    if request.method == 'POST':
        sender = request.user
        to = request.POST['to']
        subject = request.POST['subject']
        message = request.POST['message']
        recipient = get_object_or_404(CustomUser,username=to)
        to_send = Message()
        to_send.sender = sender
        to_send.recipient = recipient
        to_send.subject = subject
        to_send.message = message
        to_send.save()

        return redirect('app:dashboard_sent')

    return render(request,'app/dashboard/dashboard_messages_compose.html')

@login_required
def delete_message(request,message_id):
    message = get_object_or_404(Message,recipient=request.user,pk=message_id)
    message.read = True
    message.deleted = True
    message.save()


    return redirect('app:dashboard_messages')

@login_required
def messages_reply(request,message_id):

    if request.method == 'POST':
        sender = request.user
        to = request.POST['to']
        subject = request.POST['subject']
        message = request.POST['message']
        recipient = get_object_or_404(CustomUser,username=to)
        to_send = Message()
        to_send.sender = sender
        to_send.recipient = recipient
        to_send.subject = subject
        to_send.message = message
        to_send.save()

        return redirect('app:dashboard_sent')

    message = get_object_or_404(Message,recipient=request.user,pk=message_id)
    context = {
        'subject':'RE: '+message.subject,
        'recipient':message.sender,

    }

    return render(request,'app/dashboard/dashboard_messages_compose.html',context)

@login_required
def messages_forward(request,message_id):

    if request.method == 'POST':
        sender = request.user
        to = request.POST['to']
        subject = request.POST['subject']
        message = request.POST['message']
        recipient = get_object_or_404(CustomUser,username=to)
        to_send = Message()
        to_send.sender = sender
        to_send.recipient = recipient
        to_send.subject = subject
        to_send.message = message
        to_send.save()

        return redirect('app:dashboard_sent')

    from itertools import chain

    message = get_object_or_404(Message,pk=message_id)

    if message.sender != request.user and message.recipient != request.user:
        raise Http404

    context = {
        'subject':'FWD: '+message.subject,
        'message':str(message.message)+'\n\n'+'Forwarded From '+str(message.sender),


    }

    return render(request,'app/dashboard/dashboard_messages_compose.html',context)

@login_required
def sent(request):

    messages = Message.objects.filter(sender=request.user).order_by('date').reverse()
    context = {
        'messages':messages,
    }
    return render(request,'app/dashboard/dashboard_messages_sent.html',context)

@login_required
def messages_read_sent(request,message_id):
    message = get_object_or_404(Message,sender=request.user,pk=message_id)
    message.read = True
    message.save()
    context ={
        'message':message,
         'recipient':False,

    }

    return render(request,'app/dashboard/dashboard_messages_read.html',context)

@login_required
def messages_junk(request):
    messages = Message.objects.filter(recipient=request.user,deleted=True).order_by('date').reverse()
    context = {
    'messages':messages,
    }

    return render(request,'app/dashboard/dashboard_messages_junk.html',context)


@login_required
def notifications(request):

    return render(request,'app/dashboard/dashboard_notifications.html',{'notifications':request.user.notifications.unread})


@login_required
def image_update(request):
    if request.method == 'POST':
        image = request.FILES['image']
        profile = get_object_or_404(Profile,user=request.user)
        profile.picture = image
        profile.save()


        return redirect('app:preferences')

    else:
        raise Http404

@login_required
def basic_update(request):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser,pk=request.user.id)
        fullname = request.POST['fullname']
        username = request.POST['username']
        shortname = request.POST['shortname']
        username = str(username).lower()

        if not username == request.user.username:
            check = CustomUser.objects.filter(username=username)
            if not check.exists():
                user.username = username
                user.full_name = fullname
                user.short_name = shortname
                user.save()
                pop.add_message(request,pop.SUCCESS,"Basic Profile Updated Successfully")
                return redirect('app:preferences')
            else:
                pop.add_message(request,pop.ERROR,"User with that username already exist")
                return redirect('app:preferences')

        else:
            user.username = username
            user.full_name = fullname
            user.short_name = shortname
            user.save()
            pop.add_message(request,pop.SUCCESS,"Basic Profile Updated Successfully")
            return redirect('app:preferences')

    else:
        raise Http404

@login_required
def user_update(request):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser,pk=request.user.id)
        email = request.POST['email']
        phone = request.POST['phone']

        if email and phone:
            user.email = email
            user.phone_number = phone
            user.save()
            pop.add_message(request,pop.SUCCESS,"User Information Updated Successfully")
            return redirect('app:preferences')
        else:
            pop.add_message(request,pop.ERROR,"User Information not Saved")
            pop.add_message(request,pop.INFO,"You left one or more fields empty")
            return redirect('app:preferences')

    else:
        raise Http404

@login_required
def driver_update(request):
    if request.method == 'POST':
        dri = DriverInfo.objects.filter(driver=request.user).first()
        if dri == None:
            dri = DriverInfo()
            dri.driver = request.user

        number = request.POST.get('number',None)
        date = request.POST.get('date',None)
        picture = request.FILES.get('picture',None)
        if number and date and picture:
            dri.date_issuance = date
            dri.liscence_no = number
            dri.scanned = picture
            dri.confirmed = False
            dri.save()
            pop.add_message(request,pop.SUCCESS,"Driver Information Updated Successfully")
            pop.add_message(request,pop.INFO,"Driver information must be confirmed before you can start to share rides")
            return redirect('app:preferences')

        else:
            pop.add_message(request,pop.ERROR,"Driver Information not Saved")
            pop.add_message(request,pop.INFO,"You left one or more fields empty")
            return redirect('app:preferences')


    else:
        raise Http404


@login_required
def bio_update(request):
    if request.method == 'POST':
        profile = get_object_or_404(Profile,user=request.user)
        profile.bio = request.POST.get('bio')
        profile.education = request.POST.get('education')
        profile.work = request.POST.get('work')
        profile.save()

        pop.add_message(request,pop.SUCCESS,"Bio Updated Successfully")
        return redirect('app:preferences')

    else:
        raise Http404

@login_required
def app_update(request):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser,pk=request.user.id)
        user.address = request.POST.get('location')
        user.user_type = request.POST.get('type')
        user.save()
        pop.add_message(request,pop.SUCCESS,"App information Updated Successfully")
        return redirect('app:preferences')
        # else:
        #     pop.add_message(request,pop.ERROR,"An Error Occurred. You tried to hack my site ba ?")
        #     return redirect('app:preferences')

    else:
        raise Http404

@login_required
def social_update(request):
    if request.method == 'POST':
        prof = get_object_or_404(Profile,user=request.user)
        prof.social_facebook = request.POST.get('fb')
        prof.social_instagram = request.POST.get('ig')
        prof.social_twitter = request.POST.get('tw')

        prof.save()
        pop.add_message(request,pop.SUCCESS,"Social Profile Updated Successfully")
        return redirect('app:preferences')


    else:
        raise Http404


@login_required
def password_update(request):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser,pk=request.user.id)
        old = request.POST.get('old')
        new = request.POST.get('new')
        conf = request.POST.get('conf')

        if old and new and conf:
            try:
                auth = authenticate(username=user.username, password=old)
            except:
                pop.add_message(request,pop.ERROR,"Old Password is not correct")
                return redirect('app:preferences')


            if new == conf:
                user.set_password(new)
                user.save()
                pop.add_message(request,pop.SUCCESS,"Password changed Successfully")
                return redirect('app:preferences')
            else:
                pop.add_message(request,pop.ERROR,"confirmation password does not match")
                return redirect('app:preferences')


        else:
            pop.add_message(request,pop.ERROR,"Password not changed")
            pop.add_message(request,pop.INFO,"You left one or more fields empty")
            return redirect('app:preferences')


    else:
        raise Http404















