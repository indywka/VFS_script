import time
from configparser import ConfigParser

import winsound
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth
from termcolor import colored

import mail


class MainClass:
    def __init__(self):
        config = ConfigParser()
        config.read('config.ini')

        self.url = config.get('VFS', 'url')
        self.email_str = config.get('VFS', 'email')
        self.pwd_str = config.get('VFS', 'password')
        self.interval = config.getint('DEFAULT', 'interval')

        self.options = webdriver.ChromeOptions()
        self.options.add_argument("start-maximized")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--disable-notifications')
        self.options.add_argument("--mute-audio")
        self.options.add_argument("--incognito")
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Linux; Android 6.0; HTC One M9 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.36")

    def open_browser(self):
        self.browser = webdriver.Chrome(options=self.options,
                                        executable_path=r'chromedriver.exe')
        self.browser.delete_all_cookies()
        stealth(self.browser,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)

    def start(self):
        self.open_browser()
        self.login()

    def check_appointment(self, trial):
        global do_refresh
        global selected_visa
        print(f"Retry No.{trial}")
        mail.telegram_bot_sendtext(f"Retry No.{trial}")

        do_refresh = "X"
        selected_visa = " "

        if "You are now in line." in self.browser.page_source:
            print(colored("You are now in queue.", 'yellow'))
            while "You are now in line." in self.browser.page_source:
                WebDriverWait(self.browser, 99999).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="LocationId"]')))
            else:
                mail.telegram_bot_sendtext(f"Try to login again: line 65")
                self.login()

        for x in [6, 0, 13, 0, 1, 0]:
            WebDriverWait(self.browser, 600).until(EC.presence_of_element_located((By.XPATH, '//*[@id="LocationId"]')))
            WebDriverWait(self.browser, 600).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="LocationId"]')))
            select_center = Select(self.browser.find_element_by_xpath('//*[@id="LocationId"]'))
            select_center.select_by_index(x)
            time.sleep(5)
            if x != 0:
                if "There are no open seats available for selected center" in self.browser.page_source:
                    print(colored(f"There are no seats in {select_center.options[x].text}", 'red'))
                else:
                    try:
                        WebDriverWait(self.browser, 30).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="VisaCategoryId"]')))
                        WebDriverWait(self.browser, 30).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="VisaCategoryId"]')))

                        select_category = Select(
                            self.browser.find_element(by=By.XPATH, value='//*[@id="VisaCategoryId"]'))
                        select_category.select_by_value('302')
                        time.sleep(3)

                        if "There are no open seats available for selected center" not in self.browser.page_source:
                            print(colored(f"There are some seats in {select_center.options[x].text}", 'green'))
                            do_refresh = ""
                            selected_visa = "X"
                            break

                    except:
                        if "There are no open seats available for selected center" in self.browser.page_source:
                            print(colored(f"There are no seats in {select_center.options[x].text}", 'red'))
                        else:
                            for y in range(2):
                                select_center.select_by_index(0)
                                time.sleep(10)
                                select_center.select_by_index(x)
                                time.sleep(10)

                            try:
                                WebDriverWait(self.browser, 10).until(
                                    EC.presence_of_element_located((By.XPATH, '//*[@id="VisaCategoryId"]')))
                                WebDriverWait(self.browser, 10).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="VisaCategoryId"]')))

                                select_category = Select(
                                    self.browser.find_element(by=By.XPATH, value='//*[@id="VisaCategoryId"]'))
                                select_category.select_by_value('302')
                                time.sleep(3)

                                if "There are no open seats available for selected center" not in self.browser.page_source:
                                    print(colored(f"There are some seats in {select_center.options[x].text}", 'green'))
                                    do_refresh = ""
                                    selected_visa = "X"
                                    break
                            except:

                                print(colored(f"Error. Press 'Continue'. ", 'red'))

                                button_continue = WebDriverWait(self.browser, 15).until(
                                    EC.presence_of_element_located((By.XPATH, '//*[@id="btnContinue"]')))
                                button_continue.click()
                                time.sleep(2)
                                self.check_appointment(trial + 1)

        if do_refresh is not None:
            time.sleep(60)
            self.check_appointment(trial + 1)
        else:
            mail.telegram_bot_sendtext(f"There are some seats in {select_center.options[x].text}")
            winsound.Beep(440, 3000)
            try:
                if selected_visa is None:
                    WebDriverWait(self.browser, 600).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="VisaCategoryId"]')))
                    select = Select(self.browser.find_element(by=By.XPATH, value='//*[@id="VisaCategoryId"]'))
                    select.select_by_value('302')

                WebDriverWait(self.browser, 60).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="dvEarliestDateLnk"]')))
                WebDriverWait(self.browser, 60).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="dvEarliestDateLnk"]')))
                self.browser.find_element_by_xpath((By.XPATH, '//*[@id="dvEarliestDateLnk"]')).click()
                winsound.Beep(440, 200000)
            except:
                self.check_appointment(trial + 1)

    def login(self):
        self.browser.get(self.url)

        if "You are now in line." in self.browser.page_source:
            print(colored("You are now in queue.", 'yellow'))

        WebDriverWait(self.browser, 99999).until(EC.presence_of_element_located((By.NAME, 'EmailId')))

        winsound.Beep(440, 2000)

        self.browser.find_element(by=By.NAME, value='EmailId').send_keys(self.email_str)
        self.browser.find_element(by=By.NAME, value='Password').send_keys(self.pwd_str)

        while "Schedule Appointment" not in self.browser.page_source:
            time.sleep(1)
        else:
            WebDriverWait(self.browser, 600).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="Accordion1"]/div/div[2]/div/ul/li[1]/a')))
            print(colored("Successfully logged in!", 'yellow'))
            time.sleep(3)
            self.browser.find_element(by=By.XPATH,
                                      value='//*[@id="Accordion1"]/div/div[2]/div/ul/li[1]/a').click()

        self.check_appointment(1)


if __name__ == '__main__':
    MainClass = MainClass()
    MainClass.start()
