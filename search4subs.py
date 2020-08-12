import requests
from lxml import html
import time
import pandas as pd
import numpy as np

def get_active_subs(meds, prettyprint = False):
    # log substancji aktywnych wszystkich leków w kolejności w jakiej występują na recepcie
    # dict holding active substances of all meds in the prescription
    active_subs_dict = dict()
    # iterowanie przez receptę
    # iterate through the prescription
    for medicine in meds:
        # setup danych wchodzących do input box'a
        # setup data for the input box, fill in the form
        payload = {'searchInput': medicine}
        r = requests.post('https://ktomalek.pl/l/lek/szukaj', data=payload)


        # find a string to setup the link, extract useful data
        first_link = r.text.find("/l/ulotka")
        custom_address = r.text[first_link:first_link+300].split(' ')[0].strip('''"''')
        # setup właściwego url pierwszego linka na stronie wyszukiwania
        # setup for the first link on the search site
        url = 'https://ktomalek.pl/' + custom_address

        # request and process the content
        page = requests.get(url)
        tree = html.fromstring(page.content)
        # extract the active substances
        active_substances = tree.xpath('//span[@itemprop="activeIngredient"]/text()')
        # save extracted data
        if not active_substances:
            active_subs_dict[medicine] = ['Not Found']
        elif ',' in active_substances[0]:
            active_subs_dict[medicine] = list(map(lambda s: s.strip(' '), active_substances[0].split(',')))
        else:
            active_subs_dict[medicine] = active_substances
        
    if prettyprint:
        # pull all substances without repetitions
        all_subs = []
        for key, values in active_subs_dict.items():
            for value in values:
                if value != 'Not Found':
                    all_subs.append(value)
        all_subs = sorted(set(all_subs))

        # create a matrix encoding the composition of all meds 
        composition_data = np.zeros((len(meds), len(all_subs)), dtype = 'ubyte')
        for med_id, medicine in enumerate(active_subs_dict.keys()):
            medicine_subs = active_subs_dict[medicine]
            for sub_id, substance in enumerate(all_subs):
                if substance in medicine_subs:
                    composition_data[med_id, sub_id] = 1
                else:                
                    composition_data[med_id, sub_id] = 0

        # create a DataFrame based on the matrix
        df = pd.DataFrame(composition_data, index = active_subs_dict.keys(), columns = all_subs)
        df.replace((0,1), ('NIE', 'TAK'), inplace = True)
        print(df)


    return active_subs_dict


if __name__ == '__main__':
    prescription = ['Coffecorn forte', 'Coffecorn mite', 'Xylometazolin']

    active = get_active_subs(prescription, prettyprint=True)

