from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
import time
import csv
from geopy.geocoders import Nominatim

# SETUP
PATH = "chromedriver.exe"
driver = webdriver.Chrome(PATH)

# Targu Mures
# URL = "https://www.tripadvisor.com/Restaurants-g298477-Targu_Mures_Mures_County_Central_Romania_Transylvania.html"

# Bristol
URL = "https://www.tripadvisor.com/Restaurants-g186220-Bristol_England.html"

driver.get(URL)

geolocator = Nominatim(user_agent="webscraper")

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
    try:
        tags = driver.find_element(By.XPATH, xpath)
        tags = tags.replace(" ", "").split(",")
        print(f"Tags: {tags}")
        for tag in tags:
            rest_data.append(tag)
    except Exception:
        return


def get_element(method, str):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((method, str))
        )
    except Exception:
        return False

    return element


def parse_address(address):
    postcode_pattern = "([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})"
    print(address)
    address = address.split(",")
    print(address)
    r = re.compile(postcode_pattern)
    postcode = r.match(address[1])

    # Coordinates
    location = geolocator.geocode(f"{address[0]} {postcode}")
    if location:
        print(f"Coordinates: {location.latitude}, {location.longitude}")
        rest_data.append(location.latitude)
        rest_data.append(location.longitude)
    else:
        rest_data.append(0.001)
        rest_data.append(0.001)


# Main
try:
    # Get rid of privacy modal
    modal = get_element(By.ID, "_evidon-accept-button").click()

    # Find the list of restaurants
    restaurants = get_element(By.ID, "EATERY_SEARCH_RESULTS")

    # Get the name of every restaurant in the list
    for div in restaurants.find_elements(By.CLASS_NAME, "OhCyu"):
        header = div.find_element(By.TAG_NAME, "a")
        # print(header.text)
        restaurant_names.append(header.text)

    # Loop through the restaurants
    for name in restaurant_names:
        # Open restaurant page
        link = get_element(By.LINK_TEXT, name).click()
        time.sleep(2)

        # Switch focus to opened tab
        driver.switch_to.window(driver.window_handles[1])

        # Hold restaurant data
        rest_data = []

        # Name
        name = driver.find_element(By.CLASS_NAME, "fHibz").text
        print(f"Restaurant name: {name}")
        rest_data.append(name)

        # Address
        address = driver.find_element(By.CLASS_NAME, "brMTW").text
        if address:
            parse_address(address)

        # Details
        details_modal = get_element(By.LINK_TEXT, "View all details")
        if details_modal:
            details_modal.click()
            print("Clicked?")
            desc = get_element(By.CLASS_NAME, "OMpFN")
            if desc:
                print("Found desc?")
                print(f"Description: {desc.text}")
                rest_data.append(desc.text)
                get_tags(
                    '//*[@id="BODY_BLOCK_JQUERY_REFLOW"]/div[15]/div/div[2]/div/div/div[1]/div/div[2]/div/div[2]/div[2]'
                )
            else:
                print("No description")
                rest_data.append("No description")
                get_tags(
                    '//*[@id="BODY_BLOCK_JQUERY_REFLOW"]/div[15]/div/div[2]/div/div/div[1]/div/div/div/div[2]/div[2]'
                )
        else:
            # Description outside
            desc = get_element(By.CLASS_NAME, "epsEZ")
            if desc:
                rest_data.append(desc.text)
            else:
                print("No description")
                rest_data.append("No description")
            # Get tags anyway
            get_tags(
                '//*[@id="component_43"]/div/div/div/div[2]/div/div[3]/div[1]/div[2]'
            )

        time.sleep(1)

        # Close child tab
        driver.close()

        # Switch to parent window
        driver.switch_to.window(parent_window)
        # print("Parent window handle: %s" % driver.current_window_handle)

        all_restaurants.append(rest_data)

# If timeout or something gone wrong -- quit
except:
    driver.quit()

# Write restaurant data to CSV
write_to_csv(all_restaurants)

print("#####-----##### DONE #####-----#####")
