from default import *
from library import *
import tools

sys.path.append(os.path.join(CWD, 'external'))

import base64
from BeautifulSoup import BeautifulSoup
from urllib import quote_plus, urlencode
import datetime
try:    import simplejson as json
except: import json
try:    import md5
except: import haslib as md5

class Module(BARTSIDEE_MODULE):
    def __init__(self, app):
        self.app            = app
        BARTSIDEE_MODULE.__init__(self, app)

        self.name           = "Uitzending Gemist"        #Name of the channel
        self.type           = ['search','genre']         #Choose between 'search', 'list', 'genre'
        self.episode        = True                       #True if the list has episodes
        self.filter         = ['NL1','NL2','NL3']        #Option to set a filter to the list
        self.genrelist      = {'Kijktips':'kijktips', 'Vandaag':'vandaag','Gisteren':'gisteren'}
        self.genre          = ['Vandaag','Gisteren']
        self.content_type   = 'video/x-ms-asf'           #Mime type of the content to be played
        self.country        = 'NL'                       #2 character country id code
        
        self.url_base = 'http://www.uitzendinggemist.nl'
        self.initDate()

    def Search(self, search):
        url = self.url_base + '/zoek/autocomplete?cookie_consent=1&query=' + quote_plus(search)
        data = tools.urlopen(self.app, url, {'xhr':True})

        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES, smartQuotesTo="xml")
        div_page = soup.find("ul")
        
        streamlist = list()
        try:
            div_page.findAll("a")
        except:
            return streamlist

        for info in div_page.findAll('a'):
            stream = CreateList()
            stream.name     =  info.contents[0]
            stream.id       =  info['href']
            streamlist.append(stream)

        return streamlist
    
    def Episode(self, stream_name, stream_id, page, totalpage):
        url = self.url_base + stream_id + '/afleveringen?_pjax=true&page=' + str(page)
  
        data = tools.urlopen(self.app, url, {'cache':3600})
     
        if data == "":
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            episodelist = list()
            return episodelist

        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES, smartQuotesTo="xml")

        if totalpage == "":
            try:
                pages = soup.findAll( 'div', {'class' : 'pagination'})[0]
                pages = pages.findAll('a')
                totalpage = int(pages[len(pages)-2].contents[0])
            except:
                totalpage = 1

        episodelist = list()
        for info in soup.findAll('li'):
            i = info.findAll('div', {"class" : "description"})[0]
            try:
		id = i.h3.a['href']
            except:
		id = False
            try:
                t = info.findAll('img')[0]['data-images']
                thumb = 'http' + re.compile("http(.*?)jpg", re.DOTALL + re.IGNORECASE).search(str(t)).group(1) + 'jpg'
            except:
                thumb = info.findAll('img')[0]['src']
            if id:
		episode = CreateEpisode()
		episode.name            =   stream_name
		episode.id              =   self.url_base + id
		episode.description     =   i.text
		episode.thumbnails      =   thumb
		episode.date            =   i.h3.a.contents[0]
		episode.page            =   page
		episode.totalpage       =   totalpage
		episodelist.append(episode)

        return episodelist

    def Genre(self, genre, filter, page, totalpage):
        if genre == 'Kijktips':
            url = self.url_base + '/kijktips?cookie_consent=1&page=' + str(page)
            id = 'kijktips'
        else: 
            url = self.url_base + '/weekarchief/' + self.genrelist[genre]
            url += '?cookie_consent=1&display_mode=detail&_pjax=true&page=' + str(page)
            if filter != "": url = url + '&zender=' + filter
            id = 'week'

        data = tools.urlopen(self.app, url, {'cache':3600})
        genrelist = []
        if data == "":
            mc.ShowDialogNotification("No genre found for " + str(genre))
            return genrelist

        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES, smartQuotesTo="xml")
        if totalpage == "":
            try:
                pagediv = soup.findAll( 'div', {'class' : 'pagination'})[0]
                apage = pagediv.findAll("a")
                totalpage = int(apage[len(apage)-1].contents[0])
            except:
                totalpage = 1


        if id == 'kijktips':
            div_show = soup.find( 'div', {'id' : 'kijktips'})
            list = div_show.findAll("li")

        else:
            div_show = soup.find('ol', {'class' : 'episodes detail'})
            list = div_show.findAll("li")

        for info in list:
            try:
                thumb = info.findAll(attrs={"class" : "thumbnail loaded"})[0]['src']
            except:
                thumb = info.findAll(attrs={"class" : "thumbnail"})[0]['src']

            filters = ""

            if id == 'kijktips':
                i = info.findAll('div', {"class" : "description"})[0]
                title = i.h3.a.contents[0]
                desc = i.p.contents[0]
                date = i.h2contents[0]
                path = self.url_base + i.h3.a['href']
            else:
                i = info.findAll('div', {"class" : "info"})[0]
                f = i.span.img['alt']
                if "NL1" in f.upper(): filters = "NL1"
                if "NL2" in f.upper(): filters = "NL2"
                if "NL3" in f.upper(): filters = "NL3"

                title = i.h2.a['title']+': [COLOR FFA6A6A6]'+i.h3.a['title']+'[/COLOR]'
                desc = self.url_base + i.contents[0]
                date = i.span.text.replace(' ', '').replace('om', '').replace('op', '')
                path = self.url_base + i.h3.a['href']

            genreitem = CreateEpisode()
            genreitem.name          =   title
            genreitem.id            =   path
            genreitem.description   =   desc
            genreitem.thumbnails    =   thumb
            genreitem.filter        =   filters
            genreitem.date          =   date
            genreitem.page          =   page
            genreitem.totalpage     =   totalpage
            genrelist.append(genreitem)

        return genrelist
        
    def Play(self, stream_name, stream_id, subtitle):
        data = tools.urlopen(self.app, stream_id, {'cache':3600})
        streamid = re.compile('data-episode-id="(.*?)"', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        playerid = re.compile('data-player-id="(.*?)"', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
        
        if playerid: 
            print "playerid: "+playerid
            data = tools.urlopen(self.app, 'http://ida.omroep.nl/npoplayer/i.js', {'cache':0})
            token = re.compile('.token\s*=\s*"(.*?)"', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
            
            data = tools.urlopen(self.app, 'http://ida.omroep.nl/odiplus/?prid='+playerid+'&puboptions=adaptive&adaptive=yes&part=1&token='+token, {'cache':0})
            json_data = json.loads(data)
            if not json_data['streams'][0]:
                mc.ShowDialogNotification("Geen stream beschikbaar...")
                return
            
            streamdataurl = json_data['streams'][0]
            streamurl = str(streamdataurl.split("?")[0]) + '?extension=m3u8'
            
            data = tools.urlopen(self.app, streamurl, {'cache':0})
            json_data = json.loads(data)

            if not json_data['url']:
                mc.ShowDialogNotification("Geen stream beschikbaar...")
                return
        
            url_play = json_data['url']
            
            params = { 'quality': 'A' }
            playlist_url = "playlist://%s?%s" % (quote_plus(url_play), urlencode(params))

            play              = CreatePlay()
            play.path         = playlist_url
            play.content_type = 'application/vnd.apple.mpegurl'
            
            return play
        
        elif streamid: 
            print "streamid: "+streamid
            data = tools.urlopen(self.app, 'http://pi.omroep.nl/info/security', {'cache':0})
            soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")
            try:
                key = soup.session.key.contents[0]
            except:
                mc.ShowDialogNotification("Kan de security key niet ophalen")
                return
            security = base64.b64decode(key)

            securitystr = str(security).split('|')[1]
            md5code = streamid + '|' + securitystr
            md5code = md5.md5(md5code).hexdigest()

            streamdataurl = 'http://pi.omroep.nl/info/stream/aflevering/' + str(streamid) + '/' + str(md5code).upper()
            data = tools.urlopen(self.app, streamdataurl, {'cache':0}).decode('utf-8')

            xmlSoup = BeautifulSoup(data)
            streamurl = xmlSoup.find(attrs={"compressie_formaat" : "wvc1"})
            url_play = streamurl.streamurl.contents[0].replace(" ","").replace("\n","").replace("\t","")
           
            play = CreatePlay()
            play.path               =   url_play
            if subtitle and streamid:
                play.subtitle       =   self.GetSubtitle(security, streamid)
                play.subtitle_type  =   'sami'

            return play  
        
        else:
            print "not found: "
            mc.ShowDialogNotification("Geen stream beschikbaar...")
            return

    def initDate(self):
        now = datetime.datetime.now()
        for i in range(2, 7):
            newdate = now - datetime.timedelta(days=i)
            self.genrelist[newdate.strftime("%d-%b")] = newdate.strftime("%Y-%m-%d")
            self.genre.append(newdate.strftime("%d-%b"))

    def GetSubtitle(self, security, streamid):
        samisecurity1 = int(str(security).split('|')[0])
        samisecurity2 = str(security).split('|')[3]
        str4 = hex(samisecurity1)[2:]
        str5 = 'aflevering/' + streamid + '/format/sami'
        str6 = 'embedplayer'
        samimd5 = str(samisecurity2) + str(str5) + str(str4) + str(str6)
        str7 = md5.md5(samimd5).hexdigest()
        url = 'http://ea.omroep.nl/tt888/' + str(str6) + '/' + str(str7).lower() + '/' + str(str4) + '/' + str(str5)
        return url



   