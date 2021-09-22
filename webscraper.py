from logging import error
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
# URL = "https://www.tripadvisor.com/Restaurants-g186220-Bristol_England.html"

URL = "https://www.tripadvisor.com/Restaurants-g298474-Cluj_Napoca_Cluj_County_Northwest_Romania_Transylvania.html"

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
        tags = driver.find_element(By.XPATH, xpath).text
        tags = tags.replace(" ", "").split(",")
        print(f"Tags: {tags}")
        for tag in tags:
            rest_data.append(tag)
    except Exception:
        return


def get_images():
    try:

        large_photo_div = driver.find_element_by_class_name("large_photo_wrapper")
        large_photo_div.find_element_by_class_name("basicImg").click()

        for _ in range(3):
            main_image = get_element(By.CLASS_NAME, "mainImg")
            main_image_src = main_image.find_element_by_tag_name("img").get_attribute(
                "src"
            )
            rest_data.append(main_image_src)
            next = get_element(
                By.XPATH,
                '//*[@id="taplc_pv_resp_content_hero_0"]/div/div[1]/div[3]/div[2]',
            ).click()
            print(main_image_src)
        close = get_element(
            By.XPATH, '//*[@id="BODY_BLOCK_JQUERY_REFLOW"]/span/div[2]'
        ).click()

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


# def parse_address(address):
# Regex for UK postcodes
# postcode_pattern = "([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})"

# Trying to be smart but its not worth it
# # Get house number
# r = re.compile("\d+")
# house_number = r.match(address[0])
# address[0].replace(house_number, "")
# if "No." in address[0]:
#     address[0].replace("No.", "")

# # Split the second part of string for more details
# address[1] = address[1].strip().split(" ")

# # Create dictionary with address details
# address_dict = {
#     "street": f"{house_number} {address[0]}",
#     "city": address[1][0],
#     "country": address[1][2],
#     "postalcode": address[1][1],
# }

# Coordinates
# location = geolocator.geocode(address_dict)

# if location:
#     print(f"Coordinates: {location.latitude}, {location.longitude}")
#     rest_data.append(location.latitude)
#     rest_data.append(location.longitude)
# else:
#     print(f"Coordinates: Not Found")
#     rest_data.append(0.001)
#     rest_data.append(0.001)


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

        # Images
        get_images()

        # Address
        address = get_element(By.CLASS_NAME, "brMTW").text
        if address:
            print(f"Address: {address}")
            rest_data.append(address)
            # parse_address(address)

        # Coordinates
        coordinatesAttr = driver.find_element_by_class_name("eCPON").get_attribute(
            "src"
        )

        coordinates = coordinatesAttr.split("&")
        for val in coordinates:
            if "center=" in val:
                coordinates = val.replace("center=", "").split(",")
                break

        rest_data.append(coordinates[0])
        rest_data.append(coordinates[1])
        print(f"Coordinates: {coordinates}")

        # Details
        details_modal = get_element(By.LINK_TEXT, "View all details")
        if details_modal:
            details_modal.click()
            desc = get_element(By.CLASS_NAME, "OMpFN")
            if desc:
                print("Found description!")
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
                '//*[@id="component_43"]/div/div/div/div[2]/div[1]/div[3]/div[1]/div[2]'
            )

        time.sleep(1)

        # Close child tab
        driver.close()

        # Switch to parent window
        driver.switch_to.window(parent_window)
        # print("Parent window handle: %s" % driver.current_window_handle)

        all_restaurants.append(rest_data)
        print()
        print()

# If timeout or something gone wrong -- quit
except:
    driver.quit()

# Write restaurant data to CSV
write_to_csv(all_restaurants)

print("#####-----##### DONE #####-----#####")
