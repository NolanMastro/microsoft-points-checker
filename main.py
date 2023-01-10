import os
import random
import traceback
import requests
import datetime
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

LOGIN="email1:password1,email2:password2,etc..."
URL="Your login url, you can get this by going to bing.com on a incognito window, than pressing the sign in button. Copy and put that link here."


options = webdriver.ChromeOptions()
options.add_argument("--headless")
ACCOUNTS = LOGIN.replace(" ", "").split(",")
APPRISE_ALERTS = False
BOT_NAME = "Points checker."
pointss = []

def login(EMAIL, PASSWORD, driver):
    # Find email and input it
    try:
        driver.find_element(By.XPATH, value='//*[@id="i0116"]').send_keys(EMAIL)
        driver.find_element(By.XPATH, value='//*[@id="i0116"]').send_keys(Keys.ENTER)
    except:
        try:
            username_field = driver.find_element(By.XPATH, value='//*[@id="i0116"]')
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(username_field)
            )
            username_field.send_keys(EMAIL)
            username_field.send_keys(Keys.ENTER)
        except:
            return False
    sleep(random.uniform(2, 4))
    try:
        message = driver.find_element(By.XPATH, value='//*[@id="usernameError"]').text
        if("microsoft account doesn't exist" in message.lower()):
            print(f"Microsoft account {EMAIL} doesn't exist. Skipping this account & moving onto the next in env...")
            return False
    except:
        pass
    # Check if personal/work prompt is present
    try:
        message = driver.find_element(By.XPATH, value='//*[@id="loginDescription"]').text
        if message.lower() == "it looks like this email is used with more than one account from microsoft. which one do you want to use?":
            try:
                personal = driver.find_element(By.XPATH, value='//*[@id="msaTileTitle"]')
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(personal)
                )
                personal.click()
                sleep(random.uniform(2, 4))
            except:
                print(f'Personal/Work prompt was present for account {EMAIL} but unable to get past it.')
                return False
    except:
        pass
    
    # Find password and input it
    try:
        driver.find_element(By.XPATH, value='//*[@id="i0118"]').send_keys(PASSWORD)
        driver.find_element(By.XPATH, value='//*[@id="i0118"]').send_keys(Keys.ENTER)
    except:
        try:
            password_field = driver.find_element(By.XPATH, value='//*[@id="i0118"]')
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(password_field)
            )
            password_field.send_keys(PASSWORD)
            password_field.send_keys(Keys.ENTER)
        except:
            print(f'Unable to find password field for account {EMAIL}')
            return False
    sleep(random.uniform(3, 6))
    try:
        message = driver.find_element(By.XPATH, value='//*[@id="passwordError"]').text
        if("password is incorrect" in message.lower()):
            print(f"Microsoft account {EMAIL} has incorrect password in LOGIN env. Skipping...")
            return False
    except:
        pass
    try:
        driver.find_element(By.XPATH, value='//*[@id="iNext"]').click()
    except:
        pass
    try:
        driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()
        return True
    except:
        try:
            message = driver.find_element(By.XPATH, value='//*[@id="StartHeader"]').text
            if message.lower() == "your account has been locked":
                print(f"uh-oh, your account {EMAIL} has been locked by Microsoft! Sleeping for 15 minutes to allow you to verify your account.\nPlease restart the bot when you've verified.")
                sleep(900)
                return False
        except NoSuchElementException as e:
            pass
        try:
            message = driver.find_element(By.XPATH, value='//*[@id="iPageTitle"]').text
            if message.lower() == "help us protect your account":
                print(f"uh-oh, your account {EMAIL} will need to manually add an alternative email address!\nAttempting to skip in 50 seconds, if possible...")
                sleep(50)
                driver.find_element(By.XPATH, value='//*[@id="iNext"]').click()
        except:
            driver.find_element(By.XPATH, value='//*[@id="idSIButton9"]').click()
        finally:
            driver.get('https://rewards.microsoft.com/')
        return True

