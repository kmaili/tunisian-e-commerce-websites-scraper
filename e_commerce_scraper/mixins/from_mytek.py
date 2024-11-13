import json
from time import sleep

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, Any

from typing import Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from e_commerce_scraper.mixins.utils import wait_for_element_to_be_clickable


class FromMytek:

    mytek_website= "mytek.tn"

    def _getSubCategoryMenus_mytek(self, levels):
        menus = []
        principal = levels[0]
        for level in levels[1:]:
            sub_categ_index = levels.index(level) + 1
            for item in range(1, level + 1):
                menu = self._driver.find_element(
                    By.XPATH,
                    f".//li[contains(@class, 'nav-{principal}-{sub_categ_index}-{item}')]//a",
                ).get_attribute('href')
                menus.append(menu)
        return menus

    def getProductsFromMytek(self, levels, nb_product_for_each_subcategory):
        self._driver.get("https://"+self.mytek_website)
        button = self._driver.find_element(
            By.XPATH, "//li[contains(@class, 'all-category-wrapper')]"
        )
        wait_for_element_to_be_clickable(self._driver, button).click()
        parent_categ_elem = self._driver.find_element(By.XPATH, f"//ul[contains(@class, 'vertical-list')]/li[{levels[0]}]")
        wait_for_element_to_be_clickable(self._driver, parent_categ_elem).click()
        menus = self._getSubCategoryMenus_mytek(levels)
        yield from self._getProductsCategory_mytek(menus, nb_product_for_each_subcategory)

    def _getProductsCategory_mytek(self, categs_links, nb_products):
        global_prods_links = []
        for categ_link in categs_links:
            self._driver.get(categ_link)

            prods_links = []
            while True:
                productsDivs = self._driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class,'products-list')]//li[contains(@class,'product-item')]",
                )
                for elem in productsDivs:
                    prod_link = (
                        elem
                        .find_element(By.CLASS_NAME, "product-item-link")
                        .get_attribute("href")
                    )
                    prods_links.append(prod_link)
                if len(prods_links) >= nb_products:
                    prods_links = prods_links[:nb_products]
                    break
                if not self._jump_to_next_page_mytek():
                    break
            global_prods_links.extend(prods_links)
        for link in global_prods_links:
            yield self._getSingleProduct_mytek(link)

    def _getSingleProduct_mytek(self, prod_link):
        self._driver.get(prod_link)

        ''' reference is used is data cleaning phase to removed duplicates  '''
        reference = self._driver.find_element(By.XPATH, "//div[@itemprop = 'sku']").text


        name = self._driver.find_element(By.XPATH, "//h1[@class='page-title']").text
        in_stock = (
            True
            if self._driver.find_element(
                By.XPATH, "//div[@itemprop='availability']"
            ).text
            == "En Stock"
            else False
        )
        price = self._driver.find_element(
            By.XPATH,
            "//div[@class = 'product-info-price']//div[contains(@class, 'price-final_price')]",
        ).text.replace(" DT", "")
        description = self._driver.find_element(
            By.XPATH, "//div[@itemprop='description']//p"
        ).text

        category = self._driver.find_element(By.XPATH, "//ul[@itemtype='https://schema.org/BreadcrumbList']/li[position()=last()-1]").text


        data = {
            "website": self.mytek_website,
            "product_reference_in_website": reference,
            "product_name": name,
            "product_category": category,
            "in_stock": in_stock,
            "product_price": price,
            "product_url": prod_link,
            "product_description": description,
            "availability": self._get_availability_mytek(),
            "technical_sheet": self._get_technical_sheet_mytek(),
            "product_images": self._get_product_images_mytek()
        }
        return data

    def _get_availability_mytek(self):
        disp_div = self._driver.find_element(
            By.XPATH, "//table[@class = 'tab_retrait_mag']"
        )
        places_divs = disp_div.find_elements(By.TAG_NAME, "tr")
        availabilities = dict()
        for place_div in places_divs:
            place_status = place_div.find_elements(By.TAG_NAME, "td")
            place = place_status[0]
            status = place_status[1]

            availabilities[place.text] = status.text
        return availabilities
    def _get_technical_sheet_mytek(self):
        switch_btn = self._driver.find_element(By.XPATH, "//a[text()='FICHE TECHNIQUE']")
        wait_for_element_to_be_clickable(self._driver, switch_btn).click()
        sleep(2)
        specs = self._driver.find_element(By.ID, "product-attribute-specs-table").find_elements(By.TAG_NAME, "tr")
        technical_data = dict()
        for spec in specs:
            key = spec.find_element(By.TAG_NAME, "th").text
            value = spec.find_element(By.TAG_NAME, "td").text
            technical_data[key] = value
        if len(technical_data.keys()) <= 1:
            self.logger.error("technical sheet not collected [mytek]")
        return technical_data

    def _jump_to_next_page_mytek(self):
        try:
            next_btn = self._driver.find_element(By.CLASS_NAME, "item pages-item-next".replace(" ", "."))
            wait_for_element_to_be_clickable(self._driver, next_btn).click()
            return True
        except:
            self.logger.info("failed to jump to next page")
            return False

    def _get_product_images_mytek(self):
        images_elems = self._driver.find_elements(By.XPATH, "//ol[@class='carousel-indicators list-inline']//img")
        return [img.get_attribute('src') for img in images_elems]