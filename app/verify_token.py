import requests
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")

def verify_google_token(access_token: str = Depends(oauth2_scheme)):
    url = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
    params = {'access_token': access_token}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None 
    