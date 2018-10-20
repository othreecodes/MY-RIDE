# MY-RIDE (Django Carpool) ![](https://img.shields.io/badge/othree-codes-yellowgreen.svg)
# Live Demo - http://myrideapp.xyz

![](http://i.imgur.com/sd8Ziu9.png)

### Installation
requires python > 3 django 1.9

After cloning repo

```sh
cd Carpool
python manage.py makemigrations
python manage.py migrate
```

### Create superuser
creates the admin account

```sh
python manage.py createsuperuser
Username:
Email Address:
Password:
Password (again):
```

###Coniguring Email
-Open settings.py

```python
#replace with gmail username and password or comment out to ignore the email
STATIC_URL = '/static/'
ACCOUNT_ACTIVATION_DAYS=7
EMAIL_HOST='smtp.gmail.com'
EMAIL_USE_TLS=1
EMAIL_PORT=587
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''

```

-Open views.py line 85
edit the email address there or comment out the line to ignore sending emails in contact form
```python
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




```




### Running the server

```sh
python manage.py runserver 
```
Open browser to
http://localhost:8000/

### Todos

 - [x] Notifications
 - [x] Chat Integration (personal and group messaging)
 - [x] Add liscence registration for drivers
 - [ ] Add Agency registration for hired cars
 - [x] Inbox and notification menus


License
-------

The MIT License (MIT). Please see LICENSE.rst for more information.


    Copyright (c) 2016-2017 Obi Uchenna David

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy,
    modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
    is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
