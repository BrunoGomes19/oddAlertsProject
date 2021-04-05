# Here are included the imports
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
 
# Here Chrome  will be used
driver = webdriver.Chrome(ChromeDriverManager().install())
 
# URL of website
url = "https://www.oddalerts.com/login/"

# Email to login on the website
email = ""

# Password to login on the website
password = ""
 
# Opening the website
driver.get(url)

print("\nThe web scrapping process has started.")

# Insert the email and password on their own fields
driver.find_element_by_id("email").send_keys(email)
driver.find_element_by_id("password").send_keys(password)

# Wait until the submit button is available and click
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type=submit]"))).click()

time.sleep(0.5)

# Wait until the filters button is available and click
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/filters']"))).click()

# Click on the Filters button (Dropdown)
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#app-pane-id div div.saved-filters nav div.fill button"))).click()

# Click on the Testing option
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Testing"))).click()

time.sleep(0.5)

# Retrieve all filters available on the page
filters = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#app-pane-id > div > div.saved-filters > div > li > div.filter-actions > button")))

print("\nThere are " + str(len(filters)) + " filters to be retrieved.")

for x in range(1,len(filters) + 1):  
  # array with excel content
  arrOfContents = []

  # array to save the headers
  headers = []

  # Click on each open filter button
  WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#app-pane-id > div > div.saved-filters > div > li:nth-child(" + str(x) + ") > div.filter-actions > button"))).click()

  # Click on the Results button
  WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "i.fa-list-ul"))).click()

  # Get filter title
  filterTitle = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.saved-filters div.filter-view div.filter-menu div.title"))).text

  print("\nWe are retrieving information from the filter: " + filterTitle)

  # functionality to scrolldown to the bottom of the page
  display = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#app-pane-id div.fixture-list div.infinite-loading-container div:nth-child(3)"))).value_of_css_property("display")

  while display == 'none':
        
    element = driver.find_element_by_class_name("infinite-loading-container")
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(0.5)
    
    display = driver.find_element_by_tag_name("#app-pane-id div.fixture-list div.infinite-loading-container > div:nth-child(3)").value_of_css_property("display")
    display2 = driver.find_element_by_tag_name("#app-pane-id div.fixture-list div.infinite-loading-container > div:nth-child(2)").value_of_css_property("display")
    if display != 'none' or display2 != 'none':
      break	

  # variable to store all rows
  rows = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.fixture-list > div > div:not([class])")))

  print("\nThere are " + str(len(rows)) + " rows to be retrieved.")

  iterator = 1
  for row in rows:
        
    # array with excel content
    content = []
    
    if len(row.find_elements_by_tag_name('div.fixture-divider .nowrap')) > 0:
      leagueSelector = row.find_element_by_tag_name('div.fixture-divider .nowrap')
      leagueName = leagueSelector.text
      
      if iterator == 1:
        headers.append("League Name")
        
    content.append(leagueName)

    teamsSelector = row.find_element_by_tag_name('div.fixture-listing .info-wrapper .teams .team')
    teamsName = teamsSelector.text
    content.append(teamsName)
    if iterator == 1:
      headers.append("Teams")

    resultTimeSelector = row.find_element_by_tag_name('div.fixture-listing .info-wrapper .status .ko').get_property('childNodes')
    if iterator == 1:
      headers.append("Result")
      headers.append("Start Time")
      headers.append("Current Time")

    if len(resultTimeSelector) > 1:
      resultText = resultTimeSelector[0].get('data')
      timeText = resultTimeSelector[1].text
            
    else:
      resultText = ""
      timeText = resultTimeSelector[0].get('data')
    
    content.append(resultText)

    if ':' in timeText:
      content.append(timeText)
      content.append("")
    else:
      content.append("")
      content.append(timeText)

    if len(row.find_elements_by_tag_name('div.fixture-listing div.stats-wrapper div.inner div.feed-glance')) > 0:

      time.sleep(0.5);
      stats = row.find_elements_by_tag_name('div.fixture-listing div.stats-wrapper div.inner div.feed-glance')

      for stat in stats:
      
        statTitleSelector = stat.find_element_by_tag_name('div.title')
        statTitle = (statTitleSelector.get_attribute("innerHTML")).split("<")[0]

        if iterator == 1:
          headers.append(statTitle + " - H")
          headers.append(statTitle + " - A")

        statDataSelector = stat.find_elements_by_tag_name('div.stats .stat')
        content.append(statDataSelector[0].text)
        content.append(statDataSelector[1].text)

    arrOfContents.append(content)  

    print("Row " + str(iterator) + " of " + str(len(rows)) + " retrieved with success.")
    iterator += 1
  
  games = pd.DataFrame(arrOfContents, columns=headers)

  games.to_excel('oddAlerts - ' + filterTitle + '.xlsx', index=False)

  print("\nThe oddAlerts - " + filterTitle + ".csv was created!")
  
  driver.refresh()

  # Click on the Filters button (Dropdown)
  WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#app-pane-id div div.saved-filters nav div.fill button"))).click()

  # Click on the Testing option
  WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Testing"))).click()

print("\nThe web scrapping process has ended.")
driver.close()