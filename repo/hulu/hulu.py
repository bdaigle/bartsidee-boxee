from default import *
from library import *
import tools

sys.path.append(os.path.join(CWD, 'external'))

from BeautifulSoup import BeautifulSoup
from urllib import quote_plus

try:    import simplejson as json
except: import json
import math

class Module(BARTSIDEE_MODULE):
    def __init__(self, app):
        self.app            = app
        BARTSIDEE_MODULE.__init__(self, app)

        self.url_base       = 'http://www.hulu.com'
        
        self.name           = "Hulu"                            #Name of the channel
        self.type           = ['search', 'genre']               #Choose between 'search', 'list', 'genre'
        self.episode        = True                              #True if the list has episodes
        self.genre          = ['Comedy', 'Drama', 'Reality and Game Shows','Animation and Cartoons', 'Anime', 'International', 'Kids', 'Family', 'Action and Adventure', 'Food', 'Science Fiction', 'News and Information', 'Classics', 'Latino', 'Horror and Suspense', 'Documentaries', 'Korean Drama', 'Health and Wellness', 'Lifestyle', 'Sports', 'Music', 'Arts and Culture', 'Videogames', 'Gay and Lesbian']
        self.filter         = []                                #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type   = 'video/x-flv'                     #Mime type of the content to be played
        self.country        = 'US'                              #2 character country id code
        
        
        self.free           = "1"
        self.pageSize       = 16
        
        self.access_token   = re.compile('w.API_DONUT = \'(.*?)\';', re.DOTALL + re.IGNORECASE).search(str(tools.urlopen(self.app, self.url_base))).group(1)

    def Search(self, search):
        url  = self.url_base + '/browse/search?alphabet=All&family_friendly=0&closed_captioned=0&has_free=1&has_huluplus=0&has_hd=0&channel=All&subchannel=&network=All&display=Shows%20with%20full%20episodes%20only&decade=All&type=tv&view_as_thumbnail=false&block_num=0&keyword=' + quote_plus(search)
        data = tools.urlopen(self.app, url)

        data = re.compile('"show_list", "(.*?)"\)', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        data = data.replace('\\u003c','<').replace('\\u003e','>').replace('\\','').replace('\\n','').replace('\\t','')
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES, smartQuotesTo="xml")

        streamlist = list()
        for info in soup.findAll('a', {'onclick':True}):
            stream         = CreateList()
            stream.name    = info.contents[0]
            stream.id      = info['href']
            streamlist.append(stream)

        return streamlist
    
    def Episode(self, stream_name, stream_id, page, totalpage):
        data = tools.urlopen(self.app, stream_id, {'cache':3600})

        if not data:
            return []

        soup    = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
        show_id = re.compile('show\/(.*?)\?region\=', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)

        url  = self.url_base + "/mozart/v1.h2o/shows/videos?free_only="+self.free+"&include_seasons=true&order=asc&shorter_cache=true&show_id="+show_id+"&sort=seasons_and_release&video_type%5B%5D=episode&video_type%5B%5D=game&items_per_page=" + str(self.pageSize) + "&position=" + str(self.pageSize * (page - 1)) + "&_user_pgid=1&_content_pgid=67&_device_id=1&access_token=" + self.access_token

        data = tools.urlopen(self.app, url)
        json_data = json.loads(data)
        
        if totalpage == "":
            if int(json_data['total_count']) > self.pageSize:
               totalpage = int(math.ceil(int(json_data['total_count']) / self.pageSize))
            else:
               totalpage = 1

        episodelist = list()
        for item in json_data['data']:
            episode             =   CreateEpisode()
            episode.name        =   stream_name
            episode.id          =   self.url_base + '/watch/'+str(item['video']['id'])
            episode.description =   'Episode: ' + str(item['video']['episode_number']) + ' - '  + str(item['video']['title'])
            episode.thumbnails  =   'http://ib1.huluim.com/video/'+str(item['video']['content_id'])+'?size=220x124'
            episode.date        =   'Season: ' + str(item['video']['season_number'])
            episode.page        =   page
            episode.totalpage   =   totalpage
            episodelist.append(episode)

        return episodelist

    def Genre(self, genre, filter, page, totalpage):
        url = self.url_base + '/mozart/v1.h2o/shows?asset_scope=tv&genre='+genre.replace(" ", "+")+'&order=desc&sort=view_count_week&video_type=tv&items_per_page=' + str(self.pageSize) + '&position='+ str(self.pageSize * (page - 1)) + '&_user_pgid=1&_content_pgid=67&_device_id=1&free_only='+self.free + '&access_token=' + self.access_token
        
        data = tools.urlopen(self.app, url, {'cache':3600})

        if data == "":
            mc.ShowDialogNotification("No genre found for " + str(genre))
            return []

        json_data = json.loads(data)
        
        if totalpage == "":
            if int(json_data['total_count']) > self.pageSize:
               totalpage = int(math.ceil(int(json_data['total_count']) / self.pageSize))
            else:
               totalpage = 1

        genrelist = list()
        for item in json_data['data']:
            genreitem           =   CreateEpisode()
            genreitem.episode   =   "True"
            genreitem.name      =   '[UPPERCASE]'+ item['show']['name'] +'[/UPPERCASE] ' + item['show']['description']
            genreitem.id        =   self.url_base + '/' +str(item['show']['canonical_name'])
            genreitem.page      =   page
            genreitem.totalpage =   totalpage
            genrelist.append(genreitem)

        return genrelist

    def Play(self, stream_name, stream_id, subtitle):
        path            =   self.tinyurl(stream_id)
        play            =   CreatePlay()
        play.path       =   quote_plus(path)
        play.domain     =   'bartsidee.nl'
        play.jsactions  =   quote_plus('http://boxee.bartsidee.nl/js/hulu.js')
        return play

    def tinyurl(self, params):
        url = "http://tinyurl.com/api-create.php?url=" + str(params)
        return tools.urlopen(self.app, url)

    def getGenres(self):
        url  = self.url_base + "/mozart/v1.h2o/shows/genres?sort=view_count_week&type=tv&items_per_page=32&position=0&_user_pgid=1&_content_pgid=67&_device_id=1&access_token=" + self.access_token
        data = tools.urlopen(self.app, url, {'cache':36000})
        
        json_data = json.loads(data)
        
        genres = []
        for item in json_data['data']:
            genres.append(item["genre"]["name"])

        return genres
