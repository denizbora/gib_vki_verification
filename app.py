import os

import uvicorn
import requests
import json
import urllib.parse
from gradio_client import Client

from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing_extensions import Annotated

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
client = Client("https://docparser-text-captcha-breaker.hf.space/")
templates = Jinja2Templates(directory="www")


def get_token():
    url = "https://ivd.gib.gov.tr/tvd_server/assos-login"

    payload = 'assoscmd=cfsession&rtype=json&fskey=intvrg.fix.session&fuserid=INTVRG_FIX'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    veri_dict = json.loads(response.text)
    return veri_dict["token"]


def get_captcha(image_id):
    url = f"https://ivd.gib.gov.tr/captcha/jcaptcha?imageID={image_id}"

    img_response = requests.request("GET", url)

    image_data = img_response.content
    if os.path.exists('indirilen_resim.jpg'):
        os.remove('indirilen_resim.jpg')
    with open('indirilen_resim.jpg', 'wb') as dosya:
        dosya.write(image_data)

    return "indirilen_resim.jpg"


def solve_captcha(image_file):
    result = client.predict(
        image_file,  # str (filepath or URL to image) in 'img_org' Image component
        api_name="/predict"
    )
    return result


def tax_identification_number_verification(token, image_id, security_code, tckn1, vkn1, iller, vergidaireleri):
    url = "https://ivd.gib.gov.tr/tvd_server/dispatch"

    jp = {
        'imageID': image_id,
        'securityCode': security_code,
        'tckn1': tckn1,
        'vkn1': vkn1,
        'iller': iller,
        'vergidaireleri': vergidaireleri
    }

    jp_text = json.dumps(jp)

    data = {
        'token': token,
        'cmd': 'vergiNoIslemleri_vergiNumarasiSorgulama',
        'callid': 'c2717ea9f7b27-10',
        'pageName': 'R_INTVRG_INTVD_VERGINO_DOGRULAMA',
        'jp': jp_text
    }
    encoded_data = urllib.parse.urlencode(data)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=encoded_data)
    return response


@app.post("/")
async def create_product(tckn1: Annotated[str, Form()], vkn1: Annotated[str, Form()], iller: Annotated[str, Form()], vergidaireleri: Annotated[str, Form()]):
    token = get_token()
    base64_image = get_captcha("6it2y1lnd8b17e00")
    captcha_value = solve_captcha(base64_image)
    captcha_value = str(captcha_value).upper()
    print(captcha_value)
    verification_response = tax_identification_number_verification(token, "6it2y1lnd8b17e00", captcha_value,
                                                                   tckn1, vkn1, iller, vergidaireleri)
    return verification_response.json()

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})

@app.get("/sorgu")
async def get(request: Request):
    return templates.TemplateResponse("sorgu.html",{"request": request})

@app.post("/sorgu")
async def create_product(image_id: Annotated[str, Form()], tckn1: Annotated[str, Form()], vkn1: Annotated[str, Form()], iller: Annotated[str, Form()], vergidaireleri: Annotated[str, Form()], captcha: Annotated[str, Form()]):
    token = get_token()
    verification_response = tax_identification_number_verification(token, image_id, captcha,
                                                                   tckn1, vkn1, iller, vergidaireleri)
    return verification_response.json()


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8080)
