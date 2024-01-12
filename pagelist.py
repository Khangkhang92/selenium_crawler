from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import time
from loguru import logger
import os
import json




def _process_table(id,driver):
    table = driver.find_element(By.ID,id)
    time.sleep(3)
    header_elements = table.find_elements(By.CSS_SELECTOR, 'thead th')
    header_values = [header.text.strip() for header in header_elements[1:]]  # Skip the first header with display:none
    rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr')
    results_dict_list = []
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, 'td')
        row_data = {header_values[i]: cells[i + 1].text if len(cells) > i + 1 else None for i in range(len(header_values))}
        row_data.pop("Hiển thị nhãn", None)
        row_data.pop("", None)
        results_dict_list.append(row_data)
    return results_dict_list      


def _mapping_data(order_number,driver):
        data_list = driver.find_elements(By.CLASS_NAME,"content-view")

        file_path = "crawed.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as json_file:
                existing_data = json.load(json_file)
        except FileNotFoundError:
            existing_data = []

        existing_data.append({  
                'STT' :order_number,
                'Tên thức ăn': data_list[0].text,
                'Công dụng' : data_list[1].text,
                'Dạng' : data_list[2].text,
                'Màu' : data_list[3].text,
                'Ký hiệu tiêu chuẩn' : data_list[4].text,
                'Mã số công nhận' :data_list[5].text,
                'Nhà sản xuất' : data_list[6].text,
                'Địa chỉ sản xuất' : data_list[7].text,
                'Nước' : data_list[8].text,
                'Thời hạn hiệu lực':data_list[9].text,
                'Thành phần nguyên liệu' :data_list[-1].text,
                # 'Chỉ tiêu chất lượng' : _table_handler(chi_tieu_chat_luong_element),
                # 'Chỉ tiêu an toàn' : _table_handler(chi_tieu_an_toan_element),
                'Chỉ tiêu chất lượng' : _process_table('CCN-ChiTieuChatLuongTACN',driver),
                'Chỉ tiêu an toàn' : _process_table('CCN-ChiTieuVeSinhTACN',driver),
        })

        
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)


def handle_content_page(driver,body_rows)->None:
        content_rows = body_rows[1:-2]  
        for row in content_rows:
            cells = row.find_elements(By.XPATH,".//td")
            view_button = cells[10].find_element(By.XPATH,".//div")
            view_button.click()
            time.sleep(3)
            iframe_element = driver.find_element(By.XPATH, '//iframe[contains(@src, "/portaldvc/Pages/popup/view-thuc-an-chan-nuoi-public.aspx")]')
            order_number = cells[1].text
            driver.switch_to.frame(iframe_element)
            _mapping_data(order_number,driver)
            close_button = driver.find_element(By.XPATH,"//button")
            close_button.click()
            time.sleep(3)
            driver.switch_to.default_content()
            logger.info(row.text)


def main():
    driver = None
    try:    
            start_page = 33
            url = 'https://dichvucong.mard.gov.vn/portaldvc/Pages/danh-muc/dm-thuc-an-chan-nuoi-public.aspx'
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
            driver.get(url)
            tr_element = driver.find_element(By.XPATH, "//tbody")    
            body_rows = tr_element.find_elements(By.XPATH,"//tr")
            pages_count = body_rows[-1]
            other_page_buttons = pages_count.find_elements(By.XPATH, f"//*[contains(text(), '...')]")
            other_page_button = other_page_buttons[-1]
            current_page_element = pages_count.find_element(By.XPATH, './/span')
            current_page_number = int(current_page_element.text)

          
            while other_page_button.text == "..." and current_page_number < start_page: # walk through pages and do nothing until start_page
                try:
                    next_page = pages_count.find_element(By.XPATH, f".//*[contains(text(), '{current_page_number+1}')]")
                    next_page.click() 
                    time.sleep(3)
                    tr_element = driver.find_element(By.XPATH, "//tbody")    
                    body_rows = tr_element.find_elements(By.XPATH,"//tr")
                    pages_count = body_rows[-1]
                    other_page_buttons = pages_count.find_elements(By.XPATH, f"//*[contains(text(), '...')]")
                    other_page_button = other_page_buttons[-1]
                    current_page_element = pages_count.find_element(By.XPATH, './/span')
                    current_page_number = int(current_page_element.text)
                    logger.info(f"Current page number is {current_page_number}")
                
                except Exception as e:
                    other_page_button.click()
                    time.sleep(3)
                    tr_element = driver.find_element(By.XPATH, "//tbody")    
                    body_rows = tr_element.find_elements(By.XPATH,"//tr")
                    pages_count = body_rows[-1]
                    other_page_buttons = pages_count.find_elements(By.XPATH, f"//*[contains(text(), '...')]")
                    other_page_button = other_page_buttons[-1]
                    current_page_element = pages_count.find_element(By.XPATH, './/span')
                    current_page_number = int(current_page_element.text)
        
            tr_element = driver.find_element(By.XPATH, "//tbody")    
            body_rows = tr_element.find_elements(By.XPATH,"//tr")
            handle_content_page(driver,body_rows)
            pages_count = body_rows[-1]
            other_page_buttons = pages_count.find_elements(By.XPATH, f"//*[contains(text(), '...')]")
            other_page_button = other_page_buttons[-1]
            current_page_element = pages_count.find_element(By.XPATH, './/span')
            current_page_number = int(current_page_element.text)
            logger.info(f"Current page number is {current_page_number}")
            while other_page_button.text == "...":
                try:
                    next_page = pages_count.find_element(By.XPATH, f".//*[contains(text(), '{current_page_number+1}')]")
                    next_page.click() 
                    logger.info(f"Current page number is {current_page_number +1 }")
                    time.sleep(3)
                    tr_element = driver.find_element(By.XPATH, "//tbody")    
                    body_rows = tr_element.find_elements(By.XPATH,"//tr")
                    
                    pages_count = body_rows[-1]
                    other_page_buttons = pages_count.find_elements(By.XPATH, f"//*[contains(text(), '...')]")
                    other_page_button = other_page_buttons[-1]
                    current_page_element = pages_count.find_element(By.XPATH, './/span')
                    current_page_number = int(current_page_element.text)
                    handle_content_page(driver,body_rows)
                    logger.info(f"Crawed page {current_page_number}")
                
                except Exception as e:
                    other_page_button.click()
                    time.sleep(3)
                    logger.info(f"Current page number is {current_page_number +1 }")
                    tr_element = driver.find_element(By.XPATH, "//tbody")    
                    body_rows = tr_element.find_elements(By.XPATH,"//tr")
                    pages_count = body_rows[-1]
                    other_page_buttons = pages_count.find_elements(By.XPATH, f"//*[contains(text(), '...')]")
                    other_page_button = other_page_buttons[-1]
                    current_page_element = pages_count.find_element(By.XPATH, './/span')
                    current_page_number = int(current_page_element.text)
                    handle_content_page(driver,body_rows)              
                   
    except Exception as e:
        print(e)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()



