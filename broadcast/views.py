from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.context_processors import request
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.six import b
from notifications.signals import notify
from app.models import CustomUser

from .models import *
from django.shortcuts import *
# Create your views here.

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg','gif','bmp']
@login_required
def upload_text(request):
    if request.method =='POST':
        text = request.POST['text-text']
        share = request.POST['share_to']

        text_broadcast = TextBroadcast()
        text_broadcast.user = request.user
        text_broadcast.message = text

        if share == 'followers':
            text_broadcast.send_to_all=False
        else:
            text_broadcast.send_to_all=True

        text_broadcast.save()

        return redirect('broadcast:index')

    else:
        raise Http404

@login_required
def upload_image(request):
    if request.method == 'POST':
        image = request.FILES['image-image']
        desc = request.POST['text-image']
        share = request.POST['share_to']

        image_broadcast = ImageBroadcast()
        image_broadcast.image = image
        image_broadcast.user = request.user
        image_broadcast.description = desc

        if share == 'followers':
            image_broadcast.send_to_all=False
        else:
            image_broadcast.send_to_all=True

        image_broadcast.save()

        return redirect('broadcast:index')

    else:
        raise Http404

@login_required
def upload_ride(request):
    if request.method == 'POST':
        source = request.POST['source']
        destination = request.POST['destination']
        date = request.POST['date']
        share = request.POST['share_to']

        ride_broadcast = RideBroadcast()
        ride_broadcast.user = request.user
        ride_broadcast.date_needed = date
        ride_broadcast.source = source
        ride_broadcast.dest = destination

        if share == 'followers':
            ride_broadcast.send_to_all=False
        else:
            ride_broadcast.send_to_all=True

        ride_broadcast.save()

        return redirect('broadcast:index')

    else:
        raise Http404

@login_required
def upload_direction(request):
    if request.method == 'POST':
        source = request.POST['ride-source']
        dest = request.POST['ride-destination']
        add_info = request.POST['ride-text']
        share = request.POST['share_to']

        direct_broadcast = DirectionBroadcast()
        direct_broadcast.user = request.user
        direct_broadcast.location = source
        direct_broadcast.destination = dest
        direct_broadcast.additional_info = add_info
        if share == 'followers':
            direct_broadcast.send_to_all=False
        else:
            direct_broadcast.send_to_all=True

        direct_broadcast.save()

        return redirect('broadcast:index')

    else:
        raise Http404


def index(request,
    template='broadcast/broadcasts_home.html',
    page_template='broadcast/broadcast_template.html'):
    broadcasts = Broadcast.objects.order_by('pk').reverse().select_subclasses()

    try:
        users = CustomUser.objects.order_by('?').exclude(followee__follower=request.user).exclude(pk=request.user.id)
    except:
        users = None

    context ={ 'broadcasts':broadcasts,
    'page_template': page_template,
    'users':users,

    }

    if request.is_ajax():
        template = page_template
    return render_to_response( template, context, context_instance=RequestContext(request))

@login_required
def like_broadcast(request,broadcast_id):
    broadcast = get_object_or_404(Broadcast,pk=broadcast_id)
    test = Like.objects.filter(liker=request.user,broadcast_message=broadcast)
    if(test.exists()):
        test.delete()

    else:
        like = Like()
        like.broadcast_message = broadcast
        like.liker = request.user

        like.save()

        notify.send(request.user,recipient=broadcast.user,verb='Liked Broadcast ',action_object=broadcast,
                    description=str(request.user)+' Liked your Broadcast',level='info')

    page_template='broadcast/broadcast_template.html'
    template = page_template
    broadcasts = Broadcast.objects.order_by('pk').reverse().select_subclasses()

    context ={ 'broadcasts':broadcasts,
               'page_template': page_template
               }
    return render_to_response( template, context, context_instance=RequestContext(request))



@login_required
def rebc(request,bc_id):


    broadcast = Broadcast.objects.filter(pk=bc_id).select_subclasses()[0]
    broadcast.pk = None
    broadcast.id = None
    broadcast.bc_from = broadcast.user
    broadcast.user = request.user
    broadcast.bc_time = timezone.now()
    broadcast.bc_date = timezone.now()
    broadcast.save()

    notify.send(request.user,recipient=broadcast.bc_from,verb='Re-Bc\'d Broadcast ',action_object=broadcast,
                description=str(request.user)+' Shared your Broadcast',level='info')

    return redirect('broadcast:index')


def broadcast_view(request,bc_id):
    broad  = Broadcast.objects.filter(pk=bc_id).select_subclasses()[0]

    return render(request,'broadcast/broadcast_view.html',{'broad':broad})


@login_required
def comment(request,broadcast_id):
    broadcast = get_object_or_404(Broadcast,pk=broadcast_id)
    comment = Comment()
    comment.commenter = request.user
    comment.broadcast_message = broadcast
    try:
        comment.comment = request.POST['comment']
    except:
        redirect(broadcast.get_absolute_url())

    comm = Comment.objects.filter(broadcast_message=broadcast).values_list('commenter',flat=True).distinct()
    #to add distinct on commenters when using mysql finally



    if comm.count() >= 1:

        for user in comm:

            recipient = CustomUser.objects.get(pk=user)
            if recipient == request.user:
                pass
            elif recipient == broadcast.user:
                pass
            else:
                notify.send(request.user,recipient=recipient,verb='commented on Broadcast ',action_object=broadcast,
                      description=str(request.user)+' commented on a Broadcast You are following ',level='info')


    notify.send(request.user,recipient=broadcast.user,verb='commented on Broadcast ',action_object=broadcast,
                    description=str(request.user)+' commented on your broadcast ',level='info')


    comment.save()

    return redirect('broadcast:view', broadcast_id)























