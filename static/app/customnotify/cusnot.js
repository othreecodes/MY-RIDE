/**
 * Created by OTHREE on 7/17/2016.
 */

function my_special_notification_callback(data) {
    var badge = document.getElementById('live_notify_badge2');
    if (badge) {
        badge.innerHTML = data.unread_count;
    }
    var template = "<li> <a href='/user/dashboard/notifications/' id='{{id}}'> <i class='fa fa-info text-aqua'></i>  {{level}} "+
        "<br><small> {{ description }} </small></a></li>";
    var menu = document.getElementById('live_notify_list');
    if (menu) {
        menu.innerHTML = "";
        for (var i=0; i < data.unread_list.length; i++) {
            var item = data.unread_list[i];

            var message = "";
            if(typeof item.actor !== 'undefined'){
                message = item.actor;
            }
            if(typeof item.verb !== 'undefined'){
                message = message + " " + item.verb;
            }
            if(typeof item.target !== 'undefined'){
                message = message + " " + item.target;
            }
            if(typeof item.timestamp !== 'undefined'){
                message = message + " " + item.timestamp;
            }

            menu.innerHTML = menu.innerHTML + Mustache.render(template,item)

        }
    }



}
