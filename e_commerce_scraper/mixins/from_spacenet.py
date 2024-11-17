from selenium.common import TimeoutException
from selenium.webdriver.common.by import By

from e_commerce_scraper.mixins.utils import wait_for_element_to_be_clickable, wait_for_all_elements_to_be_present, \
    wait_for_element_to_be_present, wait_for_all_elements_to_be_visible, get_text_by_javascript


class FromSpacenet:
    spacenet_website = "spacenet.tn"

    def _getSubCategoryMenus_spacenet(self, levels):
        self.logger.info("start selecting the target categories ...")

        bigs = []
        bigs_categs = wait_for_all_elements_to_be_present(self._driver, (By.XPATH, "//ul[@class='nav navbar-nav  menu sp_lesp level-1']/li"))
        for bb in bigs_categs:
            big_categ_name = get_text_by_javascript(self._driver, wait_for_element_to_be_present(bb, (By.TAG_NAME, "a"))).strip().replace('  ','').replace('\n','')
            br = []
            ss = wait_for_all_elements_to_be_present(bb, (By.XPATH, "./div/ul/li"))
            for elem in ss:
                sub_name = get_text_by_javascript(self._driver, wait_for_element_to_be_present(elem, (By.XPATH, ".//a"))).strip().replace('  ','').replace('\n','')
                categ_subs = []
                try:
                    for mm in wait_for_all_elements_to_be_present(elem, (By.XPATH, ".//li/a"), 1):
                        categ_subs.append(mm.get_attribute('href'))
                except:
                    pass
                br.append({
                    "categ": sub_name,
                    "count": len(categ_subs),
                    "menus": categ_subs
                })
            bigs.append({
                "big": big_categ_name,
                "categs": br
            })
        bigs = list({item["big"].replace(' ',''): item for item in bigs}.values())
        target_parent_categ = bigs[levels[0]-1]
        result = []
        for sub, count in zip(target_parent_categ["categs"], levels[1:]):
            result.extend(sub["menus"][:count])
            if count > len(sub["menus"]):
                self.logger.info("sub-category index out of range ... will take the whole list")


        self.logger.info(f"{len(result)} categories selected")
        return result

    def getProductsFromSpacenet(self, levels, nb_product_for_each_subcategory):
        self._driver.get("https://" + self.spacenet_website)
        wait_for_element_to_be_clickable(self._driver, (
            By.XPATH, "//div[contains(@class, 'v-megameu-main')]"
        ))

        menus = self._getSubCategoryMenus_spacenet(levels)
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
        reference = wait_for_element_to_be_present(self._driver,
                                                   (By.XPATH, "//div[@class = 'product-reference']/span")).text

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

        category = wait_for_element_to_be_present(self._driver, (
        By.XPATH, "//div[@class = 'breadcrumb-no-images']//ol/li[position()=last()-1]")).text

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
            return wait_for_element_to_be_present(self._driver, (
            By.XPATH, "//div[@class = 'product-manufacturer']//img")).get_attribute('alt')
        except:
            return ""

    def _get_availability_spacenet(self):
       try:
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
       except:
           self.logger.info('availability data not collected')
           return {}

    def _get_technical_sheet_spacenet(self):
        try:
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

            return technical_data
        except:
            self.logger.info('technical sheet not collected')
            return {}

    def _jump_to_next_page_spacenet(self):
        try:
            next_btn = wait_for_element_to_be_present(self._driver, (
            By.XPATH, "//nav[@class = 'pagination']//li[position()=last()]/a"))
            self._driver.get(next_btn.get_attribute('href'))
            return True
        except:
            self.logger.info("failed to jump to next page")
            return False

    def _get_product_images_spacenet(self):
        try:
            images_elems = wait_for_all_elements_to_be_present(self._driver, (
            By.XPATH, "//div[contains(@class, 'js-qv-product-images')]//img"), 3)
            return [img.get_attribute('src') for img in images_elems]
        except:
            try:
                return [
                    wait_for_element_to_be_present(self._driver, (By.CLASS_NAME, "js-qv-product-cover")).get_attribute(
                        'src')]
            except:
                self.logger("product images not collected")
                return []
