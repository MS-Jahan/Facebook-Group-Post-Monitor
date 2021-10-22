#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time, os
from authenticate_improved import authenticate
import telepot
from telepot.namedtuple import InputMediaPhoto
import creds
import json
import requests
import shutil
import traceback

from urllib.parse import urlparse
from urllib.parse import parse_qs

REPO_NAME = creds.REPO_NAME
group_id = "ist.prodipto27"

authenticate()


bot = telepot.Bot(creds.bot_token) # Telegram Bot Token 
chat_id = creds.chat_id

def sendToTelegram(msg):
    print(msg)
    bot.sendMessage(chat_id, msg)

chrome_options = Options()
chrome_options.add_argument("--user-data-dir=chrome-data")
# chrome_options.add_argument('--headless')
s = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=s, options=chrome_options)


URL = 'https://mbasic.facebook.com/groups/' + group_id
browser.get(URL)
posts = browser.find_elements_by_tag_name('article')

print(len(posts))
#print(links)

# curr_posts = []

prev_posts = []

try:
    with open(REPO_NAME + "/posts/" + group_id + ".txt", "r") as f:
        prev_posts = f.read().splitlines()
except:
    print(traceback.format_exc())


# Check if posts folder exists
try:
    os.mkdir(REPO_NAME + "/posts")
except:
    print(traceback.format_exc())

post_ids = []

for post in posts:

    # curr_posts.append(post.text)
    post_keys = post.get_attribute("data-ft")

    if post_keys == None:
        continue

    # print(post_keys)
    post_keys = json.loads(post_keys)
    post_id = post_keys["top_level_post_id"]
    post_ids.append(post_id)

print(prev_posts)
print(post_ids)

for i, post_id in enumerate(post_ids):
    if post_id not in prev_posts:
        # Check if img folder exists
        try:
            os.mkdir("img")
        except:
            print(traceback.format_exc())

        try:
            POST_URL = URL + "/posts/" + post_id
            browser.get(POST_URL)

            body = browser.find_element_by_tag_name('body')
            body.screenshot("img/body.png")

            whole_post = browser.find_element_by_class_name('bi')
            postText = whole_post.text

            paragraphs = browser.find_elements_by_tag_name('p')

            post_string = ""

            for para in paragraphs:
                post_string += "\n" + str(para.text)

            img_link_tags = browser.find_elements_by_tag_name('a')

            img_files = []
            # img_files.append(InputMediaPhoto(type='photo', media=open(REPO_NAME + "img/body.png", 'rb')))
            
            img_files.append(InputMediaPhoto(type='photo', media=open("img/body.png", 'rb')))

            img_urls = []
            for img in img_link_tags:
                img_urls.append(img.get_attribute("href"))

            for j, link in enumerate(img_urls):
                
                url = link
                if "photo.php" not in url:
                    pass
                    img_urls.remove(link)
                else:
                    parsed_url = urlparse(url)
                    img_id = parse_qs(parsed_url.query)['fbid'][0]
                    url = 'https://mbasic.facebook.com/photo/view_full_size/?fbid=' + img_id + "&ref_component=mbasic_photo_permalink&ref_page=%2Fwap%2Fphoto.php&refid=13&__tn__=%2Cg"
                    
                    browser.get(url)
                    url = browser.current_url
                    try:
                        img = requests.get(url, allow_redirects=True)
                        f_ext = '.jpg'
                        f_name = 'img' + str(j) + f_ext
                        with open("img/" + f_name, 'wb') as f:
                            f.write(img.content)
                    
                        img_files.append(InputMediaPhoto(type='photo', media=open("img/" + f_name, 'rb')))
                    except:
                        pass
            
            img_files = img_files[:10]

            if post_id not in prev_posts:
                postText = postText[:1020] + "..."
                post_string = post_string[:1020] + "..."

                if len(img_files) == 0:
                    sendToTelegram(postText)
                elif len(img_files) == 1:
                    bot.sendPhoto(chat_id, open(str(img_files[0].media.name), "rb"), caption=postText)
                else:
                    # message_info = sendToTelegram(post_string)
                    message_info = bot.sendMediaGroup(chat_id, tuple(img_files))
                    # print(message_info)
                    # message_info = json.loads(str(message_info))
                    # try:
                    #     message_id = message_info['message_id']
                    # except:
                    #     message_id = message_info[0]['message_id']
                    
                    # print(message_id)

                    sendToTelegram(postText)
            
            # Try deleting img folder
            try:
                shutil.rmtree("img")
            except:
                print(traceback.format_exc())
        except:
            print(traceback.format_exc())

try:
    textToWrite = ""
    for post_id in post_ids:
        textToWrite += post_id + "\n"
    with open(REPO_NAME + "/posts/" + group_id + ".txt", "w") as f:
        f.write(textToWrite)
except:
    print(traceback.format_exc())

browser.quit()
