/**
 * Created by OTHREE on 8/1/2016.
 */

var share_to;
var share_to_icon;
window.onload = function(){
    share_to = document.getElementsByName('share_to');
    share_to_icon = document.getElementsByName('share_to-icon')
     

}

function setEveryone(){
    for(ele=0;ele<share_to.length;ele++){
    share_to[ele].value = 'everyone';
        share_to_icon[ele].className ='fa fa-globe';
        console.log(share_to[ele].value)
    }


}

function setFollowers(){
    for(ele=0;ele<share_to.length;ele++){
        share_to[ele].value = 'followers';
        share_to_icon[ele].className ='fa fa-users';
        console.log(share_to[ele].value)
    }


}