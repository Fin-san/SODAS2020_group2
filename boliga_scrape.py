# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 12:06:01 2020

@author: Lenovo
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from collections import Counter

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


def get_reviews(df):
    i = 0
    bodys = list()
    estates = list()
    estate_ids = list()
    
    #Finder alle ejendomsmæglere, som har mere end 100 huse til salg
    for value in df["estateUrl"].values:
        estates.append(value[8:15])
    numbers = dict(Counter(estates))
    over_100 = dict() 
    for key, value in numbers.items():
        if value > 100:
            over_100[key] = value
            
    #Kører igennem alle links og finder tilhørende beskrivelse
    for link in tqdm(df["estateUrl"].values):
        i += 1
        body_len_prior = len(bodys)
        try:
            response = requests.get(link)
            html = response.text
            soup = BeautifulSoup(html,"html.parser")
            
            if link[8:15] =="home.dk": #Home
                ids = soup.find_all("div",{"class":"text"},"p")
                bodys.extend([x.p.text.replace("\n","").strip().lower() for x in ids[0:1] if len(x)>1])
            elif link[8:15] =="ww.skbo": #skbolig
                ids = soup.find_all("div",{"class":"listing-text"})
                bodys.extend([sk.text.replace("\n","").replace("\r","").strip().lower() for sk in ids[0:1] if len(sk)>1])
            elif link[8:15] == "www.nyb": #Nybolig
                ids = soup.find_all("div",{"class":"foldable-spot__container"})
                bodys.extend([ny.text.replace("\n","").strip().lower() for ny in ids[0:1] if len(ny)>1])
            elif link [8:15] == "ww.elto": #Eltoft Nielsen
                ids = soup.find_all("br")
                bodys.extend([elto.text.replace("\n","").strip().lower() for elto in ids[0:1] if len(elto)>1])
            elif link[8:15] == "www.cla": #Claus Borg
                ids = soup.find_all("div",{"id":"case_content"})
                bodys.extend([cla.text.replace("\n","").strip().lower() for cla in ids[0:1] if len(cla)>1])
            elif link[8:15] == "www.lok": #Lokalbolig
                ids = soup.find_all("div",{"class":"css-s7itso eknr0ef1"})
                bodys.extend([lok.text.replace("\n","").strip() for lok in ids[0:1] if len(lok)>1])
            elif link[8:15] == "www.edc": #EDC Bolig
                ids = soup.find_all("div",{"class":"description"})
                bodys.extend([edc.text.replace("\n","").strip().lower() for edc in ids[0:1] if len(edc)>1])
            elif link[8:15] == "adamsch": #Adam Schnack
                ids = soup.find_all("div",{"class":"listing-text"})
                bodys.extend([adam.text.replace("\n","").strip().lower() for adam in ids[0:1] if len(adam)>1])
            elif link[8:20] == "www.estate.d": #Estate
                ids = soup.find_all("div",{"class":"property-description"})
                bodys.extend([est.text.replace("\n","").strip().lower() for est in ids[0:1] if len(est)>1])
            elif link[8:15] == "www.bri": #Brikk Ejendomme
                ids = soup.find_all("div",{"class":"prop-user-content"})
                bodys.extend([bri.text.replace("\n","").strip().lower() for bri in ids[0:1] if len(bri)>1])
            elif link[8:15] == "www.rea": #Realmæglerne
                ids = soup.find_all("div",{"class":"text-full"})
                bodys.extend([rea.text.replace("\n","").strip().lower() for rea in ids[0:1] if len(rea)>1])
            elif link[8:15] == "danboli": #Danbolig
                ids = soup.find_all("div",{"class":"db-description-block"})
                bodys.extend([dan.text.replace("\n","").strip().lower() for dan in ids[0:1] if len(dan)>1])
            elif link[8:15] == "ww.lili": #Lillenhof
                ids = soup.find_all("div",{"class":"inner"})
                bodys.extend([dan.text.replace("\n","").strip().lower() for dan in ids[0:1] if len(dan)>10])
            elif link[8:15] == "bjornby":
                ids = soup.find_all("div",{"class":"content d-md-block d-none wrap-content"})
                bodys.extend([bjor.text.replace("\n","").strip() for bjor in ids[0:1] if len(bjor)>10])
            elif link[8:15] == 'www.hov': #Hovmand
                ids = soup.find_all("div",{"class":"column"})
                bodys.extend([hov.text.replace("\n","").strip() for hov in ids[0:1] if len(hov)>1])
            elif link[8:15] == 'ww.jesp': #Jesper Nielsen
                ids = soup.find_all("div",{"class":"case-description"})
                bodys.extend([jesp.text.replace("\n","").strip() for jesp in ids[0:1] if len(jesp)>1])
            elif link[8:15] == "www.sel": #Selvsalg
                ids = soup.find_all("div",{"class":"tab-pane active fade in"})
                bodys.extend([selv.text.replace("\n","").strip() for selv in ids[0:1] if len(selv)>1])
            elif link[8:15] == "www.bol": #Bolig
                ids = soup.find_all("div",{"class":"description col-md-16"})
                bodys.extend([bol.text.replace("\n","").strip() for bol in ids[0:1] if len(bol)>1])
            elif link[8:15] == 'www.joh': #Johns
                ids = soup.find_all("div",{"class":"column"})
                bodys.extend([john.text.replace("\n","").strip() for john in ids[0:1] if len(john)>1])
            elif link[8:15] == "racking": #Robinhus
                ids = soup.find_all("div",{"class":"text-container"})
                bodys.extend([robin.text.replace("\n","").strip() for robin in ids[0:1] if len(robin)>1])
            elif link[8:15] == "www.min": #minbolighandel
                ids = soup.find_all("div",{"class":"description col-md-16"})
                bodys.extend([minb.text.replace("\n","").strip() for minb in ids[0:1] if len(minb)>1])
            elif link[8:15] == "ww.unni": #Unnibolig
                ids = soup.find_all("div",{"class":"column"})
                bodys.extend([un.text.replace("\n","").strip() for un in ids[0:1] if len(un)>1])
            elif link[8:15] == "www.sdb": #Sdb bolig
                ids = soup.find_all("div",{"class":"column"})
                bodys.extend([un.text.replace("\n","").strip() for un in ids[0:1] if len(un)>1])
            elif link[8:15] == "ww.land":#Landobolig
                ids = soup.find_all("div",{"class":"col-md-8"})
                bodys.extend([land.text.replace("\n","").strip() for land in ids[0:1] if len(land)>1])
            elif link[8:15] == "www.ber": #Bermistof
                ids = soup.find_all("div",{"class":"column"})
                bodys.extend([ber.text.replace("\n","").strip() for ber in ids[0:1] if len(ber)>1])
            elif link [8:20] == 'www.carlsber': #Carlsberg Byen
                ids = soup.find_all("div",{"itemprop":"description"})
                bodys.extend([car.text.replace("\n","").strip() for car in ids[0:1] if len(car)>1])
            elif link[8:15] == "www.car": #Carsten Nordbo
                ids = soup.find_all("div",{"class":"description col-md-16"})
                bodys.extend([car.text.replace("\n","").strip() for car in ids[0:1] if len(car)>1])
            elif link[8:15] == 'ww.agri': 
                ids = soup.find_all("div",{"class":"col-md-8 col-sm-7 hidden-xs text-box desktop"})
                bodys.extend([agr.text.replace("\n","").strip() for agr in ids[0:1] if len(agr)>1])
            elif link[8:15] == "www.pla":#Place2Live
                ids = soup.find_all("div",{"class":"col-lg-16"})
                bodys.extend([pla.text.replace("\n","").strip() for pla in ids[0:1] if len(pla)>1])
            elif link[8:15] == "www.vil": #Villadsenbolig
                ids = soup.find_all("div",{"class":"description col-md-16"})
                bodys.extend([vil.text.replace("\n","").strip() for vil in ids[0:1] if len(vil)>1])
            elif link[8:15] == 'maegler': #Mæglerhuset
                ids = soup.find_all("div",{"class":"case-text"})
                bodys.extend([mae.text.replace("\n","").strip() for mae in ids[0:1] if len(mae)>1])
            elif link[8:15] == 'ww.thom': #ThomasJørgensen
                ids = soup.find_all("div",{"class":"description col-md-16"})
                bodys.extend([thom.text.replace("\n","").strip() for thom in ids[0:1] if len(thom)>1])
            elif link[8:15] == 'www.htb': #HTbolig
                ids = soup.find_all("div",{"class":"left-side global-style"})
                bodys.extend([htb.text.replace("\n","").strip() for htb in ids[0:1] if len(htb)>1])
            elif link[8:15] == 'ww.boli': #Boligone
                ids = soup.find_all("div",{"class":"first-col"})
                bodys.extend([bol.text.replace("\n","").strip() for bol in ids[0:1] if len(bol)>1])
            elif link[8:15] == "www.mæg":#Mæglerringen
                ids = soup.find_all("div",{"class":"first-col"})
                bodys.extend([ma.text.replace("\n","").strip() for ma in ids[0:1] if len(ma)>1])
            elif link[8:15] == "ww.vest":
                ids = soup.find_all("div",{"class":"first-col"})
                bodys.extend([vest.text.replace("\n","").strip() for vest in ids[0:1] if len(vest)>1])
            elif link[8:15] == "www.tho": #Thorregård
                ids = soup.find_all("div",{"class":"annonce rammebaggrund"})
                bodys.extend([th.text.replace("\n","").strip() for th in ids[0:1] if len(th)>1])
            elif link[8:15] == "byggegr": #Byggegrund
                ids = soup.find_all("div",{"class":"section section-12"})
                bodys.extend([byg.text.replace("\n","").strip() for byg in ids[0:1] if len(byg)>1])
            elif link[8:15] == "grundsa": #Grundsalg
                bodys.append(np.nan)
            elif link[8:15] == "rundsal": #Grundsalg
                bodys.append(np.nan)
            elif link[8:15] =="ww.paul": #paulun
                bodys.append(np.nan)
            else:
                bodys.append(np.nan)
        except:
            bodys.append(np.nan)
            print(link,"virkede ikke")
            continue
        
        body_len_after = len(bodys)
        fixed_change = body_len_prior + 1
        
        try:
            bodys = bodys[0:fixed_change]
        except:
            None
            
        if body_len_after == body_len_prior + 1:
            estate_ids.append(df[df["estateUrl"]==link]["currentArchiveId"].values[0])
    
    print(len(estate_ids))
    print(len(bodys))
    bodys_df = pd.DataFrame({"currentArchiveId":estate_ids,"body":bodys})
    
    return bodys_df

def preprocess_csv(csv):
    """
    This function loads the dataset from boliga and preproccesses it.
    """
    df = pd.read_csv(csv)
    y = np.array(df["price"])
    
    return df

if __name__ == "__main__":
    df = preprocess_csv("house_data_final.csv")
    bodys_df = get_reviews(df)
    df = df.join(bodys_df,on="currentArchiveId")
    #df.to_csv("house_data_final.csv")