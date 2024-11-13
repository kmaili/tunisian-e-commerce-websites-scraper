import json
from time import sleep

from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, Any

from typing import Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from e_commerce_scraper.mixins.utils import wait_for_element_to_be_clickable, get_text_by_javascript


class FromTunisianet:

    tunisianet_website = "tunisianet.com.tn"

    def _getSubCategoryMenus_tunisianet(self, levels, parent_categ_elem):
        each_sub_categ_items_count = [3, 11, 5, 2, 0, 0, 0, 14]
        menus = parent_categ_elem.find_elements(By.XPATH, ".//li[contains(@class,'item-header')]/following-sibling::li[not(contains(@class, 'item-header'))]//a")
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

    def getProductsFromTunisianet(self, levels, nb_product_for_each_subcategory):
        self._driver.get("https://"+self.tunisianet_website)
        parent_categ_elem = self._driver.find_element(By.XPATH, f"//ul[contains(@class, 'menu-content')]/li[{levels[0]}]")

        menus = self._getSubCategoryMenus_tunisianet(levels=levels, parent_categ_elem=parent_categ_elem)
        yield from self._getProductsCategory_tunisianet(menus, nb_product_for_each_subcategory)

    def _getProductsCategory_tunisianet(self, categs_links, nb_products):
        global_prods_links = []
        for categ_link in categs_links:
            self._driver.get(categ_link)
            prods_links = []
            while True:
                productsDivs = self._driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class,'item-product')]",
                )
                for elem in productsDivs:
                    prod_link = (
                        elem
                        .find_element(By.XPATH, ".//h2[contains(@class, 'h3 product-title')]//a")
                        .get_attribute("href")
                    )
                    prods_links.append(prod_link)
                if len(prods_links) >= nb_products:
                    prods_links = prods_links[:nb_products]
                    break
                if not self._jump_to_next_page_tunisianet():
                    break
            global_prods_links.extend(prods_links)

        for link in global_prods_links:
            yield self._getSingleProduct_tunisianet(link)

    def _getSingleProduct_tunisianet(self, prod_link):
        self._driver.get(prod_link)

        ''' reference is used is data cleaning phase to removed duplicates  '''
        reference = self._driver.find_element(By.XPATH, "//span[@itemprop = 'sku']").text


        name = self._driver.find_element(By.XPATH, "//h1[@itemprop='name']").text
        in_stock = (
            True
            if self._driver.find_element(
                By.XPATH, "//span[@class='in-stock']"
            ).text
            == "En stock"
            else False
        )
        price = self._driver.find_element(
            By.XPATH,
            "//span[@itemprop = 'price']",
        ).text.replace(" DT", "")
        description = self._driver.find_element(
            By.XPATH, "//div[@itemprop='description']"
        ).text

        category = self._driver.find_element(By.XPATH, "//ol[@itemtype='http://schema.org/BreadcrumbList']/li[position()=last()-1]").text


        data = {
            "website": self.tunisianet_website,
            "product_reference_in_website": reference,
            "product_name": name,
            "product_category": category,
            "in_stock": in_stock,
            "product_price": price,
            "product_url": prod_link,
            "product_description": description,
            "availability": self._get_availability_tunisianet(),
            "technical_sheet": self._get_technical_sheet_tunisianet(),
            "product_images": self._get_product_images_tunisianet()
        }
        return data

    def _get_availability_tunisianet(self):
        disp_div = self._driver.find_element(
            By.ID, "product-availability-store-mobile"
        )
        places_avail_cols = disp_div.find_elements(By.XPATH, ".//div[contains(@class, 'stores')]")
        availabilities = dict()
        places_elems = places_avail_cols[0].find_elements(By.XPATH, ".//div[contains(@class, 'store-availability')]")
        avail_elems = places_avail_cols[1].find_elements(By.XPATH, ".//div[contains(@class, 'store-availability')]")
        for place_elem, avail_elem in zip(places_elems, avail_elems):
            place = get_text_by_javascript(self._driver, place_elem)
            status = get_text_by_javascript(self._driver, avail_elem)
            availabilities[place] = status
        return availabilities
    def _get_technical_sheet_tunisianet(self):

        details_btn = self._driver.find_element(By.XPATH, "//li[contains(@class, 'pdetail')]")
        wait_for_element_to_be_clickable(self._driver, details_btn).click()

        sleep(2)

        table = self._driver.find_elements(By.CLASS_NAME, "product-features")[0]
        keys = table.find_elements(By.TAG_NAME, "dt")
        values = table.find_elements(By.TAG_NAME, "dd")
        technical_data = dict()
        for key, value in zip(keys, values):
            technical_data[key.text] = value.text

        if len(technical_data.keys()) <= 1:
            self.logger.error("technical sheet not collected [tunisianet]")
        return technical_data


    def _get_product_images_tunisianet(self):
        images_elems = self._driver.find_elements(By.XPATH, "//ul[contains(@class, 'js-qv-product-images')]//img")
        return [img.get_attribute('src') for img in images_elems]
    def _jump_to_next_page_tunisianet(self):
        try:
            next_btn = self._driver.find_element(By.XPATH, "//ul[contains(@class, 'page-list')]/li[position()=last()]")
            wait_for_element_to_be_clickable(self._driver, next_btn).click()
            return True
        except Exception as e:
            self.logger.info(f"failed to jump to next page: {e}")
            return False
