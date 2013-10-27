from default import *
from library import *
import tools

sys.path.append(os.path.join(CWD, 'external'))

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from urllib import quote_plus

class Module(BARTSIDEE_MODULE):
    def __init__(self, app):
        self.app            = app
        BARTSIDEE_MODULE.__init__(self, app)

        self.name           = "Eredivisie"                          #Name of the channel
        self.type           = ['list']                          #Choose between 'search', 'list', 'genre'
        self.episode        = True                              #True if the list has episodes
        self.content_type   = 'video/x-flv'                     #Mime type of the content to be played
        self.country        = 'NL'                              #2 character country id code


        self.url_base       = 'http://eredivisielive.nl'

    def List(self):
        url = self.url_base  + '/video/'
        data = tools.urlopen(self.app, url)
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES, smartQuotesTo="xml")

        div_main = soup.findAll('div', {'id':'filter-club-options'})[0]

        streamlist = []
        i = 0
        for item in div_main.findAll('a'):
            if not i == 0:
                stream = CreateList()
                stream.name     =   item.findAll('span', {'class':'name'})[0].contents[0]
                stream.id       =   item['href']
                streamlist.append(stream)
            i += 1

        return streamlist

    def Episode(self, stream_name, stream_id, page, totalpage):
        url  = self.url_base + str(stream_id) + 'pagina/' + str(page) +'/'
        data = tools.urlopen(self.app, url, {'cache':3600})
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES, smartQuotesTo="xml")

        div_main = soup.findAll('div', {'id':'video-overview'})[0]

        try:
            submenu   = soup.findAll('div', {'id':'pagination-pages'})[0]
            pages     = submenu.findAll('a')
            totalpage = len(pages) + 1
        except:
            totalpage = 1

        episodelist = list()
        for info in div_main.findAll('li'):
            if info.findAll('span', {'class':'video-payment-noprice-button'}):
                continue

            episode                 =   CreateEpisode()
            episode.name            =   info.findAll('span', {'class':'title'})[0].contents[0]
            episode.id              =   info.a['href']
            episode.thumbnails      =   info.a.img['src']
            episode.date            =   info.findAll('span', {'class':'date'})[0].contents[0]
            episode.page            =   page
            episode.totalpage       =   totalpage
            episodelist.append(episode)

        return episodelist

    def Play(self, stream_name, stream_id, subtitle):
        id = re.compile('video\/(.*?)-').search(str(stream_id)).group(1)

        url  = 'http://eredivisielive.nl/content/playlist/website/%s_ere_lr.xml' % (id,)
        data = tools.urlopen(self.app, url)
        soup = BeautifulStoneSoup(data, convertEntities=BeautifulSoup.XML_ENTITIES, smartQuotesTo="xml")
        
        domain = soup.findAll('videodock:streamer')[0].contents[0]
        media  = soup.findAll('media:content')

        quality = []
        files   = {}
        for i in media:
            quality.append(int(i['bitrate']))
            files[int(i['bitrate'])] = i['url']

        quality = sorted(quality)

        url                 =   'http://www.bartsidee.nl/flowplayer/player.php?url=' + str(domain) + '&clip=mp4:' + str(files[quality.pop()])
        play                =   CreatePlay()
        play.content_type   =   'video/x-flv'
        play.path           =   quote_plus(url)
        play.domain         =   'bartsidee.nl'
        
        return play