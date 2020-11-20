# Exist authentication token

As a proper service, the Exist uses OAuth2 for authorization and authentication.
To make secure calls to the Exist you first need to authrorize your client and then get the authentication token.

## Authentication token
To get the `token` take a look at their documentation on [OAuth2 authentication](http://developer.exist.io/?python#oauth2-authentication).
It's pretty well explained. What you're after is that `access_token` which you should store in your environment
variables as the `EXIST_TOKEN`.

## Refresh authentication token

Obtained access token only lasts for a year. That's a lot of time but it can hit you in the least expected moment.
To refresh the token please follow really well written documentation on
[refreshing an access token](http://developer.exist.io/?python#refreshing-an-access-token).

In case you forgot your details, you can check them by going to your account in the Exist.
Then find "Developer clients" and select the client that is responsible for updating data.
All data, i.e. client id, client secret and the refhres token should be on that page.
