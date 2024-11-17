from time import sleep
from selenium.webdriver.common.by import By

from e_commerce_scraper.mixins.utils import wait_for_element_to_be_clickable, wait_for_element_to_be_present, \
    wait_for_all_elements_to_be_present, wait_for_all_elements_to_be_visible


class FromMytek:

    mytek_website= "mytek.tn"

    def _getSubCategoryMenus_mytek(self, levels):

        menus = []
        principal = levels[0]
        for level in levels[1:]:
            sub_categ_index = levels.index(level) + 1
            for item in range(1, level + 1):
                menu = wait_for_element_to_be_present(self._driver, (
                    By.XPATH,
                    f".//li[contains(@class, 'nav-{principal}-{sub_categ_index}-{item}')]//a",
                )).get_attribute('href')
                menus.append(menu)
        return menus

    def getProductsFromMytek(self, levels, nb_product_for_each_subcategory):
        self._driver.get("https://"+self.mytek_website)
        wait_for_element_to_be_clickable(self._driver, (
            By.XPATH, "//li[contains(@class, 'all-category-wrapper')]"
        ))
        wait_for_element_to_be_clickable(self._driver, (By.XPATH, f"//ul[contains(@class, 'vertical-list')]/li[{levels[0]}]"))
        menus = self._getSubCategoryMenus_mytek(levels)
        yield from self._getProductsCategory_mytek(menus, nb_product_for_each_subcategory)

    def _getProductsCategory_mytek(self, categs_links, nb_products):
        global_prods_links = []
        for categ_link in categs_links:
            self._driver.get(categ_link)

            prods_links = []
            while True:
                productsDivs = wait_for_all_elements_to_be_present(self._driver, (
                    By.XPATH,
                    "//div[contains(@class,'products-list')]//li[contains(@class,'product-item')]",
                ))
                for elem in productsDivs:
                    prod_link = (
                        wait_for_element_to_be_present(elem, (By.CLASS_NAME, "product-item-link"))
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
        reference = wait_for_element_to_be_present(self._driver, (By.XPATH, "//div[@itemprop = 'sku']")).text


        name = wait_for_element_to_be_present(self._driver, (By.XPATH, "//h1[@class='page-title']")).text
        in_stock = (
            True
            if wait_for_element_to_be_present(self._driver, (
                By.XPATH, "//div[@itemprop='availability']")
            ).text
            == "En Stock"
            else False
        )
        price = wait_for_element_to_be_present(self._driver, (
            By.XPATH,
            "//div[@class = 'product-info-price']//div[contains(@class, 'price-final_price')]")
        ).text.replace(" DT", "")
        description = wait_for_element_to_be_present(self._driver, (
            By.XPATH, "//div[@itemprop='description']//p")
        ).text

        category = wait_for_element_to_be_present(self._driver, (By.XPATH, "//ul[@itemtype='https://schema.org/BreadcrumbList']/li[position()=last()-1]")).text


        data = {
            "website": self.mytek_website,
            "product_reference_in_website": reference,
            "product_name": name,
            "product_category": category,
            "product_manufacturer": self._get_manufacturer_mytek(),
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
        try:
            disp_div = wait_for_element_to_be_present(self._driver, (
                By.XPATH, "//table[@class = 'tab_retrait_mag']"
            ))
            places_divs = wait_for_all_elements_to_be_present(disp_div, (By.TAG_NAME, "tr"))
            availabilities = dict()
            for place_div in places_divs:
                place_status = wait_for_all_elements_to_be_present(place_div, (By.TAG_NAME, "td"))
                place = place_status[0]
                status = place_status[1]

                availabilities[place.text] = status.text
            return availabilities
        except:
           self.logger.info('availability data not collected')
           return {}

    def _get_technical_sheet_mytek(self):
        try:
            wait_for_element_to_be_clickable(self._driver, (By.XPATH, "//a[text()='FICHE TECHNIQUE']"))
            sleep(2)
            table = wait_for_element_to_be_present(self._driver, (By.ID, "product-attribute-specs-table"))
            self._driver.execute_script("arguments[0].scrollIntoView(true);", table)
            specs = wait_for_all_elements_to_be_present(table, (By.TAG_NAME, "tr"))
            technical_data = dict()
            for spec in specs:
                key = wait_for_element_to_be_present(spec, (By.TAG_NAME, "th")).text
                value = wait_for_element_to_be_present(spec, (By.TAG_NAME, "td")).text
                technical_data[key] = value
            if len(technical_data.keys()) <= 1:
                self.logger.error(f"collected technical sheet:{len(technical_data.keys())} [mytek]")

            return technical_data
        except:
            self.logger.info('technical sheet not collected')
            return {}

    def _jump_to_next_page_mytek(self):
        try:
            wait_for_element_to_be_clickable(self._driver, By.CLASS_NAME, "item pages-item-next".replace(" ", "."))
            return True
        except:
            self.logger.info("failed to jump to next page")
            return False

    def _get_product_images_mytek(self):
        try:
            images_elems = wait_for_all_elements_to_be_present(self._driver, (By.XPATH, "//div[@class='carousel-inner']//img"))
            return list(set([img.get_attribute('src') for img in images_elems]))
        except:
            return []


    def _get_manufacturer_mytek(self):
        try:
            return wait_for_element_to_be_present(self._driver, (By.XPATH, "//div[@class = 'product-info-stock-sku']//img")).get_attribute('alt').replace("powered-by-","")
        except:
            self.logger.info("manufacturer not loaded [mytek]")
            return ""