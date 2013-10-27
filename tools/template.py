import mc, re, os, sys
sys.path.append(os.path.join(mc.GetApp().GetAppDir(), 'libs'))
import ba
from beautifulsoup.BeautifulSoup import BeautifulSoup

class Module(object):
    def __init__(self):
        self.name = "Module Name"                   #Name of the channel
        self.type = ['search','genre','list']       #Choose between 'search', 'list', 'genre'
        self.episode = True                         #True if the list has episodes
        self.filter = []                            #Option to set a filter to the list
        self.genre = []                             #Array to add a genres to the genre section
        self.content_type = 'video/x-ms-asf'        #Mime type of the content to be played
        self.country = 'NL'                         #2 character country id code

    def Search(self, search):
        """Start your code here"""
        
        """End your code here"""
        return streamlist
    
    def List(self):
        """Start your code here"""
        
        """End your code here"""
        return streamlist
    
    def Episode(self, stream_name, stream_id, page, totalpage):
        """Start your code here"""
        
        """End your code here"""
        return episodelist

    def Genre(self, genre, filter, page, totalpage):
        """Start your code here"""
        
        """End your code here"""
        return genrelist
        
    def Play(self, stream_name, stream_id, subtitle):
         """Start your code here"""
        
        """End your code here"""
        return play