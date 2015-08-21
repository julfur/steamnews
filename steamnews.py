#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import requests
import datetime
import json
from operator import itemgetter
from multiprocessing.dummy import Pool as ThreadPool


class Steam():
    """
        This class gives access to a couple Steam API.
        Takes your Steam API key and your SteamID as parameter.
    """
    def __init__(self, key, steamid):
        self.key = key
        self.steamid = steamid
        self.now = datetime.datetime.now()

    def request(self, url):
        try:
            response = requests.get(url)
            return response.json()
        except requests.exceptions.RequestException as e:
            print self.now, e
            sys.exit(1)

    def get_owned_game(self):
        """
            Get your owned games list.
        """
        url = ("http://api.steampowered.com/IPlayerService/GetOwnedGames/"
               "v0001/?key=" + str(self.key) +
               "&steamid=" + str(self.steamid) +
               "&format=json&include_appinfo=1")
        data = self.request(url)
        return data

    def get_news(self, appid):
        """
            Get the last news for a specific game (400 char max)
            Takes appid as a parameter.
        """
        url = ("http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"
               "?count=1&maxlength=500&format=json&appid=" + str(appid))
        raw = requests.get(url)
        return raw.json()

    def last_news(self, game_list):
        """
            Get the last news for every game in your owned games list.
            Sort by ascending date.
            Takes your owned games list as a parameter.
        """
        # Building appid list to feed Pool
        appid = [game['appid'] for game in game_list['response']['games']]
        # Keeping name and icon_url from owned game list
        metadata = []
        for game in game_list['response']['games']:
            icon_url = ("http://media.steampowered.com/steamcommunity/"
                        "public/images/apps/" + str(game['appid']) + "/" +
                        str(game['img_logo_url']) + ".jpg")
            metadata.append({'name' : game['name'],
                             'appid' : game['appid'],
                             'icon_url' : icon_url})
        # Multiprocessing
        news = []
        pool = ThreadPool(8)
        results = pool.map_async(self.get_news, appid, callback=news.extend)
        results.wait()
        pool.close()
        pool.join()
        # Building output
        data = []
        for x,y in zip(news, metadata):
            if x['appnews']['appid'] == y['appid']:
                name = y['name']
                icon_url = y['icon_url']
                content = x['appnews']['newsitems']
                for z in content:
                    news_date = datetime.datetime.fromtimestamp(int(z['date']))
                    if self.now - news_date < datetime.timedelta(weeks=4):
                        data.append({'title': z['title'],
                                     'date': news_date.strftime('%Y-%m-%d'),
                                     'name': name,
                                     'timestamp': z['date'],
                                     'content': z['contents'],
                                     'url': z['url'],
                                     'icon_url': icon_url})
        return sorted(data, key=itemgetter('timestamp'))


def main():
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    API_KEY = ''
    STEAM_ID = ''
    p = Steam(API_KEY, STEAM_ID)
    game_list = p.get_owned_game()
    data = p.last_news(game_list)
    with open(CURRENT_DIR + '/data.json', 'w') as outfile:
        json.dump(data, outfile)

if __name__ == '__main__':
    main()
