from selenium import webdriver
import pickle, time, traceback
import onetimepass as otp
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import creds
import telepot
from telepot.loop import MessageLoop
bot = telepot.Bot(creds.bot_token) # Telegram Bot Token 
chat_id = creds.chat_id

chrome_options = Options()
chrome_options.add_argument("--user-data-dir=chrome-data")
# chrome_options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 2})

browser = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)

def authenticate():
    try:
        
        browser.get('https://mbasic.facebook.com')
        #chrome_options.add_argument("user-data-dir=chrome-data")

        fb_username = creds.email
        fb_password = creds.password

        # username = browser.find_element_by_id("email")
        # password = browser.find_element_by_id("pass")
        # buttons = browser.find_elements_by_tag_name("div")

        # for div in buttons:
        #     # print(div.text)
        #     # print("\n\n")
        #     if "log in" == str(div.text).lower():
        #         print("found")
        #         submit = div
        #         break

        inputFields = browser.find_elements_by_tag_name("input")

        for element in inputFields:
            try:
                temp = element.get_attribute("name")

                if temp == "email":
                    username = element
                elif temp == "pass":
                    password = element
                elif temp == "login":
                    submit = element
            except Exception:
                print(str(traceback.format_exc()))
        
        
        username.send_keys(fb_username)
        password.send_keys(fb_password)

        submit.click()

        wait = WebDriverWait( browser, 5)
    except:
        pass
    else:
        # bot.sendMessage(chat_id, "Passed login phase...")
        print("Passed login phase")

    browser.save_screenshot("screenshot.png")
    # bot.sendPhoto(chat_id, photo=open('screenshot.png', 'rb'))
    print(browser.current_url)

    if 'facebook.com/checkpoint' in browser.current_url:
        # bot.sendMessage(chat_id, "Waiting for 2FA Code: -->")
        print("Enter 2FA Code: -->")
        time.sleep(3)
        tfacode = "00000"
        while(len(str(tfacode)) < 6):
            time.sleep(5)
            tfacode = otp.get_totp(creds.tfa_hash)
            print(tfacode)
        try:
            browser.find_element_by_id('approvals_code').send_keys(tfacode)
            browser.find_element_by_id('checkpointSubmitButton').click()
            time.sleep(2)
            browser.find_element_by_id('checkpointSubmitButton').click()
            time.sleep(3)
            browser.save_screenshot("screenshot.png")
            # bot.sendPhoto(chat_id, photo=open('screenshot.png', 'rb'))
        except:
            pass
    
    if 'facebook.com/checkpoint' in browser.current_url:
        try:
            browser.find_element_by_id('checkpointSubmitButton-actual-button').click()
            time.sleep(3)
            browser.find_element_by_id('checkpointSubmitButton-actual-button').click()
            time.sleep(3)
            browser.find_element_by_id('checkpointSubmitButton-actual-button').click()
            time.sleep(5)
            browser.save_screenshot("screenshot.png")
            # bot.sendPhoto(chat_id, photo=open('screenshot.png', 'rb'))
        except:
            pass

    time.sleep(4)
    browser.quit()

