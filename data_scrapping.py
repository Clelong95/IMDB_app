import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def cleancast(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', str(raw_html)).replace('\n'," ").replace('|',":").strip()
    list_ = [i.strip() for i in cleantext.split(":")]
    return list_

def build_df(user_id):
    
    url = 'https://www.imdb.com/user/{}/ratings'.format(user_id)
    raw_data = []
    
    while url != 0 :
        page = requests.get(url)
        soup = BeautifulSoup(page.content,'html.parser')
        
        item_list = soup.find(id="ratings-container").findAll("div",{"class":"lister-item mode-detail"})
        for item in item_list : 
            id_ = item.find("div",{"class":"lister-item-image ribbonize"})["data-tconst"]
            name = item.findAll("a")[1].contents[0]
            genre = item.find("span",{"class":"genre"}).contents[0].strip()
            year = item.find("span",{"class":"lister-item-year text-muted unbold"}).contents[0]
            cast = item.findAll("p",{"class":"text-muted text-small"})[1]
            user_note = item.findAll("span",{"class":"ipl-rating-star__rating"})[1].contents[0]
            imdb_note = item.findAll("span",{"class":"ipl-rating-star__rating"})[0].contents[0]
            
            dict_ = {"Id":id_,
                    "Name":name,
                    "Genre":genre,
                    "Year":year,
                    "Cast":cast,
                    "IMDB_note":imdb_note,
                    "User_note":user_note}
            
            raw_data.append(dict_)
        
        next_page = soup.findAll("a",{"class":"flat-button lister-page-next next-page"})
        if len(next_page)>0:
            url = "https://www.imdb.com/"+ next_page[0]["href"]
        else:
            url = 0
    
    df = pd.DataFrame(raw_data)
    df['Cast'] = df['Cast'].apply(lambda x : cleancast(x))
    df['Stars'] = df['Cast'].apply( lambda x : x[-1].split(','))
    
    df['Actor_1'] = df['Stars'].apply(lambda x: x[0].strip() if len(x)>0 else 'None')
    df['Actor_2'] = df['Stars'].apply(lambda x: x[1].strip() if len(x)>1 else 'None')
    df['Actor_3'] = df['Stars'].apply(lambda x: x[2].strip() if len(x)>2 else 'None')
    df['Actor_4'] = df['Stars'].apply(lambda x: x[3].strip() if len(x)>3 else 'None')

    
    df['Director'] = df['Cast'].apply(lambda x : x[1] if len(x)==4 else "None")
    df['Type'] = df['Director'].apply(lambda x: "Serie" if x == "None" else "Movie")
    df['Year'] = df['Year'].apply(lambda x : re.findall('\d+',x)[0])
    
    df.drop(['Cast','Stars'],axis=1,inplace=True)
    
    df = df.astype({"Id":"string",
               "Name":"string",
               "Genre":"string",
               "Year":"int",
               "IMDB_note":"float",
               "User_note":"int",
               "Actor_1" :"string",
               "Actor_2" :"string",
               "Actor_3" :"string",
               "Actor_4" :"string",
               "Director":"string",
               "Type":"string"})
    
    return(df)