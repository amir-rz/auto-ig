
# imports
from random import random
from instapy import InstaPy
from instapy import smart_run
# from instapy_cli import client
from instabot import Bot
from PIL import Image, ImageFont, ImageDraw

from os import environ, remove
from datetime import datetime, timedelta
import requests
import json
import urllib
import time
import random

# Instagram Limits 2020-2021:
# like: 300-400/day
# follow/unfollow: 150/day
# to avoid spamming on instagram:
# - 50 follow/unfollow per day on week 1
# - 100 follow/unfollow per day on week 2
# - 150 follow/unfollow per day on week 3
# stories : unlimited


# ---- Insta
IG_USERNAME = environ.get("IG_USERNAME")
IG_PASSWORD = environ.get("IG_PASSWORD")


# ---- Unsplash
UNSPLASH_ACCESS_KEY = environ.get("UNSPLASH_ACCESS_KEY")
# UNSPLASH_SECRET_KEY = "your unsplash secret key here"
UNSPLASH_URL = "https://api.unsplash.com/"
W = 1080
H = 1080
UNSPLASH_CREDS = {
    "client_id": UNSPLASH_ACCESS_KEY,
}
UNSPLASH_CATEGORIES = [
    "motivation",
    "motivational",
    "inspire",
    "inspirational",
    "inspiring",
    "life",
    "quote",
    "heavy"
]

# ---- Quotes
QUOTES_URL = "https://type.fit/api/quotes"


class Login:
    """ Instagram login for instapy and instabot """

    def __init__(self):
        pass
    # Instabot

    def login_instabot(self, username, password):
        """ login for instabot """
        self.bot = Bot()
        self.bot.login(username=username,
                       password=password, use_cookie=False)

        return self.bot
    # Instapy

    def login_instapy(self, username, password):
        """ login for instapy """
        self.session = InstaPy(username=username,
                               password=password,
                               headless_browser=True)
        return self.session


# one time login to prevent Instagram from blocking the account
login = Login()
bot = login.login_instabot(IG_USERNAME, IG_PASSWORD)
# session = login.login_instapy(IG_USERNAME, IG_PASSWORD)


def get_image():
    """ download a random image from unsplash and save it on local storage """
    UNSPLASH_PARAMS = {
        **UNSPLASH_CREDS,
        "query": UNSPLASH_CATEGORIES[random.randint(0, len(UNSPLASH_CATEGORIES)-1)],
        "orientation": "portrait",
    }

    try:
        img_raw = requests.get(f"{UNSPLASH_URL}photos/random", UNSPLASH_PARAMS)
        img_raw.raise_for_status()
        result = json.dumps(img_raw.json(), indent=4)
        results_dict = json.loads(result)
        image_id = results_dict["id"]
        # print(f'{results_dict["urls"]["raw"]}&w={W}')
        urllib.request.urlretrieve(
            f'{results_dict["urls"]["raw"]}&w={W}&dpr=2', f"posts/{image_id}.jpg")
        # im = Image.open(
        #     f"/home/amir/Documents/Practice/Django-beginner/auto-ig/posts/{image_id}.jpg")
        # newsize = (W, H)
        # im1 = im.resize(newsize)
        # im1.save(f'posts/{image_id}.jpg')
    except Exception as e:
        print("Error on download and saving image: \n")
        print(e)
        print("Trying again...")
        get_image()
    else:
        print("===| Got the image!")
        return image_id


def get_quote():
    """ Get a random inspirational quote """

    try:

        res = requests.get(QUOTES_URL)
        res.raise_for_status()
        results = json.dumps(res.json(), indent=4)
        results_dict = json.loads(results)
        quote_number = random.randint(0, len(results_dict)-1)
        quote_data = {
            "quote": results_dict[quote_number]['text'],
            "author": results_dict[quote_number]['author']
        }
    except Exception as e:
        print(e)
        print("Trying again...")
        get_quote()
    else:
        return quote_data


def new_post(text, imageName):
    # image = f"/home/amir/Documents/Practice/Django-beginner/auto-ig/posts/{imageName}.jpg"
    image = f"posts/{imageName}.jpg"
    bot.upload_photo(image, text)
    # with client(IG_USERNAME, IG_PASSWORD,) as cli:
    #     cli.upload(image, text)


def instapy():
    # ------------------instapy------------------
    comments = ['Nice shot! @{}',
                'I love your profile! @{}',
                'Your feed is an inspiration :thumbsup:',
                'Just incredible :open_mouth:',
                'What camera did you use @{}?',
                'Love your posts @{}',
                'Looks awesome @{}',
                'Getting inspired by you @{}',
                ':raised_hands: Yes!',
                'I can feel your passion @{} :muscle:']
    with smart_run(session):
        """ Activity flow """
        session.set_action_delays(enabled=True,
                                  follow=2,
                                  like=1,
                                  randomize=True,
                                  random_range_from=50,
                                  random_range_to=150)

        session.follow_user_followers(["sookhtejet.ir"], amount=10)
        session.like_by_tags(["psychology", "open_mind"], amount=10)


def start_posting():
    """ post a new image + quote in caption on IG """
    try:
        print("> 1: downloading image...")
        imageName = get_image()
        print(f"===| Image name: {imageName}")
        print("=========================\n")

        print("> 2: getting the quote...")
        qoute_data = get_quote()
        quote = qoute_data["quote"]
        author = qoute_data["author"]
        print(f"===| Quote: {quote} - {author}")
        print("=========================\n")

        # print("> 3: Writing quote on image...")
        # write_on_image(quote, author, imageName)
        # print("=========================\n")

        print("> 3: Posting on Instagram...")
        text = quote
        if author != None:
            text = f"{quote} - {author}"
        new_post(text, imageName)
        print("=========================\n")

        print("> 4: Removing the picture...")
        text = quote
        remove(f"posts/{imageName}.jpg")
        print("Image removed!")
        print("=========================\n")

    except Exception as e:
        print("Here we go again...")
        print("Trying...")
        start_posting()


while True:
    now = int(datetime.now().hour)
    print(f"Hour: {now}")
    print(f"Should post: {now > 6 and now < 24}")
    if now > 6 and now < 24:
        start_posting()
        sleep_time = random.randint(3600, 13000)
        print("A random time generated for the next post.")
        print(f"Next post on {round(sleep_time/60)} minutes")
        time.sleep(sleep_time)
    time.sleep(1800)

# def write_on_image(quote=str, author=str, imageName=str):
#     try:
#         image = Image.open(f'posts/{imageName}.jpg')
#         text = quote + " - " + author
#         image_editable = ImageDraw.Draw(image)
#         image_editable.text((15, 15), text, (237, 230, 211))
#         image.save("text.jpg")
#     except Exception as e:
#         print(e)
#     else:
#         print("Successfuly generated the final image!")
