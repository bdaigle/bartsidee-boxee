import mc, re, ba
from beautifulsoup.BeautifulSoup import BeautifulSoup

global url, zender, urlshow

base_url = 'http://itunes.apple.com/'
country = {'AR':'Argentina','AU':'Australia','AT':'Austria','BE':'Belgium','BR':'Brazil','CA':'Canada','CL':'Chile','CN':'China','CO':'Colombia','CR':'Costa Rica','HR':'Croatia','CZ':'Czech Republic','DK':'Denmark','SV':'El Salvador','FI':'Finland','FR':'France','DE':'Germany','GR':'Greece','GT':'Guatemala','HK':'Hong Kong','HU':'Hungary','IN':'India','ID':'Indonesia','IE':'Ireland','IL':'Israel','IT':'Italy','JP':'Japan','KR':'Korea, Republic Of','KW':'Kuwait','LB':'Lebanon','LU':'Luxembourg','MY':'Malaysia','MX':'Mexico','NL':'Netherlands','NZ':'New Zealand','NO':'Norway','PK':'Pakistan','PA':'Panama','PE':'Peru','PH':'Philippines','PL':'Poland','PT':'Portugal','QA':'Qatar','RO':'Romania','RU':'Russia','SA':'Saudi Arabia','SG':'Singapore','SK':'Slovakia','SI':'Slovenia','ZA':'South Africa','ES':'Spain','LK':'Sri Lanka','SE':'Sweden','CH':'Switzerland','TW':'Taiwan','TH':'Thailand','TR':'Turkey','GB':'UK','US':'USA','AE':'United Arab Emirates','VE':'Venezuela','VN':'Vietnam'}
genre = {'':'All Genres','1301':'Arts','1321':'Business','1303':'Comedy','1304':'Education','1323':'Games & Hobbies','1325':'Government & Organizations','1307':'Health','1305':'Kids & Family','1310':'Music','1311':'News & Politics','1314':'Religion & Spirituality','1315':'Science & Medicine','1324':'Society & Culture','1316':'Sports & Recreation','1318':'Technology','1309':'TV & Film'}

config = mc.GetApp().GetLocalConfig()

#ITUNES_BASE = 'http://itunes.apple.com/nl/rss/toppodcasts/limit=50/genre=1310/xml'

def GetCountry():
    list = mc.GetWindow(16000).GetList(61)
    list_items = mc.ListItems()
    
    i = 0
    focus = 0
    id = config.GetValue("country")
    for key in country.keys():
        list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
        list_item.SetLabel(country[key])
        list_item.SetPath(key)
        list_items.append(list_item)
        if key == id: focus = i
        i += 1
    list.SetItems(list_items)
    list.SetFocusedItem(focus)
    
    
def GetGenre():
    list = mc.GetWindow(16000).GetList(62)
    list_items = mc.ListItems()
    
    i = 0
    focus = 0
    id = config.GetValue("genre")
    for key in genre.keys():
        list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
        list_item.SetLabel(genre[key])
        list_item.SetPath(key)
        list_items.append(list_item)
        if key == id: focus = i
        i += 1
    list.SetItems(list_items)
    list.SetFocusedItem(focus)


def ShowNet():
    mc.ShowDialogWait()
    targetcontrol = 51
    targetwindow = 14000

    countryid = config.GetValue("country")
    genreid = config.GetValue("genre")
    if countryid == '': countryid = 'US'
    
    url = 'http://itunes.apple.com/'+countryid+'/rss/toppodcasts/limit=50/genre='+genreid+'/xml'

    list = mc.GetWindow(targetwindow).GetList(targetcontrol)
    list_items = mc.ListItems()

    data = ba.FetchUrl(url, 3600)
    soup = BeautifulSoup(data, convertEntities="xml", smartQuotesTo="xml")

    for info in soup.findAll('entry'):
        title = info.find('im:name').contents[0]
        link = info.link['href']
        thumb = info.find('im:image', {'height' : '170'}).contents[0]
        price = info.find('im:price')['amount']
        artist = info.find('im:artist').contents[0]
        try: summary = info.summary.contents[0]
        except: summary = ''

        if price == '0':
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(title.encode('utf-8', 'ignore'))
            list_item.SetThumbnail(str(thumb))
            list_item.SetPath(str(link))
            list_item.SetDescription(summary.encode('utf-8', 'ignore'))
            list_item.SetArtist(artist.encode('utf-8', 'ignore'))
            list_items.append(list_item)

    Label = mc.GetWindow(targetwindow).GetLabel(10102)
    Label.SetLabel('[B]Country:[/B] '+country[countryid]+'[CR][B]Genre:[/B] '+genre[genreid])
    
    mc.HideDialogWait()
    list.SetItems(list_items)



def ShowEpisode(urlshow, title = ""):
    targetcontrol  	= 52
    targetwindow   	= 14000

    mc.ShowDialogWait()
    data = ba.FetchUrl(urlshow, 3600)
    soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES, smartQuotesTo="xml")

    list = mc.GetWindow(targetwindow).GetList(targetcontrol)
    list_items = mc.ListItems()

    for info in soup.findAll('tr', {'class' : 'podcast-episode'}):
        try: title = info['preview-title']
        except: pass
        try: link = info['video-preview-url']
        except:
            try: link = info['audio-preview-url']
            except: link = False
        if link:
            list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            list_item.SetLabel(title.encode('utf-8', 'ignore'))
            list_item.SetPath(str(link))
            list_items.append(list_item)
            
    mc.HideDialogWait()
    list.SetItems(list_items)

def ShowPlay(url, title = ""):
    player = mc.GetPlayer()
    if '.mp4' in url: list_item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_OTHER)
    else: list_item = mc.ListItem(mc.ListItem.MEDIA_AUDIO_OTHER)
    list_item.SetPath(str(url))
    list_item.SetLabel(str(title))
    list_item.SetReportToServer(True)
    list_item.SetAddToHistory(True)
    player.Play(list_item)
    config.SetValue("play", 'True')

def EmptyEpisode():
    targetcontrol  	= 52
    targetwindow   	= 14000
    list = mc.GetWindow(targetwindow).GetList(targetcontrol)
    list_items = mc.ListItems()
    list_item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    list_item.SetLabel('')
    list_item.SetPath('')
    list_items.append(list_item)
    list.SetItems(list_items)