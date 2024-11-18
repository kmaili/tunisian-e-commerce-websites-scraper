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

BASE_NAME = "e-commerce_scraper"


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

        super().__init__(**kwargs)
        base_path = kwargs.get("base_path", ".")
        self._config = ConfigReader(name=BASE_NAME, base_path=base_path)
        self._config.extend(**kwargs)
        self.logger = LoggerFactory(BASE_NAME, self._config).get_logger()
        self._driver = self._init_driver()



    def _init_driver(self) -> WebDriver:
        driver: WebDriver
        options = webdriver.ChromeOptions()
        if self._config("remote"):
            self.logger.info("using selenium on remote mode")
            driver = webdriver.Remote(
                command_executor=self._config("remote_url"),
                desired_capabilities={
                    "javascriptEnabled": True,
                    "goog:loggingPrefs": {"performance": "ALL"},
                    "se:vncEnabled": True,
                },
                options=options,
            )
            driver.maximize_window()
            return driver
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
        driver.maximize_window()
        return driver