def get_points(EMAIL, PASSWORD, driver):
    # Set initial value for points
    points = -1

    # Wait for the page to load
    driver.implicitly_wait(5)
    sleep(random.uniform(3, 5))

    try:
        # Go to the sign-in page
        driver.get('https://rewards.microsoft.com/Signin?idru=%2F')

        # Attempt to login
        if not login(EMAIL, PASSWORD, driver):
            return -404

        # If it's the first sign in, join Microsoft Rewards
        if driver.current_url == 'https://rewards.microsoft.com/welcome':
            try:
                join_rewards = driver.find_element(By.XPATH, value='//*[@id="start-earning-rewards-link"]')
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(join_rewards)
                )
                join_rewards.click()
                print(f'Joined Microsoft Rewards on account {EMAIL}')
            except:
                try:
                    driver.find_element(By.XPATH, value='//*[@id="start-earning-rewards-link"]').click()
                    print(f'Joined Microsoft Rewards on account {EMAIL}')
                except:
                    print(traceback.format_exc())
                    print("Got Rewards welcome page, but couldn't join Rewards.")
                    return -404

            # Check if the user has completed the welcome tour
            try:
                if driver.current_url == 'https://rewards.microsoft.com/welcometour':
                    driver.find_element(By.XPATH, value='//*[@id="welcome-tour"]/mee-rewards-slide/div/section/section/div/a[2]').click()
            except:
                driver.get('https://rewards.microsoft.com/')

        # Check if the user's account has been suspended
        if driver.title.lower() == 'rewards error':
            try:
                if "microsoft Rewards account has been suspended" in driver.find_element(By.XPATH, value='//*[@id="error"]/h1').text.lower() or "suspended" in driver.find_element(By.XPATH, value='/html/body/div[1]/div[2]/main/div/h1').text.lower():
                    print(f"\t{EMAIL} account has been suspended.")
                    return -404
            except:
                sleep(random.uniform(2, 4))
                driver.get('https://rewards.microsoft.com/')
    except Exception as e:
        driver.get('https://rewards.microsoft.com/')
        print(e)
        pass
    finally:
        sleep(random.uniform(8, 20))

    xpaths = [
        '//*[@id="balanceToolTipDiv"]/p/mee-rewards-counter-animation/span',
        '/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/mee-rewards-user-status-banner/div/div/div/div/div[2]/div[1]/mee-rewards-user-status-banner-item/mee-rewards-user-status-banner-balance/div/div/div/div/div/div/p/mee-rewards-counter-animation/span',
        '//*[@id="rewardsBanner"]/div/div/div[2]/div[1]/mee-rewards-user-status-banner-item/mee-rewards-user-status-banner-balance/div/div/div/div/div/p/mee-rewards-counter-animation/span',
        '/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/mee-rewards-user-status-banner/div/div/div/div/div[2]/div[1]/mee-rewards-user-status-banner-item/mee-rewards-user-status-banner-balance/div/div/div/div/div/p/mee-rewards-counter-animation/span',
        '//*[@id="rewardsBanner"]/div/div/div[3]/div[1]/mee-rewards-user-status-item/mee-rewards-user-status-balance/div/div/div/div/div/p[1]/mee-rewards-counter-animation/span',
        '//*[@id="rewardsBanner"]/div/div/div[2]/div[2]/span',
    ]

    for xpath in xpaths:
        try:
            element = driver.find_element(By.XPATH, xpath)
            points = element.text.strip().replace(',', '')
            
        except:
            pass
        try:
            element = driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/main/div/ui-view/mee-rewards-dashboard/main/mee-rewards-user-status-banner/div/div/div/div/div[2]/div[3]/mee-rewards-user-status-banner-item/mee-rewards-user-status-banner-dailypoint/div/div/div/div/div/div/p/mee-rewards-counter-animation/span')
            global pointsperday
            pointsperday = element.text.strip().replace(',', '')
        except:
            pass
    pointss.append(points)  
    
def main():
        threads = []
        for x in ACCOUNTS:
            colonIndex = x.index(":")+1
            EMAIL = x[0:colonIndex-1]
            PASSWORD = x[colonIndex:len(x)]
            driver = driver = webdriver.Chrome(service=Service(ChromeDriverManager(cache_valid_range=30).install()),options=options)
            t = threading.Thread(target=get_points, args=(EMAIL, PASSWORD, driver))
            threads.append(t)
            t.start()
            sleep(10)
        for thread in threads:
            thread.join()

wantedpoints = int(input('How many points do you want to get on all accounts?: '))


main()

os.system('cls')

count = 0
accountslength = len(ACCOUNTS)
while count <= (accountslength -1):
    accountspoints = pointss[count]
    accountspoints = int(accountspoints)
    needed = wantedpoints - accountspoints
    pointsperday = int(pointsperday)
    days = (wantedpoints-accountspoints)/pointsperday
    days = round(days)
    if pointsperday >= 430:
        maxed = "Yes."
    elif 390 <= pointsperday <= 429:
        maxed = "Not quite."
    else:
        maxed = "No."

    print(f"                                        {ACCOUNTS[count]}")
    print(f"                                          Points: {pointss[count]}")
    print(f"                                          Needs: {needed}")
    print(f"                                          Goal: {wantedpoints}")
    print(f"                                          Days: {days}")
    print(f"                                          Points Per Day: {pointsperday}")
    print(f"                                          Maxed out: {maxed}")
    print(" ")
    print(" ")
    count = count+1



sleep(90)
