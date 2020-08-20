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



def houses_boliga():
    """
    Returns a list of all ids for houses on boliga
    """
    house_id = list()
    url = "https://www.boliga.dk/resultat?"
    
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html,"html.parser")
    ids = soup.find_all("a",{"class":"page-button"})
    
    max_pages = int(ids[-2].text)
    
    for i in tqdm(range(1,max_pages)):
        new_url = url + f"page={i}"
        response = requests.get(new_url)
        html = response.text
        soup = BeautifulSoup(html,"html.parser")
        ids = soup.find_all("a",{"class":"house-list-item"})
        link_houses = list()
        
        for link in ids:
            try:
                link_houses.append(re.findall("(/\d{4,}/)",link["href"])[0].replace("/",""))
            except:
                continue
        
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
        try:
            response = requests.get(f'https://api.boliga.dk/api/v2/estate/{house_id}')
            response = response.json()
            df_dict = {key: response[key] for key in new_keys}
            df = pd.DataFrame(df_dict,index=[0])
            all_df.append(df)
        except:
            continue
        
    df = pd.concat(all_df,axis=0,ignore_index=True)
    
    return df

id_houses = houses_boliga()
df_house_id = pd.DataFrame({"ids":id_houses})
df_house_id.to_csv("id_houses.csv")
df = get_info(id_houses)
df.to_csv("house_data.csv")
