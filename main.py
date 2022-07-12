import time
from configparser import ConfigParser

import winsound
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth


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

        do_refresh = "X"
        for x in [1, 6, 13]:
            WebDriverWait(self.browser, 9999).until(EC.presence_of_element_located((By.XPATH, '//*[@id="LocationId"]')))
            WebDriverWait(self.browser, 9999).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="LocationId"]')))
            select_center = Select(self.browser.find_element_by_xpath('//*[@id="LocationId"]'))
            select_center.select_by_index(x)
            time.sleep(2)
            if "There are no open seats available for selected center" in self.browser.page_source:
                print(f"There are no seats in {select_center.options[x].text}")
            else:
                if EC.element_to_be_clickable((By.XPATH, '//*[@id="VisaCategoryId"]')):
                    select_category = Select(self.browser.find_element(by=By.XPATH, value='//*[@id="VisaCategoryId"]'))
                    select_category.select_by_value('302')
                    time.sleep(2)
                    if "There are no open seats available for selected center" in self.browser.page_source:
                        print(f"There are no seats in {select_center.options[x].text}")
                    else:
                        print(f"There are some seats in {select_center.options[x].text}")
                        do_refresh = ""
                        selected_visa = "X"
                        break
                else:
                    print(f"Error")
                    self.check_appointment(trial + 1)

        if do_refresh is not None:
            time.sleep(60)
            self.check_appointment(trial + 1)
        else:
            if selected_visa is None:
                WebDriverWait(self.browser, 9999).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="VisaCategoryId"]')))
                select = Select(self.browser.find_element(by=By.XPATH, value='//*[@id="VisaCategoryId"]'))
                select.select_by_value('302')

            winsound.Beep(440, 200000)

            WebDriverWait(self.browser, 600).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="dvEarliestDateLnk"]')))
            WebDriverWait(self.browser, 9999).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="dvEarliestDateLnk"]')))

            # WebDriverWait(self.browser, 9999).until(
            #     EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Continue']")))

    def login(self):
        self.browser.get(self.url)

        if "You are now in line." in self.browser.page_source:
            print("You are now in queue.")

        WebDriverWait(self.browser, 9999).until(EC.presence_of_element_located((By.NAME, 'EmailId')))

        self.browser.find_element(by=By.NAME, value='EmailId').send_keys(self.email_str)
        self.browser.find_element(by=By.NAME, value='Password').send_keys(self.pwd_str)

        while "Schedule Appointment" not in self.browser.page_source:
            time.sleep(1)
        else:
            WebDriverWait(self.browser, 9999).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="Accordion1"]/div/div[2]/div/ul/li[1]/a')))
            print("Successfully logged in!")
            time.sleep(3)
            self.browser.find_element(by=By.XPATH,
                                      value='//*[@id="Accordion1"]/div/div[2]/div/ul/li[1]/a').click()

        self.check_appointment(1)


if __name__ == '__main__':
    MainClass = MainClass()
    MainClass.start()
