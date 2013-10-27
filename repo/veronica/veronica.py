from default import *
from library import *
import tools

sys.path.append(os.path.join(CWD, 'external'))

from BeautifulSoup import BeautifulSoup
from urllib import quote_plus

import pyamf
from pyamf import remoting
import httplib

class Module(BARTSIDEE_MODULE):
    def __init__(self, app):
        self.app            = app
        BARTSIDEE_MODULE.__init__(self, app)

        self.name           = "Veronica Gemist"                     #Name of the channel
        self.type           = ['list']                          #Choose between 'search', 'list', 'genre'
        self.episode        = True                              #True if the list has episodes
        self.content_type   = 'video/x-flv'                     #Mime type of the content to be played
        self.country        = 'NL'                              #2 character country id code


        self.url_base       = 'http://www.veronicatv.nl'

    def List(self):
        index = ['0-9abcdef', 'ghijkl', 'mnopqr', 'stuvwxyz']
        data = []

        for i in index:
            url  = self.url_base + '/ajax/programFilter/day/0/genre/all/block/programs/range/' + i
            data.extend(self.process(url))

        streamlist = []
        for item in data:
            stream = CreateList()
            stream.name     =   item['label']
            stream.id       =   item['id']
            streamlist.append(stream)

        return streamlist

    def Episode(self, stream_name, stream_id, page, totalpage):
        url  = str(stream_id) + '/afleveringen'
        data = tools.urlopen(self.app, url, {'cache':3600})


        if data.rfind('Programma Video') != -1:
            parse = '/afleveringen'
        else:
            url   = str(stream_id) + '/videos'
            data  = tools.urlopen(self.app, url, {'cache':3600})
            parse = '/videos'
            
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES, smartQuotesTo="xml")
        
        try:
            submenu   = soup.findAll('div', {'class' : 'subMenu'})[0]
            pages     = submenu.findAll('li')
            totalpage = len(pages)
        except:
            totalpage = 1

        if page != 1:
            i    = totalpage - page
            id   = str(pages[i].a.contents[0])
            url  = str(stream_id) + parse + '/' + id.replace(' ', '-')
            data = tools.urlopen(self.app, url, {'cache':3600})
            soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES, smartQuotesTo="xml")
        else:
            try:    id   = str(pages[totalpage-1].a.contents[0])
            except: id = ''

        if parse == '/afleveringen':
            episodes = soup.findAll('div', {'class' : 'i iMargin iEpisode iBorder'})

            if not episodes:
                return []

            episodelist = []
            for item in episodes:
                body  = item.findAll('div', {'class' : 'iBody'})
                url   = item.findAll('a',   {'class' : 'btnSmall'})

                if not url or not body:
                    continue

                if not 'Video' in url[0].prettify():
                    continue

                p = body[0].findAll('p')

                episode                 =   CreateEpisode()
                episode.name            =   body[0].h2.string
                episode.id              =   self.url_base + url[0]['href']
                episode.thumbnails      =   self.url_base + item.find('img')['src']
                episode.date            =   p[0].string
                episode.description     =   id + ' ' + tools.encodeUTF8(p[1].string)
                episode.page            =   page
                episode.totalpage       =   totalpage
                episodelist.append(episode)

        elif parse == '/videos':
            episodes = soup.findAll('div', {'class' : 'i iGuide iGuideSlider'})

            if not episodes:
                return []

            episodelist = []
            for item in episodes:
                body  = item.findAll('div', {'class' : 'iBody'})
                url   = item.findAll('a',   {'class' : 'm mMargin'})

                if not url or not body:
                    continue

                p = body[0].findAll('p')

                episode                 =   CreateEpisode()
                episode.name            =   body[0].h2.string
                episode.id              =   self.url_base + url[0]['href']
                episode.thumbnails      =   self.url_base + item.find('img')['src']
                episode.description     =   id
                episode.date            =   p[0].string
                episode.page            =   page
                episode.totalpage       =   totalpage
                episodelist.append(episode)

        return episodelist

    def Play(self, stream_name, stream_id, subtitle):
        data  = tools.urlopen(self.app, str(stream_id), {'cache':3600})
        
        contentId = re.compile('videoPlayer\\\\" value=\\\\"(.*?)\\\\"', re.DOTALL + re.MULTILINE).search(str(data)).group(1)
        playerKey = re.compile('playerKey\\\\" value=\\\\"(.*?)\\\\"', re.DOTALL + re.MULTILINE).search(str(data)).group(1)
        seed = "61773bc7479ab4e69a5214f17fd4afd21fe1987a"
        
        amfHelper = BrightCoveHelper(playerKey, contentId, str(stream_id), seed)
        
        streams = {}
        for stream, bitrate in amfHelper.GetStreamInfo():
            s = {}
            s["uri"] = stream
            streams[bitrate] = s

        sort = []
        for key in sorted(streams.iterkeys()):
            sort.append(int(key))
            sort = sorted(sort)

        quality = sort.pop()
        rtmp = streams[int(quality)]["uri"]
        domain, file  = rtmp.split('/&')

        url                 =   'http://www.bartsidee.nl/flowplayer/player.php?url=' + str(domain) + '&clip=' + str(file)
        play                =   CreatePlay()
        play.content_type   =   'video/x-flv'
        play.path           =   quote_plus(url)
        play.domain         =   'bartsidee.nl'

        return play

    def process(self, url):
        html = tools.urlopen(self.app, url, {'cache':3600})
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES, smartQuotesTo="xml")
        data = []

        div_main = soup.findAll('div', {'class' : 'i iGrid'})
        if not div_main:
            return data

        for div in div_main:
            thumb = self.url_base + div.a.img['src']
            label = div.div.h2.a.contents[0]
            id   = self.url_base + div.div.h2.a['href']
            data.append({'label':label, 'thumb':thumb, 'id':id,})

        return data

