/**
 * Created by OTHREE on 7/28/2016.
 */

window.onload = initForms;
var done = false;
function initForms() {
    stuff = document.getElementsByName('to')[0];
    if(stuff.readOnly){
        done = true;
    }
    for (var i=0; i< document.forms.length; i++) {
        document.forms[i].onsubmit = function() {return validateForm();}
    }
}



function validate(input){
    recipient = input.value;

    errorField = document.getElementById('error');
    var bool = false;
    var data = new XMLHttpRequest();
    data.open("GET", '/app/profile/'+recipient+'/', true);

    data.onreadystatechange = function () {
        if(data.status ==404){
            input.className= 'form-control alert alert-danger';
            errorField.className = 'label label-danger visible';
            errorField.innerHTML = 'No Such User'
            bool = false;
        }
        else {
            input.className= 'form-control';
            errorField.className = 'hidden';
            bool = true;
            done = true;

        }

    };
    data.send();

 return bool;
}

function validateForm(form){

    return done;

}