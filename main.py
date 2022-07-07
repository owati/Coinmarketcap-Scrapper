import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import selenium


PAGE_URL = 'https://coinmarketcap.com'


def url_gen(rows):
    '''
    Generates all the coins url from the page
    '''
    for row in rows:
        coin =  row.find_all('td')[2]
        yield coin.find('a')['href'] # gets the URL of the coin



def main() ->  None:
    file = open('test.csv', 'w')
    writer = csv.writer(file)
    try:
        for page in range(1,101): # iterate through all the pages
            session = HTMLSession()
            res = session.get(PAGE_URL + '?page=' + str(page))

            soup = BeautifulSoup(res.html.html, 'html.parser')
            rows = soup.find_all('tr')
            print(len(rows))

            for coin in url_gen(rows[1:]):
                driver = webdriver.Chrome()
                name = coin.split('/')[2] # the name of the coin from the url
                
                writer.writerow([name])

                new_url = f'{PAGE_URL}{coin}historical-data/' # the url for the historical data
                driver.get(new_url)
                check = None
                try:
                    check = WebDriverWait(driver, 30).until(  # wait until the data has been rendered
                        EC.text_to_be_present_in_element_attribute((By.TAG_NAME, 'td'), 'style','text-align: left;')
                    )
                except Exception as e: # the page loaded to slow
                    print(e)
                    driver.close()

                if check:
                    coin_html = driver.execute_script('''
                    const html = document.querySelector('html');
                    return html.innerHTML
                    ''')
                    coin_soup = BeautifulSoup(coin_html, 'html.parser')
                    coin_rows = coin_soup.find_all('tr')    

                    headers = [head.text for head in coin_rows[0].find_all('th')] # finds the headers of the table

                    writer.writerow(headers)

                    for row in coin_rows[1:]:
                        coin_data = []
                        tds = row.find_all('td') # gets the individual element in each row
                        for data in tds:
                            coin_data.append(data.text)
                        writer.writerow(coin_data)

                    driver.close()
                    writer.writerow([''])
                break
            break

                    

    except Exception as e:
        # handle exceptions
        print(e)

    finally:
        file.close()


                
                
                




if __name__ == '__main__':
    main()