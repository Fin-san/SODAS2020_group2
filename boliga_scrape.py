# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 12:06:01 2020

@author: Lenovo
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import re
import json

import time
from tqdm import tqdm
def houses_boliga(number_houses):
    """
    Returns a list of all ids for houses on boliga
    """
    house_id = list()
    url = "https://www.boliga.dk/resultat?"
    
    for i in tqdm(range(int(number_houses))):
        new_url = url + f"?page={i}"
        response = requests.get(new_url)
        html = response.text
        soup = BeautifulSoup(html,"html.parser")
        ids = soup.find_all("a",{"class":"house-list-item"})
        link_houses = list()
        
        for link in ids:
            link_houses.append(re.findall("(/\d{4,}/)",link["href"])[0].replace("/",""))
        
        print(f"hentet {len(house_id)} ids")
        house_id.extend(link_houses)
    print("Hentet alle ids")
    return house_id

def get_info(id_list):
    all_df = list()
    new_keys = ["registeredArea","downPayment","estateUrl","currentArchiveId","forSaleNowId",
                "foreclosureId","selfsaleEstateId","cleanStreet","estateId","latitude","longitude",
               "propertyType","priceChangePercentTotal","energyClass","price","rooms","size","lotSize",
               "floor","buildYear","city","isActive","municipality","zipCode","street",
                "squaremeterPrice","daysForSale","createdDate","basementSize","views"]
    i = 0
    for house_id in tqdm(id_list):
        i +=1
        response = requests.get(f'https://api.boliga.dk/api/v2/estate/{house_id}')
        response = response.json()
        df_dict = {key: response[key] for key in new_keys}
        df = pd.DataFrame(df_dict,index=[0])
        all_df.append(df)
        print(f"Hentet {i} hus data")
        
        time.sleep(1)
        
        
    df = pd.concat(all_df,axis=0,ignore_index=True)
    
    return df

id_houses = houses_boliga(1042)
df_house_id = pd.DataFrame({"ids":id_houses})
df_house_id.to_csv("id_houses.csv")
df = get_info(id_houses)
df.to_csv("house_data.csv")
