from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import json
import os
import re
import datetime

import pandas as pd
import matplotlib.pyplot as plt

# Function to scrap one page


def url_scraper(url):

    # Opening web browser
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    # Getting the the page we want to scrap
    driver.get(url)
    driver.implicitly_wait(1)

    # Extracting page main title
    title_page = driver.find_element(By.CLASS_NAME, 'KkejIK').text
    # Identification of each sections of the page. Creating an empty dictionary to save the data.
    sections = driver.find_elements(By.CLASS_NAME, 'MAcbb-')
    section_dict = {}

    # Looping throught each section to get the information we want which are the tables
    for section in sections:
        # Extracting section title
        title_section = section.find_element(By.CLASS_NAME, "sC0Aof").text
        sub_section_dict = {}
        section_dict[title_section] = sub_section_dict

        # Looping throught ever sub-section to extract every table
        if section.find_elements(By.CLASS_NAME, "T8G8vu"):
            sub_sections = section.find_elements(By.CLASS_NAME, "T8G8vu")
            extra_title = ''
            for sub_section in sub_sections:

                try:
                    title_sub_section = extra_title + \
                        sub_section.find_element(By.CLASS_NAME, 'SQoGqa').text
                    sub_section_dict[title_sub_section] = {}

                    # To load the HTML, we need to 'activate' the JS by clicking on a button of the table
                    sub_section.find_element(By.CLASS_NAME, 'JxT10f').click()

                    # Getting features name as they are different on each urls. Features comes in one long str thet needs to be split
                    features = sub_section.find_element(
                        By.CLASS_NAME, 'JxT10f')
                    feature_list = (features.text).split('\n')

                    # Getting the table associated with the sub section
                    tables = sub_section.find_element(By.CLASS_NAME, 'cjpIYY')
                    feature_dict = {}

                    # Adding the date of scrapping
                    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

                    # Going through every row of every column and creating the list of values associated with each feature
                    rows = tables.find_elements(By.TAG_NAME, 'tr')
                    for i in range(len(feature_list)):
                        feature_dict[feature_list[i]] = []
                        feature_dict['Date'] = []

                        for row in rows:
                            value = row.find_element(
                                By.XPATH, f'./td[{i+1}]').text
                            feature_dict[feature_list[i]].append(value)
                            feature_dict['Date'].append(current_date)

                    sub_section_dict[title_sub_section] = feature_dict

                except Exception as e:
                    extra_title = sub_section.find_element(
                        By.CLASS_NAME, 'SQoGqa').text + ' '
                    del sub_section_dict[title_sub_section]

        else:

            sub_section.find_element(By.CLASS_NAME, 'JxT10f').click()

            # Getting features name as they are different on each urls. Features comes in one long str thet needs to be split
            features = sub_section.find_element(By.CLASS_NAME, 'JxT10f')
            feature_list = (features.text).split('\n')

            # Getting the table associated with the sub section
            tables = sub_section.find_element(By.CLASS_NAME, 'cjpIYY')
            feature_dict = {}

            # Adding the date of scrapping
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")

            # Going through every row of every column and creating the list of values associated with each feature
            rows = tables.find_elements(By.TAG_NAME, 'tr')
            for i in range(len(feature_list)):
                feature_dict[feature_list[i]] = []
                feature_dict['Date'] = []

                for row in rows:
                    value = row.find_element(By.XPATH, f'./td[{i+1}]').text
                    feature_dict[feature_list[i]].append(value)
                    feature_dict['Date'].append(current_date)

            sub_section_dict[title_sub_section] = feature_dict

    page_dict = {}
    page_dict[title_page] = section_dict

    driver.quit()

    return page_dict


# Function to scrap all the urls and follow the one we have scrapped or not
def urls_scrapped(urls):
    data = []
    # urls_done has been created if the script come to a stop for whatever reason. We can look at the last link added here and restart from here.
    urls_done = []
    for url in urls:
        print(url)  # Help to follow the script live
        try:
            scraping = url_scraper(url)
            data.append(scraping)
            urls_done.append(url)
        except:  # If there is an issue on a url we can just skip it and move on
            pass

    return data, urls_done[-1]


# Function to save the scraping
def json__saving(page_dict):
    json_string = json.dumps(page_dict)
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(f'scrapings/{current_date}_mon_fichier.json', 'w') as datas:
        datas.write(json_string)


# Function to find all the branches of the json
def find_branches(dictionary, depth, max_depth, parent_key=None):
    branches = []
    for key, value in dictionary.items():
        current_key = key if parent_key is None else f"{
            parent_key}\\{key}"  # Change '.' to '\\'
        if isinstance(value, dict) and depth < max_depth:
            branches.extend(find_branches(
                value, depth + 1, max_depth, current_key))
        else:
            branches.append(current_key)
    return branches


# Function to find the deepness of a dictionnary
def find_nested_depth(dictionary, current_depth=0):
    max_depth = current_depth
    for value in dictionary.values():
        if isinstance(value, dict):
            depth = find_nested_depth(value, current_depth + 1)
            max_depth = max(max_depth, depth)
    return max_depth


def chain_to_list(chaine):
    return re.findall(r"\['(.*?)'\]", chaine)


def list_to_chain(liste):
    elements = [f"['{element}']" for element in liste]
    chain = ''.join(elements)
    return chain


def get_options(requests_list, level, selected_options):
    if level == 0:
        return set(req[0] for req in requests_list)
    else:
        return set(req[level] for req in requests_list if req[:level] == selected_options)
