# Spotify Authentication
Endpoints that do not require user authorization can be used with a client-level access token. Such an endpoint is for example the search, since it does not access or modify a user's data.

To get this access token, you first need to register your application in the Spotify developer console. Then, you need to POST the following request to the auth server:

`curl -X "POST" -H "Authorization: Basic Yzg...WE3ZTU=" -d grant_type=client_credentials https://accounts.spotify.com/api/token`

The `Basic` header is composed as follows: `my_client_id:my_client_secret` -> convert to base64. Essentially, you concatenate your client_id and client_secret (which you get form your application's page in the dev console) with a ":" and encode this string in base64.

The key fields in the response to this request are `access_token` and `expires_in` (in seconds).

The access token is a Bearer token, which you can use as follows:

`curl -X GET "https://api.spotify.com/v1/search?q=tania%20bowra&type=artist" -H "Authorization: Bearer BQB...rAJ8Eo"`

where the URL can be changed to any endpoint that does not require user authorization.

## Expired access token
**TODO: need to find out what error is returned if provided access token is expired**

## API Rate Limits
According to [this StackOverflow post](https://stackoverflow.com/questions/30548073/spotify-web-api-rate-limits), the API will return `429 (Too Many Requests)` (see [RFC6585](https://tools.ietf.org/html/rfc6585#section-4)) if the rate limit is reached. The post also mentions that the `429` response header will include a `Retry-After` field, which is the (rounded-down) number of seconds before the rate limit will expire.

**TODO: this needs to be verified.**

## Sources
- [Spotify Web API Endpoint Reference](https://beta.developer.spotify.com/documentation/web-api/reference/search/search/)
- [Spotify Authorization Flow Guides (Section: Client Credentials Flow)](https://beta.developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-flows)
- [Spotify Token Swap and Refresh](https://beta.developer.spotify.com/documentation/ios-sdk/guides/token-swap-and-refresh/)
- [StackOverflow: Spotify Web API Rate Limits](https://stackoverflow.com/questions/30548073/spotify-web-api-rate-limits)