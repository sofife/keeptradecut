import numpy as np
import pandas as pd
import time
from datetime import datetime
from bs4 import BeautifulSoup as bs
import requests


def get_html(url):
    return requests.get(url, timeout=5)


def get_bs(url):
    page_response = get_html(url)
    return bs(page_response.content, "html.parser")


def parse_players(soup, position):
    players = soup.find_all('div',class_='onePlayer')
    data_dict = {'name':[], 
                 'position':[], 
                 'team':[], 
                 'overall_rank':[], 
                 'position_rank':[], 
                 'value':[], 
                 'ktc_keep':[], 
                 'ktc_trade':[], 
                 'ktc_cut':[], 
                 'age':[], 
                 'height':[], 
                 'experience':[], 
                 'draft_capital':[]}
    
    for p in players:
        data = p.find('div',class_='infoModal')
        data_dict['overall_rank'].append(data.find('div',class_='rank').p.get_text().strip())
        data_dict['position_rank'].append(data.find('p',class_='positional-rank').get_text().strip().split(' ')[1])
        data_dict['value'].append(data.find('p',class_='value').get_text().strip())
        data_dict['ktc_keep'].append(data.find('p',class_='ktc keep').get_text().strip())
        data_dict['ktc_trade'].append(data.find('p',class_='ktc trade').get_text().strip())
        data_dict['ktc_cut'].append(data.find('p',class_='ktc cut').get_text().strip())
        data_dict['name'].append(data.find('p',class_='player-name').get_text().strip())
        player_details = data.find('p',class_='player-details').get_text().split('–')
        draft_details = data.find('p',class_='player-draft-details').get_text().split('–')
        
        if position != 'RDP':
            data_dict['position'].append(player_details[0].strip())
            data_dict['team'].append(player_details[1].strip())
            data_dict['age'].append(player_details[2].strip().split(' ')[0])
            height_raw = player_details[3].strip()[:-1].split("'")
            data_dict['height'].append(int(height_raw[0]) * 12 + int(height_raw[1]))
            data_dict['experience'].append(draft_details[0].strip().split(' ')[0])
            draft_capital_raw = draft_details[1].strip().split(', ')
            data_dict['draft_capital'].append(float(draft_capital_raw[0][-1]) + float(draft_capital_raw[1].split(' ')[-1])/100)
#             print(position, team, age, height, experience, draft_capital)
        else:
            data_dict['position'].append(player_details[0].strip())
            data_dict['team'].append(None)
            data_dict['age'].append(None)
            data_dict['height'].append(None)
            data_dict['experience'].append(None)
            data_dict['draft_capital'].append(None)
              
    return pd.DataFrame.from_dict(data_dict)


def ktc_scrape():
    positions = ['QB','WR','RB','TE','RDP']
    df_list = []
    # for loop for position
    for p in positions:
        i = 0
        more_pages = True
        while more_pages:
            if i > 0: time.sleep(3)
            endpoint = 'https://keeptradecut.com/dynasty-rankings?page={0}&filters={1}&format=2'.format(i,p)
            # get_soup()
            soup = get_bs(endpoint)
            player_list = soup.find_all('div', class_='onePlayer')
#             print(p, i, len(player_list))
            if len(player_list) > 0:
                i += 1
                df_list.append(parse_players(soup,p))
            else:
                more_pages = False
        df = pd.concat(df_list, ignore_index=True)
        df['datetime'] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    return df


def program(write=True, filename=None):
	'''
	'''
	df = ktc_scrape()
	if not filename:
		now = datetime.now()
		filename = 'ktc_' + now.strftime("%Y%m%d-%H%M") + '.csv'
	
	if write:
		df.to_csv(filename)
	else:
		return df

    
if __name__ == "__main__":
    program()  