# django-simple-social-login
A reusable django application for implementing social login using the Javascript api for both Google and Facebook. It also implements Login in using Facebook's Account kit with either email or phone


## Installation process

```
$ pip install -e git+https://github.com/gbozee/django-simple-social-login.git@master#egg=simple_social_login
```


## Setting Variables to set

**Facebook and AccountKit Required**

FACEBOOK_APP_ID

**Facebook only**

FACEBOOK_APP_SECRET

FACEBOOK_REDIRECT_URL defaults to `http://{{site.domain}}/{{reverse('fb_login.redirect_view)}}`

`FB_CREATE_USER_CALLBACK`: An optional callback function that creates a `User` based on the information gotten from `Facebook`

A sample look like this
```
def create_user(cls, email=None,name=None, birthday=None, **kwargs):
    return cls.objects.create(email=email,username=email)
```
**AccountKit Only**
```
FACEBOOK_ACCOUNT_KIT_API_VERSION (defaults to "v1.2")
FACEBOOK_ACCOUNT_KIT_REDIRECT_URL (defaults to )
FACEBOOK_ACCOUNT_KIT_APP_SECRET
```
**Google only**

`GOOGLE_CLIENT_ID`

`GOOGLE_CREATE_USER_CALLBACK` defaults to 
```

def create_user(cls, **user_data):
    return cls.objects.create(
        username=user_data['email'], email=user_data['email'],
        first_name=user_data['first_name'], last_name=data['last_name'])

```

## Signals to hook up to

**Facebook**
```
from simple_social_login.fb_login import signals

```
`signals.data_from_fb_scope` : Details fetched from the client that is required to create a user account. 

params passed are 

`request`: The django request object in case you need to do anything special with it

`data`: The user specific data passed from the client. This could be 
```
email
```

`signals.save_long_lived_token`: Swaps out the shortlived token for a longer one. 

**AccountKit**
```
from simple_social_login.account_kit import signals
```
`signals.account_kit_access_token`: useful data gotten after verification of acces token consist of the following params

`access_token`: The access token 

`expires_at`: a python datetime when the token would expire

`data`: The response gotten from the validation. Includes the following

```
{
    user_id,
    email, # if email login used
    number, # if sms login used
}
```

**Google**
```
from simple_social_login.google_login import signals
```
`signals.data_from_google_scope`: The request object and the verified user data fetched after initial token sent to server for validation.

Data include

`request`: the django original request object

`data`: this is a dict consisting of `email, first_name` and `last_name`

`after_creating_google_user`: A signals to implement any logic after the user has been logged in. Data include `request`


An example project is provided in the `example` folder for testing. Ensure you populate the required environmental variables listed in the `settings.py` of the project

## Todo
1. Provide better documentation
2. Control the json response that is sent back to the user

**Contributions and suggestions are welcome**

