

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, Any

from typing import Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from e_commerce_scraper.mixins.utils import wait_for_element_to_be_clickable, wait_for_all_elements_to_be_present, \
    wait_for_element_to_be_present, wait_for_all_elements_to_be_visible, get_text_by_javascript


class FromZoom:

    zoom_website= "zoom.com.tn"

    def _getSubCategoryMenus_zoom(self, levels):

        self.logger.info("start selecting the target categories ...")

        bigs = []
        bigs_categs = wait_for_all_elements_to_be_present(self._driver, (By.XPATH, "//ul[contains(@class, 'mm_columns_ul')]/li"))
        for bb in bigs_categs:
            big_categ_name = get_text_by_javascript(self._driver, wait_for_element_to_be_present(bb, (By.XPATH, "./div/span"))).strip().replace('  ','').replace('\n','')
            br = []
            ss = wait_for_all_elements_to_be_present(bb, (By.XPATH, ".//div[@class = 'ets_mm_block_content']"))
            for elem in ss:
                sub_name = get_text_by_javascript(self._driver, wait_for_element_to_be_present(elem, (By.XPATH, "..//span[@class='h4']"))).strip().replace('  ','').replace('\n','')
                categ_subs = []
                try:
                    for mm in wait_for_all_elements_to_be_present(elem, (By.XPATH, "..//div[@class = 'ets_mm_block_content']//li/a"), 1):
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
        target_parent_categ = bigs[levels[0]-1]
        result = []
        for sub, count in zip(target_parent_categ["categs"], levels[1:]):
            result.extend(sub["menus"][:count])
            if count > len(sub["menus"]):
                self.logger.info("sub-category index out of range ... will take the whole list")

        self.logger.info(f"{len(result)} categories selected")
        return result


    def getProductsFromZoom(self, levels, nb_product_for_each_subcategory):
        #self._driver.get("https://"+self.zoom_website)
        wait_for_element_to_be_clickable(self._driver, (
            By.XPATH, "//ul[contains(@class, 'mm_menus_ul')]/li[2]"
        ))
        parent_elem_locator = By.XPATH, f"//ul[contains(@class, 'mm_columns_ul_tab')]/li[{levels[0]}]"
        wait_for_element_to_be_clickable(self._driver, parent_elem_locator)

        menus = self._getSubCategoryMenus_zoom(levels)
        yield from self._getProductsCategory_zoom(menus, nb_product_for_each_subcategory)

    def _getProductsCategory_zoom(self, categs_links, nb_products):
        global_prods_links = []
        for categ_link in categs_links:
            self._driver.get(categ_link)

            prods_links = []
            while True:
                productsDivs = wait_for_all_elements_to_be_present(self._driver, (
                    By.XPATH,
                    "//div[@class = 'product-thumbnail']/a",
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
                if not self._jump_to_next_page_zoom():
                    break
            global_prods_links.extend(prods_links)
        for link in global_prods_links:
            yield self._getSingleProduct_zoom(link)

    def _getSingleProduct_zoom(self, prod_link):
        self._driver.get(prod_link)
        ''' reference is used is data cleaning phase to removed duplicates  '''
        reference = wait_for_element_to_be_present(self._driver, (By.XPATH, "//div[contains(@class, 'product-reference')]/span")).text


        name = wait_for_element_to_be_present(self._driver, (By.XPATH, "//span[@class='item-name']")).text
        in_stock = (
            True
            if "En stock" in wait_for_element_to_be_present(self._driver, (
                By.XPATH, "//span[@id='product-availability']"
            )).text

            else False
        )
        price = wait_for_element_to_be_present(self._driver, (
            By.XPATH,
            "//span[contains(@class, 'current-price-value')]",
        )).text.replace(" TND", "")
        description = wait_for_element_to_be_present(self._driver, (
            By.XPATH, "//div[contains(@class, 'product-description-short')]"
        )).text

        current_url = self._driver.current_url.replace("https://zoom.com.tn/","")
        category = current_url[:current_url.index('/')]

        data = {
            "website": self.zoom_website,
            "product_reference_in_website": reference,
            "product_name": name,
            "product_category": category,
            "product_manufacturer": self._get_manufacturer_zoom(),
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
        disp_div = wait_for_element_to_be_present(self._driver, (
            By.XPATH, "//table[@class = 'tab_retrait_mag']"
        ))
        places_divs = wait_for_element_to_be_present(disp_div, (By.TAG_NAME, "tr"))
        availabilities = dict()
        for _ in places_divs:
            place_status = wait_for_all_elements_to_be_present(disp_div, (By.TAG_NAME, "td"))
            place = place_status[0]
            status = place_status[1]

            availabilities[place.text] = status.text
        return availabilities
    def _get_technical_sheet_zoom(self):
        table = self._driver.find_element(By.XPATH, "//section[@class = 'product-features']")
        self._driver.execute_script("arguments[0].scrollIntoView(true);", table)
        keys = wait_for_all_elements_to_be_visible(self._driver, (By.XPATH, "//section[@class = 'product-features']//dt"))
        values = wait_for_all_elements_to_be_visible(self._driver, (By.XPATH, "//section[@class = 'product-features']//dd"))
        technical_data = dict()
        for key, value in zip(keys, values):
            technical_data[key.text] = value.text

        if len(technical_data.keys()) <= 1:
            self.logger.error(f"collected technical sheet:{len(technical_data.keys())} [zoom]")
        return technical_data

    def _jump_to_next_page_zoom(self):
        try:
            wait_for_element_to_be_clickable(self._driver, (By.CLASS_NAME, "next js-search-link".replace(" ", ".")))
            return True
        except:
            self.logger.info("failed to jump to next page")
            return False

    def _get_product_images_zoom(self):
        try:
            images_elems = self._driver.find_elements(By.XPATH, "//ul[@class='product-images']//img")
            return [img.get_attribute('src') for img in images_elems]
        except:
            return [wait_for_element_to_be_present(self._driver, (By.CLASS_NAME, "img-fluid js-qv-product-cover js-main-zoom".replace(" ","."))).get_attribute(
                'src')]

    def _get_manufacturer_zoom(self):
        try:
            return wait_for_element_to_be_present(self._driver, (By.XPATH, "//a[@class = 'li-a']")).text
        except:
            self.logger.info("manufacturer not loaded [mytek]")
            return ""