class BrightCoveHelper:
    """ BrightCoveHelper is used to get video info of videos that use the 
    BrightCover SWF player.
        
    """
    
    def __init__(self, playerKey, contentId, url, seed, experienceId=0, amfVersion=3):
        """ Initializes the BrightCoveHelper """
        
        self.playerKey = playerKey
        self.contentId = contentId
        self.url = url
        self.seed = seed
        self.experienceId = experienceId
        self.amfVersion = amfVersion
        
        self.logger = False
        self.data = self.__GetBrightCoveData()
        return
    
    def GetStreamInfo(self):
        """ Returns the streams in the form of a list of 
        tuples (streamUrl, bitrate).
        
        """
        
        streams = []
        streamData = self.data['renditions']
        for stream in streamData:
            bitrate = int(stream['encodingRate'])/1000
            # The result is Unicode, so we should encode it.
            strm = stream['defaultURL']
            streams.append((strm, bitrate))
            
        return streams
    
    def __GetBrightCoveData(self):
        """ Retrieves the Url's from a brightcove stream
        
        Arguments:
        playerKey : string - Key identifying the current request
        contentId : int    - ID of the content to retrieve
        url       : string - Url of the page that calls the video SWF
        seed      : string - Constant which depends on the website
        
        Keyword Arguments:
        experienceId : id     - <unknown parameter>
        
        Returns a dictionary with the data
        
        """
        
        # Seed = 61773bc7479ab4e69a5214f17fd4afd21fe1987a
        envelope = self.__BuildBrightCoveAmfRequest(self.playerKey, self.contentId, self.url, self.experienceId, self.seed)
        
        connection = httplib.HTTPConnection("c.brightcove.com")
        connection.request("POST", "/services/messagebroker/amf?playerKey="+self.playerKey, str(remoting.encode(envelope).read()),{'content-type': 'application/x-amf'})
        response = connection.getresponse().read()
        response = remoting.decode(response).bodies[0][1].body
        
        #self.logger.debug(response)     
        return response['programmedContent']['videoPlayer']['mediaDTO']       
    
    def __BuildBrightCoveAmfRequest(self, playerKey, contentId, url, experienceId, seed):
        """ Builds a AMF request compatible with BrightCove
        
        Arguments:
        playerKey : string - Key identifying the current request
        contentId : int    - ID of the content to retrieve
        url       : string - Url of the page that calls the video SWF 
        seed      : string - Constant which depends on the website
        
        Keyword Arguments:
        experienceId : id     - <unknown parameter>
        
        Returns a valid Brightcove request
        
        """
        
        if self.logger:
            self.logger.debug("Creating BrightCover request for ContentId=%s, Key=%s, ExperienceId=%s, url=%s", contentId, playerKey, experienceId, url)
        else:
            print "Creating BrightCover request for ContentId=%s, Key=%s, ExperienceId=%s, url=%s" % (contentId, playerKey, experienceId, url)
        
        #const = '686a10e2a34ec3ea6af8f2f1c41788804e0480cb'
        pyamf.register_class(ViewerExperienceRequest, 'com.brightcove.experience.ViewerExperienceRequest')
        pyamf.register_class(ContentOverride, 'com.brightcove.experience.ContentOverride')
        
        contentOverrides = [ContentOverride(int(contentId))]
        viewerExperienceRequest = ViewerExperienceRequest(url, contentOverrides, int(experienceId), playerKey)
    
        envelope = remoting.Envelope(amfVersion=self.amfVersion)
        remotingRequest = remoting.Request(target="com.brightcove.experience.ExperienceRuntimeFacade.getDataForExperience",body=[seed, viewerExperienceRequest],envelope=envelope)
        envelope.bodies.append(("/1", remotingRequest))
        
        return envelope

class ViewerExperienceRequest(object):
    """ Class needed for brightcove AMF requests """
    def __init__(self, URL, contentOverrides, experienceId, playerKey, TTLToken=''):
        self.TTLToken = TTLToken
        self.URL = URL
        self.deliveryType = float(0)
        self.contentOverrides = contentOverrides
        self.experienceId = experienceId
        self.playerKey = playerKey

class ContentOverride(object):
    """ Class needed for brightcove AMF requests """
    def __init__(self, contentId, contentType=0, target='videoPlayer'):
        self.contentType = contentType
        self.contentId = contentId
        self.target = target
        self.contentIds = None
        self.contentRefId = None
        self.contentRefIds = None
        self.contentType = 0
        self.featureId = float(0)
        self.featuredRefId = None
        