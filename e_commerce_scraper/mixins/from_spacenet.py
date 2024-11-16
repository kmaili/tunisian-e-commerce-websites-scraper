from selenium.common import TimeoutException
from selenium.webdriver.common.by import By

from e_commerce_scraper.mixins.utils import wait_for_element_to_be_clickable, wait_for_all_elements_to_be_present, \
    wait_for_element_to_be_present, wait_for_all_elements_to_be_visible


class FromSpacenet:

    spacenet_website= "spacenet.tn"

    def _getSubCategoryMenus_spacenet(self, levels, parent_categ_elem):
        each_sub_categ_items_count = [4, 2, 5, 14, 3, 11, 4, 9]
        subs = []
        menus = wait_for_all_elements_to_be_present(parent_categ_elem, (By.XPATH, ".//ul[@class = 'level-3']/li/a"))

        for i in range(len(each_sub_categ_items_count)):
            sub = menus[
                  sum([_ for _ in each_sub_categ_items_count[:i]]):sum([_ for _ in each_sub_categ_items_count[:i]]) +
                                                                   each_sub_categ_items_count[i]]
            subs.append([item.get_attribute('href') for item in sub])
        result = []
        for sub, max in zip(subs, levels[1:]):
            result.extend(sub[:max])
        return result

    def getProductsFromSpacenet(self, levels, nb_product_for_each_subcategory):
        self._driver.get("https://"+self.spacenet_website)
        wait_for_element_to_be_clickable(self._driver, (
            By.XPATH, "//div[contains(@class, 'v-megameu-main')]"
        ))

        parent_categ_elem = self._driver.find_element(By.XPATH, f"//ul[contains(@class, 'sp_lesp')]/li[{levels[0]}]")
        #wait_for_element_to_be_clickable(self._driver, parent_categ_elem).click()
        menus = self._getSubCategoryMenus_spacenet(levels, parent_categ_elem)
        yield from self._getProductsCategory_spacenet(menus, nb_product_for_each_subcategory)

    def _getProductsCategory_spacenet(self, categs_links, nb_products):
        global_prods_links = []
        for categ_link in categs_links:
            self._driver.get(categ_link)

            prods_links = []
            while True:
                productsDivs = wait_for_all_elements_to_be_present(self._driver, (
                    By.XPATH,
                    "//div[@id = 'box-product-grid']//div[@class='left-product']/a",
                ))
                for elem in productsDivs:
                    prod_link = (
                        elem
                        .get_attribute("href")
                    )
                    prods_links.append(prod_link)
                if len(prods_links) >= nb_products:
                    prods_links = prods_links[:nb_products]
                    break
                if not self._jump_to_next_page_spacenet():
                    break
            global_prods_links.extend(prods_links)
        for link in global_prods_links:
            yield self._getSingleProduct_spacenet(link)

    def _getSingleProduct_spacenet(self, prod_link):
        self._driver.get(prod_link)
        ''' reference is used is data cleaning phase to removed duplicates  '''
        reference = wait_for_element_to_be_present(self._driver, (By.XPATH, "//div[@class = 'product-reference']/span")).text


        name = wait_for_element_to_be_present(self._driver, (By.XPATH, "//h1[@class='h1']")).text
        try:
            wait_for_element_to_be_present(self._driver, (
                By.XPATH, "//span[@class='product-availability']"
            ), 1)
            in_stock = False
        except TimeoutException:
            in_stock = True

        price = wait_for_element_to_be_present(self._driver, (
            By.XPATH,
            "//div[@class = 'current-price']"
        )).text.replace(" DT", "")
        description = wait_for_element_to_be_present(self._driver, (
            By.XPATH, "//div[@class = 'product-des']/p"
        )).text

        category = wait_for_element_to_be_present(self._driver, (By.XPATH, "//div[@class = 'breadcrumb-no-images']//ol/li[position()=last()-1]")).text

        data = {
            "website": self.spacenet_website,
            "product_reference_in_website": reference,
            "product_name": name,
            "product_manufacturer": self._get_manufacturer_spacenet(),
            "product_category": category,
            "in_stock": in_stock,
            "product_price": price,
            "product_url": prod_link,
            "product_description": description,
            "product_images": self._get_product_images_spacenet(),
            "availability": self._get_availability_spacenet(),
            "technical_sheet": self._get_technical_sheet_spacenet()
        }
        return data


    def _get_manufacturer_spacenet(self):
        try:
            return wait_for_element_to_be_present(self._driver, (By.XPATH, "//div[@class = 'product-manufacturer']//img")).get_attribute('alt')
        except:
            return ""
    def _get_availability_spacenet(self):
        disp_div = wait_for_element_to_be_present(self._driver, (
            By.XPATH, "//div[@class = 'magasin-table']"
        ))
        places = wait_for_all_elements_to_be_present(disp_div, (By.XPATH, ".//div[contains(@class, 'left-side')]"))
        values = wait_for_all_elements_to_be_present(disp_div, (By.XPATH, ".//div[contains(@class, 'right-side')]"))

        availabilities = dict()
        for key, value in zip(places, values):
            place = key.text
            status = value.text

            availabilities[place] = status
        return availabilities
    def _get_technical_sheet_spacenet(self):
        wait_for_element_to_be_clickable(self._driver, (By.XPATH, "//a[text() = 'Détails du produit']"))
        table = wait_for_element_to_be_present(
            self._driver, (By.XPATH, "//dl[@class = 'data-sheet']")
        )
        self._driver.execute_script("arguments[0].scrollIntoView(true);", table)
        keys = wait_for_all_elements_to_be_visible(self._driver, (By.XPATH, "//dl[@class = 'data-sheet']/dt"))
        values = wait_for_all_elements_to_be_visible(self._driver, (By.XPATH, "//dl[@class = 'data-sheet']/dd"))
        technical_data = dict()
        for key, value in zip(keys, values):
            technical_data[key.text] = value.text

        if len(technical_data.keys()) <= 1:
            self.logger.error(f"collected technical sheet:{len(technical_data.keys())} [spacenet]")
        return technical_data

    def _jump_to_next_page_spacenet(self):
        try:
            next_btn = wait_for_element_to_be_present(self._driver, (By.XPATH, "//nav[@class = 'pagination']//li[position()=last()]/a"))
            self._driver.get(next_btn.get_attribute('href'))
            return True
        except:
            self.logger.info(f"failed to jump to next page")
            return False

    def _get_product_images_spacenet(self):
        try:
            images_elems = wait_for_all_elements_to_be_present(self._driver, (By.XPATH, "//div[contains(@class, 'js-qv-product-images')]//img"), 3)
            return [img.get_attribute('src') for img in images_elems]
        except:
            return [wait_for_element_to_be_present(self._driver, (By.CLASS_NAME, "js-qv-product-cover")).get_attribute('src')]