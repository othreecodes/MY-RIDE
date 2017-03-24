/**
 * Created by OTHREE on 7/19/2016.
 */
var misfires = 0;
function get_messages(){

    var data = new XMLHttpRequest();
    data.open("GET", '/app/user/messages/unread/', true);

    data.onreadystatechange = function () {
        if (data.readyState != 4 || data.status != 200) {
            misfires++;
        }
        else {
            misfires = 0;
            msg_data = JSON.parse(data.responseText);

            set_message_no(msg_data);
            set_messages(msg_data)
        }
    }
    data.send();

    if (misfires < 10) {
        setTimeout(get_messages,8000);
    } else {

    }

}

function set_message_no(data){
    badge = document.getElementById('msg_no');
    badge.innerHTML = data.unread_count;

    badge2 = document.getElementById('msg_badge');
    badge2.innerHTML = data.unread_count;

}

function set_messages(data){

    var temp = document.getElementById('msg-menu');


    var menu = '<li><!-- start message --><a href="{{ link }}"><div class="pull-left">'+
        '<i class="fa fa-envelope fa-2x"></i></div> <h4>'+
        '{{ sender }}&nbsp;<small><i class="fa fa-clock-o"></i>&nbsp;{{ date }}&nbsp;'+
        '</small> </h4> <p>{{ message }}</p> </a> </li>';
    if(menu) {
        temp.innerHTML = "";
        for (var i=0; i < data.unread_list.length; i++) {
            var item = data.unread_list[i];

            item.message = item.message.substring(0,38)+"...";
            try {
                item.date = item.date.replace("minutes", "mins").replace("hour", "hr") + " ago";
            }   catch(r) {

            }
            if(item.date === '0 mins ago'){
                item.date = 'just now';
            }


            temp.innerHTML = temp.innerHTML + Mustache.render(menu, item);

        }

    }


}


setTimeout(get_messages,1000);