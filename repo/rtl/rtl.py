from default import *
from library import *
import tools

sys.path.append(os.path.join(CWD, 'external'))

if 'linux' in sys.platform:
    sys.path.append(os.path.join(CWD, 'system', 'linux'))
elif 'win32' in sys.platform:
    sys.path.append(os.path.join(CWD, 'system', 'win32'))
elif 'darwin' in sys.platform:
    sys.path.append(os.path.join(CWD, 'system', 'darwin'))
    
from lxml import etree
import time
from urllib import quote_plus, urlencode

class Module(BARTSIDEE_MODULE):
    def __init__(self, app):
        self.app            = app
        BARTSIDEE_MODULE.__init__(self, app)

        self.name           = "RTL Gemist"                      #Name of the channel
        self.type           = ['list']                          #Choose between 'search', 'list', 'genre'
        self.episode        = True                              #True if the list has episodes
        self.country        = 'NL'                              #2 character country id code

        self.url_base = 'http://www.rtl.nl/system/s4m/ipadfd/d=ipad/fmt=adaptive'

    def List(self):
        data = tools.urlopen(self.app, self.url_base, {'cache':3600})
        doc = etree.fromstring(data)

        streamlist = list()
        try:
            series = doc.xpath('//serieitem')
        except:
            return streamlist

        for serie in series:
            stream = CreateList()
            stream.name     =  serie.findtext('serienaam').encode('utf-8')
            stream.id       =  serie.findtext('itemsperserie_url')
            streamlist.append(stream)

        return streamlist

    def Episode(self, stream_name, stream_id, page, totalpage):
        data = tools.urlopen(self.app, stream_id, {'cache':600})
        doc = etree.fromstring(data)
        try:
            episodes = doc.xpath('//item')
        except:
            episodes = []

        if len(episodes) < 1:
            mc.ShowDialogNotification("Geen afleveringen gevonden voor " + str(stream_name))
            return []

        episodes.reverse()

        episodelist = list()
        unique = []
        for item in episodes:
            date = item.findtext('broadcastdatetime')
            type = item.findtext('classname')

            if date not in unique and type in ["aflevering", "uitzending"]:
                episode             =   CreateEpisode()
                episode.name        =   stream_name + " - " + item.findtext('episodetitel')
                episode.id          =   item.findtext('movie')
                episode.thumbnails  =   item.findtext('thumbnail')
                episode.date        =   self.getDate(item.findtext('broadcastdatetime').split('T')[0]) 
                episode.description =   item.findtext('samenvattingkort').encode('utf-8') 
                episode.page        =   page
                episode.totalpage   =   totalpage
                episodelist.append(episode)
                unique.append(date)

        return episodelist

    def Play(self, stream_name, stream_id, subtitle):
        if not tools.IsEmbedded():
            play              = CreatePlay()
            play.path         = stream_id.replace("ipad/adaptive", "a3t/progressive").replace("m3u8","mp4")
            play.content_type = 'video/mp4'

        else:
            params = { 'quality': 'A' }
            playlist_url = "playlist://%s?%s" % (quote_plus(stream_id), urlencode(params))

            play              = CreatePlay()
            play.path         = playlist_url
            play.content_type = 'application/vnd.apple.mpegurl'

        return play

    def getDate(self, datestring):
        c = time.strptime(datestring,"%Y-%m-%d")
        return time.strftime("%d-%b", c)
