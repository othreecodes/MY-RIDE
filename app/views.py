from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.generic import *
from django.shortcuts import *
from .forms import *
import datetime
from django import forms as fm


# Create your views here.

class IndexView(View):

    def get(self, request):
        if request.user.is_authenticated():
            return render(request, 'app/user_home.html', {'user': request.user})
        else:
            return render(request, template_name='app/index.html')


class CreateUser(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'app/user_form.html'
    # fields = ['full_name', 'short_name', 'email', 'sex','phone_number','user_type', 'address','username','password']

    success_url = reverse_lazy('app:login')


class ViewUser(DetailView):
    model = CustomUser
    context_object_name = 'user'
    template_name = 'app/user_profile.html'


class EditUser(UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    context_object_name = 'user'
    template_name = 'app/edit_profile.html'
    success_url = reverse_lazy('app:index')


def login_user(request):
    if request.user.is_authenticated():
        return render(request, 'app/user_home.html', {'user': request.user})
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                return render(request, 'app/user_home.html', {'user': request.user})
            else:
                return render(request, 'app/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'app/login.html', context={'error_message': 'Invalid login details'})
    return render(request, 'app/index.html')


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
        return render(request, 'app/user_home.html', {'user': request.user})
    return render(request, 'app/login.html')


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

        rides = Vehicle.objects.filter(user=user)
        return render(request, 'app/view_vehicles.html', {'user': user, 'rides': rides})

    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'app/vehicle_form.html', context)


def vehicle_view(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.user != user:
        raise Http404
    if user.user_type == 'Passenger':
        raise Http404
    rides = Vehicle.objects.filter(user=user)

    context = {
        'user': user,
        'rides': rides,
    }
    return render(request, 'app/view_vehicles.html', context)


def vehicle_delete(request, user_id, vehicle_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.user != user:
        raise Http404
    if user.user_type == 'Passenger':
        raise Http404
    ride = Vehicle.objects.get(pk=vehicle_id)
    ride.delete()
    rides = Vehicle.objects.filter(user=user)

    return render(request, 'app/view_vehicles.html', {'user': user, 'rides': rides})


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

            share.vehicle = ride
            share.save()
            rides = Vehicle.objects.filter(user=user)
            shared = VehicleSharing.objects.filter(user=user)
            context = {
                'user': user,
                'rides': rides,
                'shared': shared,
            }
            return render(request, 'app/view_shared.html', context)


        else:
            form.fields['no_pass'] = fm.IntegerField(widget=forms.TextInput(attrs={'max':ride.seats,'type':'number', 'min':"1",'required':True}))

            form.fields['cost'] = fm.IntegerField(widget=forms.TextInput(attrs={'type':'number', 'min':"10", 'required':True,'placeholder':'In Naira (₦) '}))

            return render(request, 'app/share_ride.html', {'user': user, 'ride': ride,'form':form})
        pass

    else:

        form.fields['no_pass'] = fm.IntegerField(widget=forms.TextInput(attrs={'max':ride.seats,'type':'number', 'min':"1"}))

        form.fields['cost'] = fm.IntegerField(widget=forms.TextInput(attrs={'type':'number', 'min':"10", 'required':True,'placeholder':'In Naira (₦) '}))

        return render(request, 'app/share_ride.html', {'user': user, 'ride': ride,'form':form})


def vehicle_shared_view(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.user != user:
        raise Http404
    if user.user_type == 'Passenger':
        raise Http404
    rides = Vehicle.objects.filter(user=user)
    shared = VehicleSharing.objects.filter(user=user)
    requests = Request.objects.filter(ride=shared)
    context = {
        'user': user,
        'rides': rides,
        'shared': shared,
        'requests': requests,
    }
    return render(request, 'app/view_shared.html', context)


def vehicle_search(request, user_id):
    if not request.user.is_authenticated():
        redirect('app:signup')
    user = get_object_or_404(CustomUser, pk=user_id)

    rides = VehicleSharing.objects.all()
    if request.method == 'POST':
        source = request.POST['source']
        destination = request.POST['destination']
        date = request.POST['date']
        vehicle_type = request.POST['vehicle_type']
        if vehicle_type == 'default':
            vehicle_type = ''
        # print(date)

        print(vehicle_type)
        rides = VehicleSharing.objects.filter(
             dest__contains=destination,date__month=timezone.now().month, vehicle__category__contains=vehicle_type,start__icontains=source
        )
        print(rides)
        context = {
            'user': user,
            'rides': rides,
        }

        return render(request, 'app/vehicle_search.html',context)

    else:
        if request.user != user:
            raise Http404
        context = {
            'user': user,
            'rides': rides,
        }

        return render(request, 'app/vehicle_search.html',context)


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
            return redirect('app:requests_user_view',user_id )


def view_single_ride(request,vehicle_share_id):
    ride = get_object_or_404(VehicleSharing, pk=vehicle_share_id)

    return render(request,'app/view_single_ride.html', {'ride': ride})


def view_single_vehicle(request, ride_id):
    if  not request.user.is_authenticated():
        raise Http404
    ride = get_object_or_404(Vehicle, pk=ride_id)

    return render(request,'app/ride_view.html', {'ride': ride})


def vehicle_share_delete(request, user_id, vehicle_share_id):

    user = get_object_or_404(CustomUser, pk=user_id)
    if request.user != user:
        raise Http404
    if user.user_type == 'Passenger':
        raise Http404
    ride = get_object_or_404(VehicleSharing, pk=vehicle_share_id, user=user)

    ride.delete()

    return redirect('app:view_shared',user_id)


def requests_driver_view(request,user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    req = request.POST['share_id']
    print(req)
    shared_veh = VehicleSharing.objects.filter(pk=req)
    print(shared_veh)
    pass_requests = Request.objects.filter(ride=shared_veh)
    print(pass_requests)

    context = {
        'user': user,
        'pass_requests': pass_requests,
    }
    return render(request,'app/requests_view.html', context)


def request_approve(request,request_id):
    pass_requests = Request.objects.get(pk=request_id)

    if pass_requests.ride.user == request.user:
        pass_requests.status = 'approved'
        pass_requests.save()

        return request_view_hack(request,request.user.id,pass_requests.ride.id)

    else:
        raise Http404


def request_view_hack(request, user_id,req_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    shared_veh = VehicleSharing.objects.filter(pk=req_id)
    print(shared_veh)
    pass_requests = Request.objects.filter(ride=shared_veh)
    print(pass_requests)

    context = {
        'user': user,
        'pass_requests': pass_requests,
    }

    return render(request,'app/requests_view.html', context)


def request_deny(request,request_id):
    pass_requests = Request.objects.get(pk=request_id)

    if pass_requests.ride.user == request.user:
        pass_requests.status = 'denied'
        pass_requests.save()

        return request_view_hack(request,request.user.id,pass_requests.ride.id)

    else:
        raise Http404


def requests_user_view(request,user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.user != user:
        raise Http404

    all_user_requests = Request.objects.filter(user=user)

    context = {
        'user': user,
        'all_user_requests': all_user_requests,
    }

    return render(request,'app/requester_requests.html',context)


def request_view(request,request_id):
    req = get_object_or_404(Request, pk=request_id)

    if request.user == req.user :
        context = {

            'user_requests': req,
        }

        return render(request,'app/single_request.html',context)

    elif request.user.user_type == 'Driver':
        context = {

            'user_requests': req,
        }

        return render(request,'app/single_request.html',context)

    else:
        raise Http404


def request_delete(request, request_id):
    req = get_object_or_404(Request, pk=request_id)

    if request.user == req.user :
        user = get_object_or_404(CustomUser,pk=req.user.id)
        req.delete()

        return redirect('app:requests_user_view',user.id)

    else:
        raise Http404


def ride(request):
    if not request.user.is_authenticated():
        return redirect('app:sign_up')
    else:
        return redirect('app:search_ride',request.user.id)



























