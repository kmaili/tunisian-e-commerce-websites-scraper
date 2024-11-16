from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from abc import ABC, abstractmethod
from random import randint
from .config.base import ConfigReader
from selenium.webdriver.remote.webdriver import WebDriver

from .logging import LoggerFactory
from .mixins.from_mytek import FromMytek
from .mixins.from_spacenet import FromSpacenet
from .mixins.from_tunisianet import FromTunisianet
from .mixins.from_zoom import FromZoom

BASE_NAME = "mytek"


class Driver(ABC):
    def __init__(self, **kwargs) -> None:
        self._driver: WebDriver
        self._config: ConfigReader
        self.logger: LoggerFactory

    @abstractmethod
    def _init_driver(self) -> WebDriver:
        raise NotImplementedError

    def close(self) -> None:
        """This function will close the driver (navigator selenium) and COOKIE"""
        try:
            self._driver.delete_all_cookies()
            self._driver.close()
            self._driver.quit()
        except WebDriverException as e:
            print(f"An error occurred while closing the driver: {e}")


class EcommerceScraper(Driver, FromMytek, FromTunisianet, FromZoom, FromSpacenet):
    def __init__(self, **kwargs) -> None:
        FromMytek.__init__(self, **kwargs)
        FromTunisianet.__init__(self, **kwargs)

        super().__init__(**kwargs)
        base_path = kwargs.get("base_path", ".")
        self._config = ConfigReader(name=BASE_NAME, base_path=base_path)
        self._config.extend(**kwargs)
        self.logger = LoggerFactory(BASE_NAME, self._config).get_logger()
        self._driver = self._init_driver()

    def generate_user_agent(self) -> str:
        version = randint(89, 95)
        agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0 Safari/537.36"

        # agent = f"Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.2311.135 Mobile Safari/537.36"

        return agent

    def _parametiser(self) -> webdriver.ChromeOptions:
        options = webdriver.ChromeOptions()
        '''options.add_experimental_option("excludeSwitches", ["enable-logging"])
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False,
        }

        options.add_experimental_option("prefs", prefs)
        # enables = ['enable-automation', "enable-logging"]
        enables = ["enable-automation"]
        options.add_experimental_option("excludeSwitches", enables)
        options.add_argument("--lang=en-US")  # Set language to English (US)
        options.add_argument("--disable-blink-features")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--disable-blink-features=AutomationControlled")

        options.add_experimental_option("useAutomationExtension", False)

        agent = self.generate_user_agent()
        # print(f"agent : {agent}")
        header = f'--user-agent="{agent}"'
        options.add_argument(header)
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-notifications")
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        }
        options.add_experimental_option("prefs", prefs)

        if self._config("headless"):
            options.add_argument("headless")'''
        return options

    def _create_chromedriver(self) -> ChromeService:
        return ChromeService(executable_path=ChromeDriverManager().install())

    def _init_driver(self) -> WebDriver:
        """Initiate the driver"""
        driver: WebDriver
        options = self._parametiser()
        options.add_experimental_option(
            "prefs", {"intl.accept_languages": self._config("driver_language")}
        )

        if self._config("platform") == "LINUX":
            self.logger.info("Using Linux local Selenium")
            options.add_argument("--no-sandbox")
        else:
            self.logger.info("Using Windows local Selenium")
        if self._config("headless"):
            options.add_argument("headless")
        driver = webdriver.Chrome(
            executable_path=self._config("driver_path"), options=options
        )
        driver.execute_cdp_cmd("Page.setBypassCSP", {"enabled": True})
        return driver
