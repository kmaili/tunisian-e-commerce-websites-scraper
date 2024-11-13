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


class FromZoo:

    zoom_website= "zoom.com.tn"

    def _getSubCategoryMenus_zoom(self, levels, parent_categ_elem):
        each_sub_categ_items_count = [8, 6, 4, 5, 3, 4, 11, 3, 7]
        menus = parent_categ_elem.find_elements(By.XPATH, ".//ul[@class='ets_mm_categories']/li/a")
        subs = []
        for i in range(len(each_sub_categ_items_count)):
            sub = menus[
                  sum([_ for _ in each_sub_categ_items_count[:i]]):sum([_ for _ in each_sub_categ_items_count[:i]]) +
                                                                   each_sub_categ_items_count[i]]
            subs.append([item.get_attribute('href') for item in sub])
        result = []
        for sub, max in zip(subs, levels[1:]):
            result.extend(sub[:max])
        return result

    def getProductsFromZoom(self, levels, nb_product_for_each_subcategory):
        self._driver.get("https://"+self.zoom_website)
        button = self._driver.find_element(
            By.XPATH, "//ul[contains(@class, 'mm_menus_ul')]/li[2]"
        )
        wait_for_element_to_be_clickable(self._driver, button).click()

        parent_categ_elem = self._driver.find_element(By.XPATH, f"//ul[contains(@class, 'mm_columns_ul_tab')]/li[{levels[0]}]")
        wait_for_element_to_be_clickable(self._driver, parent_categ_elem).click()

        menus = self._getSubCategoryMenus_zoom(levels, parent_categ_elem)
        yield from self._getProductsCategory_zoom(menus, nb_product_for_each_subcategory)

    def _getProductsCategory_zoom(self, categs_links, nb_products):
        global_prods_links = []
        for categ_link in categs_links:
            self._driver.get(categ_link)

            prods_links = []
            sleep(1)
            while True:
                productsDivs = self._driver.find_elements(
                    By.XPATH,
                    "//div[@class = 'product-thumbnail']/a",
                )
                for elem in productsDivs:
                    prod_link = (
                        elem
                        .get_attribute("href")
                    )
                    prods_links.append(prod_link)
                if len(prods_links) >= nb_products:
                    prods_links = prods_links[:nb_products]
                    break
                if not self._jump_to_next_page_zoom():
                    break
            global_prods_links.extend(prods_links)
        for link in global_prods_links:
            yield self._getSingleProduct_zoom(link)

    def _getSingleProduct_zoom(self, prod_link):
        self._driver.get(prod_link)
        ''' reference is used is data cleaning phase to removed duplicates  '''
        reference = self._driver.find_element(By.XPATH, "//div[contains(@class, 'product-reference')]/span").text


        name = self._driver.find_element(By.XPATH, "//span[@class='item-name']").text
        in_stock = (
            True
            if "En stock" in self._driver.find_element(
                By.XPATH, "//span[@id='product-availability']"
            ).text

            else False
        )
        price = self._driver.find_element(
            By.XPATH,
            "//span[contains(@class, 'current-price-value')]",
        ).text.replace(" DT", "")
        description = self._driver.find_element(
            By.XPATH, "//div[contains(@class, 'product-description-short')]"
        ).text

        current_url = self._driver.current_url.replace("https://zoom.com.tn/","")
        category = current_url[:current_url.index('/')]

        data = {
            "website": self.zoom_website,
            "product_reference_in_website": reference,
            "product_name": name,
            "product_category": category,
            "in_stock": in_stock,
            "product_price": price,
            "product_url": prod_link,
            "product_description": description,
            "product_images": self._get_product_images_zoom(),
            "availability": [],
            "technical_sheet": self._get_technical_sheet_zoom()
        }
        return data

    def _get_availability_zoom(self):
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
    def _get_technical_sheet_zoom(self):
        table = self._driver.find_element(By.XPATH, "//section[@class = 'product-features']")
        keys = table.find_elements(By.TAG_NAME, "dt")
        values = table.find_elements(By.TAG_NAME, "dd")
        technical_data = dict()
        for key, value in zip(keys, values):
            technical_data[key.text] = value.text

        if len(technical_data.keys()) <= 1:
            self.logger.error("technical sheet not collected [zoom]")
        return technical_data

    def _jump_to_next_page_zoom(self):
        try:
            next_btn = self._driver.find_element(By.CLASS_NAME, "next js-search-link".replace(" ", "."))
            wait_for_element_to_be_clickable(self._driver, next_btn).click()
            return True
        except:
            self.logger.info("failed to jump to next page")
            return False

    def _get_product_images_zoom(self):
        images_elems = self._driver.find_elements(By.XPATH, "//ul[@class='product-images']//img")
        return [img.get_attribute('src') for img in images_elems]