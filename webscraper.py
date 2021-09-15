from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import csv

# SETUP
PATH = "chromedriver.exe"
driver = webdriver.Chrome(PATH)
URL = "https://www.tripadvisor.com/Restaurants-g298477-Targu_Mures_Mures_County_Central_Romania_Transylvania.html"

driver.get(URL)
print(driver.title)

# VARIABLES
parent_window = driver.current_window_handle
restaurant_names = []
all_restaurants = []

# Write to CSV function
def write_to_csv(data):
    with open("restaurant_data.csv", "a", newline="") as f:

        writer = csv.writer(f)

        writer.writerows(data)


def get_tags(xpath):
    tags = driver.find_element_by_xpath(xpath).text
    tags = tags.replace(" ", "").split(",")
    for tag in tags:
        rest_data.append(tag)


# Main
try:
    # Get rid of privacy modal
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "_evidon-accept-button"))
    )
    element.click()
    print("Parent window handle: %s" % driver.current_window_handle)

    # Find the list of restaurants
    restaurants = driver.find_element_by_id("EATERY_SEARCH_RESULTS")

    # Get the name of every restaurant in the list
    for div in restaurants.find_elements_by_class_name("OhCyu"):
        header = div.find_element_by_tag_name("a")
        # print(header.text)
        restaurant_names.append(header.text)

    # Loop through the restaurants
    for name in restaurant_names:
        # Open restaurant page
        link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, name))
        )
        link.click()

        # Wait for 5 seconds
        time.sleep(5)

        # Switch focus to opened tab
        driver.switch_to.window(driver.window_handles[1])
        print("Current window handle: %s" % driver.current_window_handle)

        time.sleep(1)

        # Get restaurant data
        rest_data = []

        # Get restaurant name
        rest_data.append(driver.find_element_by_class_name("fHibz").text)
        print("Name FOUND!")

        # Address
        address = driver.find_element_by_class_name("brMTW").text
        address = address.split(",")
        for a in address:
            rest_data.append(a)
        print("Address FOUND!")

        # Coords
        rest_data.append("")
        rest_data.append("")

        try:
            # Open all details modal
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "View all details"))
            )
            element.click()

            time.sleep(2)

            try:
                # Description
                rest_data.append(driver.find_element_by_class_name("OMpFN").text)
                print("Description FOUND!")

                # Tags
                get_tags(
                    '//*[@id="BODY_BLOCK_JQUERY_REFLOW"]/div[15]/div/div[2]/div/div/div[1]/div/div[2]/div/div[2]/div[2]'
                )
                print("Tags FOUND!")
            except:
                # Tags
                get_tags(
                    '//*[@id="BODY_BLOCK_JQUERY_REFLOW"]/div[15]/div/div[2]/div/div/div[1]/div/div/div/div[1]/div[2]'
                )

                print("Tags FOUND!")
        except:
            # Empty desc
            rest_data.append("")

            # Tags
            get_tags('//*[@id="component_43"]/div/div/div/div[2]/div/div[2]/div/div[2]')
            print("Tags FOUND!")

        time.sleep(3)

        # Close child tab
        driver.close()

        # Switch to parent window
        driver.switch_to.window(parent_window)
        print("Parent window handle: %s" % driver.current_window_handle)

        all_restaurants.append(rest_data)

# If timeout or something gone wrong -- quit
except:
    driver.quit()

# Write restaurant data to CSV
write_to_csv(all_restaurants)

print(" ##### DONE #####")
print(" ##### DONE #####")
print(" ##### DONE #####")
print(" ##### DONE #####")
print(" ##### DONE #####")
