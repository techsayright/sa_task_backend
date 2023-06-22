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
    


# access_token = "ya29.a0AWY7CkkGIcPO9rEXWWTFuj96iCy_xA5pwdtqbG6m2M6A2UgME1y2X8Am9EmpYrLhnakXwu4ZEdMqIUazWjOlBiLkU607KKcl3F7mkNZ6q1wFNE3gbMXyGPU0H1bDyxzjnH8_QfPKd9TnWmschLd8QBrM_u1yaCgYKAfcSARMSFQG1tDrpFUZ-jPzpWi-E_jpUQkZAXg0163"
# verification_result = verify_google_token(access_token)
# if verification_result:
#     print(verification_result)
# else:
#     print("Token verification failed.")