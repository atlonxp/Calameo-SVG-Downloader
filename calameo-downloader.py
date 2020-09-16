# --------------------------------------------------------------------------------------------------
#  Calameoassets Downloader                                                                        -
#  Copyright (c) 2020. Dr Watthanasak Jeamwatthanachai - All Rights Reserved                       -
# --------------------------------------------------------------------------------------------------
import time
from pathlib import Path

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

BASE_DIR = Path(__file__).parent.absolute()

driver = webdriver.Chrome(f"{BASE_DIR}/data/drivers/chromedriver")
driver.implicitly_wait(5)
wait = WebDriverWait(driver, 5)

calameoassets_url = 'https://p.calameoassets.com/'
header_curl = {
    'user-agent': driver.execute_script("return navigator.userAgent;")
}

driver.get('https://global.oup.com/education/support-learning-anywhere/key-resources-online/?region=uk')
book_tables = driver.find_elements(By.XPATH, '//div[@class="content_block full_width"]/div/table/tbody')

print('''
************************************
Collect list of books on the website
************************************
''')
books_list = []
for table in book_tables:
    tr = table.find_elements(By.TAG_NAME, 'tr')
    books = tr[-1].find_elements(By.TAG_NAME, 'a')
    for book in books:
        url = book.get_attribute('href')
        name = book.text
        books_list.append({'name': name, 'url': url})
        print(f'> {name} - {url}')

# In cases you want to download some particular books, you can manually define books_list
# books_list = [
#     'https://www.calameo.com/read/00077772151d39c98fbab?authid=5OmdpYZALnKk&region=uk',
#     'https://www.calameo.com/read/00077772164411330cf35?authid=K0Yqvcafhmlu&region=uk'
# ]

print('''
************************************
Download all books
************************************
''')
for book in books_list:
    print(f'> Go to {book["url"]}')
    driver.get(book['url'])
    iframe = driver.find_element_by_tag_name("iframe")
    driver.switch_to.frame(iframe)

    imgs = []
    counter = 0
    while len(imgs) == 0:
        imgs = driver.find_elements(By.XPATH, '//img[@class="page"]')
        time.sleep(1)
        counter += 1
        if counter > 20:
            raise Exception("Book ID is unreachable")
    
    imgs = driver.find_elements(By.XPATH, '//img[@class="page"]')
    book_id = imgs[0].get_attribute('src').replace(calameoassets_url, '').split('/')[0]
    print(f'\t* Book ID: {book_id}')

    Path(f'{BASE_DIR}/books/{book["name"]}').mkdir(parents=True, exist_ok=True)
    for page in range(1, 9999):
        filename = f'p{page}.svgz'
        url = f'{calameoassets_url}{book_id}/{filename}'
        response = requests.get(url, allow_redirects=True, headers=header_curl)
        if response.status_code != 200:
            break
        print(f'\t* {url}', end='\t...\t')
        open(f'{BASE_DIR}/books/{book["name"]}/{filename}', 'wb').write(response.content)
        print('saved')
driver.close()
driver.quit()
