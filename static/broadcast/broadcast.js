/**
 * Created by OTHREE on 8/4/2016.
 */

function like(id) {

    button = document.getElementById('broad' + id);


    if (button.name == 'like') {

        button.innerHTML += '<i class="fa fa-refresh fa-spin"></i>';
        button.onclick = function(){

        };
        var data = new XMLHttpRequest();
        data.open("GET", '/broadcast/like/' + id + '/', true);

        data.onreadystatechange = function () {
            if (data.readyState != 4 || data.status != 200) {

            }
            else {
                button.innerHTML = button.innerHTML.replace('<i class="fa fa-refresh fa-spin"></i>', '');
                elemen = document.getElementById('like-count' + id);

                elemen.innerHTML = parseInt(elemen.innerHTML) + 1;
                button.innerHTML = button.innerHTML.replace('Like', 'Liked');

                button.name = 'liked';
                button.className = 'btn btn-flat btn-success btn-xs';
                button.onclick = function(){
                    like(id);
                };
            }

        }
        data.send();
    }
    else if (button.name == 'liked') {
        button.innerHTML += '<i class="fa fa-refresh fa-spin"></i>';
        button.onclick = function(){

        };
        var data = new XMLHttpRequest();
        data.open("GET", '/broadcast/like/' + id + '/', true);

        data.onreadystatechange = function () {
            if (data.readyState != 4 || data.status != 200) {

            }
            else {
                button.innerHTML = button.innerHTML.replace('<i class="fa fa-refresh fa-spin"></i>', '');
                elemen = document.getElementById('like-count' + id);
                elemen.innerHTML = parseInt(elemen.innerHTML) - 1;
                button.className = 'btn btn-flat btn-primary btn-xs';
                button.innerHTML = button.innerHTML.replace('Liked', 'Like');
                button.name = 'like';
                button.onclick = function(){
                    like(id);
                };
            }

        }
        data.send();
    }

}