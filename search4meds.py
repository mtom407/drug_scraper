import requests
from bs4 import BeautifulSoup
import numpy as np
import sys
import random
import time

# load a random substance from the text file
lines = open('active_substance_database.txt').read().splitlines()
random_substance = random.choice(lines)
print(random_substance)

# how many pages contain active substances which names start with the first letter of 
# the substance drawn from the file
pages2check = 3

random_substance = random_substance.lower()
# first letter to setup the web address
first_letter = random_substance[0]

# pętla przechodząca przez storny i zapisująca nazwę susbtancji oraz link jej strony z lekami
# walk through pages and
for page_number in range(pages2check):
    
    actual_url = f'https://ktomalek.pl/substancje-czynne-na-litere-{first_letter}/l-{page_number+1}'
    source = requests.get(actual_url).text
    soup = BeautifulSoup(source, 'lxml')

    # create dict: KEYS --> MEDICINE NAMES, VALUES --> HREFs
    litags = dict()
    for ultag in soup.find_all('ul', class_='l-s:u m-l'):
        for litag in ultag.find_all('li'):
            litags[litag.text.lower()] = litag.a['href']
            
    # check if the substance has been found on the current page and break
    if random_substance in litags.keys():
        found_href = litags[random_substance]
        break
    elif page_number + 1 == pages2check: # if the substance can't be found at all
        print('Substancja "{}" nie została znaleziona. Koniec programu.'.format(random_substance))
        sys.exit()
    time.sleep(1)

# ================= FINDING THE MEDS ================= #
# setup the addres and extract the content
substance_url = 'https://ktomalek.pl' + found_href
substance_source = requests.get(substance_url).text
soup = BeautifulSoup(substance_source, 'lxml')

# count how many pages contain info about the meds
try:
    pages = soup.find('ul', class_='pagination')
    page_options = []
    for page_option in pages.find_all('li'):
        page_options.append(page_option.text)
    number_of_pages = int(page_options[-2])
except:
    number_of_pages = 1
# list of all medicine names
meds_list = []
for page_id in range(number_of_pages):
    
    substance_url = substance_url[:-1] + str(page_id+1)
    print(substance_url)
    substance_source = requests.get(substance_url).text
    soup = BeautifulSoup(substance_source, 'lxml')
    # extract medicine names on the current page
    for section in soup.find_all('section', class_='box'):
        meds_list.append(section.h2.text)
# sort and discard duplicates
meds_sorted = sorted(set(meds_list))
print(meds_sorted)
print(len(meds_sorted))
# ==================================================== #

