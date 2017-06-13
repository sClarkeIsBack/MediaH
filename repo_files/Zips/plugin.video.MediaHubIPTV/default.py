 #############Imports#############
import xbmc,xbmcaddon,xbmcgui,xbmcplugin,base64,os,re,unicodedata,requests,time,string,sys,urllib,urllib2,json,urlparse,datetime,zipfile,shutil
from resources.modules import client,control,tools,shortlinks
from datetime import date
import xml.etree.ElementTree as ElementTree


#################################

#############Defined Strings#############
addon_id     = 'plugin.video.MediaHubIPTV'
addon_name   = 'MediaHub IPTV'
icon         = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
fanart       = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))

username     = control.setting('Username')
password     = control.setting('Password')

host         = 'http://mediahubiptv.ddns.net'
port         = '4545'

live_url     = '%s:%s/enigma2.php?username=%s&password=%s&type=get_live_categories'%(host,port,username,password)
vod_url      = '%s:%s/enigma2.php?username=%s&password=%s&type=get_vod_categories'%(host,port,username,password)
panel_api    = '%s:%s/panel_api.php?username=%s&password=%s'%(host,port,username,password)
play_url     = '%s:%s/live/%s/%s/'%(host,port,username,password)


Guide = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.MediaHubIPTV/resources/catchup', 'guide.xml'))
GuideLoc = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.MediaHubIPTV/resources/catchup', 'g'))

advanced_settings           =  xbmc.translatePath('special://home/addons/'+addon_id+'/resources/advanced_settings')
advanced_settings_target    =  xbmc.translatePath(os.path.join('special://home/userdata','advancedsettings.xml'))

KODIV        = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
#########################################

def buildcleanurl(url):
	url = str(url).replace('USERNAME',username).replace('PASSWORD',password)
	return url
def start():
	if username=="":
		user = userpopup()
		passw= passpopup()
		control.setSetting('Username',user)
		control.setSetting('Password',passw)
		xbmc.executebuiltin('Container.Refresh')
		auth = '%s:%s/enigma2.php?username=%s&password=%s&type=get_vod_categories'%(host,port,user,passw)
		auth = tools.OPEN_URL(auth)
		if auth == "":
			line1 = "Incorrect Login Details"
			line2 = "Please Re-enter" 
			line3 = "" 
			xbmcgui.Dialog().ok('Attention', line1, line2, line3)
			start()
		else:
			line1 = "Login Sucsessfull"
			line2 = "Welcome to MediaHub IPTV" 
			line3 = ('[COLOR blue]%s[/COLOR]'%user)
			xbmcgui.Dialog().ok('MediaHub IPTV', line1, line2, line3)
			tvguidesetup()
			addonsettings('ADS2','')
			xbmc.executebuiltin('Container.Refresh')
			home()
	else:
		auth = '%s:%s/enigma2.php?username=%s&password=%s&type=get_vod_categories'%(host,port,username,password)
		auth = tools.OPEN_URL(auth)
		if not auth=="":
			tools.addDir('Account Information','url',6,icon,fanart,'')
			tools.addDir('Live TV','live',1,icon,fanart,'')
			tools.addDir('Live Events','events',1,icon,fanart,'')
			tools.addDir('Catchup TV','url',12,icon,fanart,'')
			if xbmc.getCondVisibility('System.HasAddon(pvr.iptvsimple)') or xbmc.getCondVisibility('System.HasAddon(script.ivueguide)'):
				tools.addDir('TV Guide','pvr',7,icon,fanart,'')
			tools.addDir('VOD','vod',3,icon,fanart,'')
			tools.addDir('Search','url',5,icon,fanart,'')
			tools.addDir('Settings','url',8,icon,fanart,'')
			tools.addDir('Extras','url',16,icon,fanart,'')
			if not control.setting('review')=='true':
				tools.addDir('[COLOR blue][B]Click To Leave a Review![/B][/COLOR]','url',21,icon,fanart,'')
				
def home():
	tools.addDir('Account Information','url',6,icon,fanart,'')
	tools.addDir('Live TV','live',1,icon,fanart,'')
	tools.addDir('Live Events','events',1,icon,fanart,'')
	tools.addDir('Catchup TV','url',12,icon,fanart,'')
	if xbmc.getCondVisibility('System.HasAddon(pvr.iptvsimple)'):
		tools.addDir('TV Guide','pvr',7,icon,fanart,'')
	tools.addDir('VOD','vod',3,icon,fanart,'')
	tools.addDir('Search','',5,icon,fanart,'')
	tools.addDir('Settings','url',8,icon,fanart,'')
	tools.addDir('Extras','url',16,icon,fanart,'')
	if not control.setting('review')=='true':
		tools.addDir('[COLOR blue][B]Click To Leave a Review![/B][/COLOR]','url',21,icon,fanart,'')
		
def livecategory(url):
	
	open = tools.OPEN_URL(live_url)
	all_cats = tools.regex_get_all(open,'<channel>','</channel>')
	for a in all_cats:
		name = tools.regex_from_to(a,'<title>','</title>')
		name = base64.b64decode(name)
		url1  = tools.regex_from_to(a,'<playlist_url>','</playlist_url>').replace('<![CDATA[','').replace(']]>','')
		if not 'Install Videos' in name:
			if not 'TEST CHANNELS' in name:
				if url == 'events':
					if 'Live:' in name:
						tools.addDir(name.replace('UK:','[COLOR blue]UK:[/COLOR]').replace('USA/CA:','[COLOR blue]USA/CA:[/COLOR]').replace('All','[COLOR blue]A[/COLOR]ll').replace('International','[COLOR blue]Int[/COLOR]ertaional').replace('Live:','[COLOR blue]Live:[/COLOR]').replace('TEST','[COLOR blue]TEST[/COLOR]').replace('Install','[COLOR blue]Install[/COLOR]').replace('24/7','[COLOR blue]24/7[/COLOR]').replace('INT:','[COLOR blue]INT:[/COLOR]').replace('DE:','[COLOR blue]DE:[/COLOR]').replace('FR:','[COLOR blue]FR:[/COLOR]').replace('PL:','[COLOR blue]PL:[/COLOR]').replace('AR:','[COLOR blue]AR:[/COLOR]').replace('LIVE:','[COLOR blue]LIVE:[/COLOR]').replace('ES:','[COLOR blue]ES:[/COLOR]').replace('IN:','[COLOR blue]IN:[/COLOR]').replace('PK:','[COLOR blue]PK:[/COLOR]'),url1,2,icon,fanart,'')
				else:
					if not 'Live:' in name:
						tools.addDir(name.replace('UK:','[COLOR blue]UK:[/COLOR]').replace('USA/CA:','[COLOR blue]USA/CA:[/COLOR]').replace('All','[COLOR blue]A[/COLOR]ll').replace('International','[COLOR blue]Int[/COLOR]ertaional').replace('Live:','[COLOR blue]Live:[/COLOR]').replace('TEST','[COLOR blue]TEST[/COLOR]').replace('Install','[COLOR blue]Install[/COLOR]').replace('24/7','[COLOR blue]24/7[/COLOR]').replace('INT:','[COLOR blue]INT:[/COLOR]').replace('DE:','[COLOR blue]DE:[/COLOR]').replace('FR:','[COLOR blue]FR:[/COLOR]').replace('PL:','[COLOR blue]PL:[/COLOR]').replace('AR:','[COLOR blue]AR:[/COLOR]').replace('LIVE:','[COLOR blue]LIVE:[/COLOR]').replace('ES:','[COLOR blue]ES:[/COLOR]').replace('IN:','[COLOR blue]IN:[/COLOR]').replace('PK:','[COLOR blue]PK:[/COLOR]'),url1,2,icon,fanart,'')
		
def Livelist(url):
	url  = buildcleanurl(url)
	open = tools.OPEN_URL(url)
	all_cats = tools.regex_get_all(open,'<channel>','</channel>')
	for a in all_cats:
		name = tools.regex_from_to(a,'<title>','</title>')
		name = base64.b64decode(name)
		xbmc.log(str(name))
		name = re.sub('\[.*?min ','-',name)
		thumb= tools.regex_from_to(a,'<desc_image>','</desc_image>').replace('<![CDATA[','').replace(']]>','')
		url1  = tools.regex_from_to(a,'<stream_url>','</stream_url>').replace('<![CDATA[','').replace(']]>','')
		desc = tools.regex_from_to(a,'<description>','</description>')
		tools.addDir(name.replace('UK:','[COLOR blue]UK:[/COLOR]').replace('USA/CA:','[COLOR blue]USA/CA:[/COLOR]').replace('All','[COLOR blue]A[/COLOR]ll').replace('International','[COLOR blue]Int[/COLOR]ertaional').replace('Live:','[COLOR blue]Live:[/COLOR]').replace('TEST','[COLOR blue]TEST[/COLOR]').replace('Install','[COLOR blue]Install[/COLOR]').replace('24/7','[COLOR blue]24/7[/COLOR]').replace('INT:','[COLOR blue]INT:[/COLOR]').replace('DE:','[COLOR blue]DE:[/COLOR]').replace('FR:','[COLOR blue]FR:[/COLOR]').replace('PL:','[COLOR blue]PL:[/COLOR]').replace('AR:','[COLOR blue]AR:[/COLOR]').replace('LIVE:','[COLOR blue]LIVE:[/COLOR]').replace('ES:','[COLOR blue]ES:[/COLOR]').replace('IN:','[COLOR blue]IN:[/COLOR]').replace('PK:','[COLOR blue]PK:[/COLOR]'),url1,4,thumb,fanart,base64.b64decode(desc))
		
	
def vod(url):
	if url =="vod":
		open = tools.OPEN_URL(vod_url)
	else:
		url  = buildcleanurl(url)
		open = tools.OPEN_URL(url)
	all_cats = tools.regex_get_all(open,'<channel>','</channel>')
	for a in all_cats:
		if '<playlist_url>' in open:
			name = tools.regex_from_to(a,'<title>','</title>')
			url1  = tools.regex_from_to(a,'<playlist_url>','</playlist_url>').replace('<![CDATA[','').replace(']]>','')
			tools.addDir(str(base64.b64decode(name)).replace('?',''),url1,3,icon,fanart,'')
		else:
			if xbmcaddon.Addon().getSetting('meta') == 'true':
				try:
					name = tools.regex_from_to(a,'<title>','</title>')
					name = base64.b64decode(name)
					thumb= tools.regex_from_to(a,'<desc_image>','</desc_image>').replace('<![CDATA[','').replace(']]>','')
					url  = tools.regex_from_to(a,'<stream_url>','</stream_url>').replace('<![CDATA[','').replace(']]>','')
					desc = tools.regex_from_to(a,'<description>','</description>')
					desc = base64.b64decode(desc)
					plot = tools.regex_from_to(desc,'PLOT:','\n')
					cast = tools.regex_from_to(desc,'CAST:','\n')
					ratin= tools.regex_from_to(desc,'RATING:','\n')
					year = tools.regex_from_to(desc,'RELEASEDATE:','\n').replace(' ','-')
					year = re.compile('-.*?-.*?-(.*?)-',re.DOTALL).findall(year)
					runt = tools.regex_from_to(desc,'DURATION_SECS:','\n')
					genre= tools.regex_from_to(desc,'GENRE:','\n')
					tools.addDirMeta(str(name).replace('[/COLOR].','.[/COLOR]'),url,4,thumb,fanart,plot,str(year).replace("['","").replace("']",""),str(cast).split(),ratin,runt,genre)
				except:pass
				xbmcplugin.setContent(int(sys.argv[1]), 'movies')
			else:
				name = tools.regex_from_to(a,'<title>','</title>')
				name = base64.b64decode(name)
				thumb= tools.regex_from_to(a,'<desc_image>','</desc_image>').replace('<![CDATA[','').replace(']]>','')
				url  = tools.regex_from_to(a,'<stream_url>','</stream_url>').replace('<![CDATA[','').replace(']]>','')
				desc = tools.regex_from_to(a,'<description>','</description>')
				tools.addDir(name,url,4,thumb,fanart,base64.b64decode(desc))
				
				
		
##############################################
#### RULE NO.1 - DONT WRITE CODE THAT IS  ####
#### ALREADY WRITTEN AND PROVEN TO WORK :)####
##############################################


def catchup():
    listcatchup()
		
def listcatchup():
	open = tools.OPEN_URL(panel_api)
	all  = tools.regex_get_all(open,'{"num','direct')
	for a in all:
		if '"tv_archive":1' in a:
			name = tools.regex_from_to(a,'"epg_channel_id":"','"').replace('\/','/')
			thumb= tools.regex_from_to(a,'"stream_icon":"','"').replace('\/','/')
			id   = tools.regex_from_to(a,'stream_id":"','"')
			if not name=="":
				tools.addDir(name.replace('KID:','[COLOR blue]KIDS:[/COLOR]').replace('UKS:','[COLOR blue]UKS:[/COLOR]').replace('ENT:','[COLOR blue]ENT:[/COLOR]').replace('DOC:','[COLOR blue]DOC:[/COLOR]').replace('MOV:','[COLOR blue]MOV:[/COLOR]').replace('SSS:','[COLOR blue]SSS:[/COLOR]').replace('BTS:','[COLOR blue]BTS:[/COLOR]').replace('TEST','[COLOR blue]TEST[/COLOR]').replace('Install','[COLOR blue]Install[/COLOR]').replace('24/7','[COLOR blue]24/7[/COLOR]').replace('INT:','[COLOR blue]INT:[/COLOR]').replace('DE:','[COLOR blue]DE:[/COLOR]').replace('FR:','[COLOR blue]FR:[/COLOR]').replace('PL:','[COLOR blue]PL:[/COLOR]').replace('AR:','[COLOR blue]AR:[/COLOR]').replace('LIVE:','[COLOR blue]LIVE:[/COLOR]').replace('ES:','[COLOR blue]ES:[/COLOR]').replace('IN:','[COLOR blue]IN:[/COLOR]').replace('PK:','[COLOR blue]PK:[/COLOR]'),'url',13,thumb,fanart,id)
			

def tvarchive(name,description):
    days = 7
	
    now = str(datetime.datetime.now()).replace('-','').replace(':','').replace(' ','')
    date3 = datetime.datetime.now() - datetime.timedelta(days)
    date = str(date3)
    date = str(date).replace('-','').replace(':','').replace(' ','')
    APIv2 = base64.b64decode("JXM6JXMvcGxheWVyX2FwaS5waHA/dXNlcm5hbWU9JXMmcGFzc3dvcmQ9JXMmYWN0aW9uPWdldF9zaW1wbGVfZGF0YV90YWJsZSZzdHJlYW1faWQ9JXM=")%(host,port,username,password,description)
    link=tools.OPEN_URL(APIv2)
    match = re.compile('"title":"(.+?)".+?"start":"(.+?)","end":"(.+?)","description":"(.+?)"').findall(link)
    for ShowTitle,start,end,DesC in match:
        ShowTitle = base64.b64decode(ShowTitle)
        DesC = base64.b64decode(DesC)
        format = '%Y-%m-%d %H:%M:%S'
        try:
            modend = dtdeep.strptime(end, format)
            modstart = dtdeep.strptime(start, format)
        except:
            modend = datetime.datetime(*(time.strptime(end, format)[0:6]))
            modstart = datetime.datetime(*(time.strptime(start, format)[0:6]))
        StreamDuration = modend - modstart
        modend_ts = time.mktime(modend.timetuple())
        modstart_ts = time.mktime(modstart.timetuple())
        FinalDuration = int(modend_ts-modstart_ts) / 60
        strstart = start
        Realstart = str(strstart).replace('-','').replace(':','').replace(' ','')
        start2 = start[:-3]
        editstart = start2
        start2 = str(start2).replace(' ',' - ')
        start = str(editstart).replace(' ',':')
        Editstart = start[:13] + '-' + start[13:]
        Finalstart = Editstart.replace('-:','-')
        if Realstart > date:
            if Realstart < now:
                catchupURL = base64.b64decode("JXM6JXMvc3RyZWFtaW5nL3RpbWVzaGlmdC5waHA/dXNlcm5hbWU9JXMmcGFzc3dvcmQ9JXMmc3RyZWFtPSVzJnN0YXJ0PQ==")%(host,port,username,password,description)
                ResultURL = catchupURL + str(Finalstart) + "&duration=%s"%(FinalDuration)
                kanalinimi = "[COLOR blue]%s[/COLOR] - %s"%(start2,ShowTitle)
                tools.addDir(kanalinimi,ResultURL,4,icon,fanart,DesC)

	
					
def DownloaderClass(url, dest):
    dp = xbmcgui.DialogProgress()
    dp.create('Fetching latest Catch Up',"Fetching latest Catch Up...",' ', ' ')
    dp.update(0)
    start_time=time.time()
    urllib.urlretrieve(url, dest, lambda nb, bs, fs: _pbhook(nb, bs, fs, dp, start_time))

def _pbhook(numblocks, blocksize, filesize, dp, start_time):
        try: 
            percent = min(numblocks * blocksize * 100 / filesize, 100) 
            currently_downloaded = float(numblocks) * blocksize / (1024 * 1024) 
            kbps_speed = numblocks * blocksize / (time.time() - start_time) 
            if kbps_speed > 0: 
                eta = (filesize - numblocks * blocksize) / kbps_speed 
            else: 
                eta = 0 
            kbps_speed = kbps_speed / 1024 
            mbps_speed = kbps_speed / 1024 
            total = float(filesize) / (1024 * 1024) 
            mbs = '[COLOR white]%.02f MB of less than 5MB[/COLOR]' % (currently_downloaded)
            e = '[COLOR white]Speed:  %.02f Mb/s ' % mbps_speed  + '[/COLOR]'
            dp.update(percent, mbs, e)
        except: 
            percent = 100 
            dp.update(percent) 
        if dp.iscanceled():
            dialog = xbmcgui.Dialog()
            dialog.ok("MediaHubIPTV", 'The download was cancelled.')
				
            sys.exit()
            dp.close()
#####################################################################

def tvguide():
	if xbmc.getCondVisibility('System.HasAddon(pvr.iptvsimple)') and xbmc.getCondVisibility('System.HasAddon(script.ivueguide)'):
		dialog = xbmcgui.Dialog().select('Select a TV Guide', ['PVR TV Guide','iVue TV Guide'])
		if dialog==0:
			xbmc.executebuiltin('ActivateWindow(TVGuide)')
		elif dialog==1:
			xbmc.executebuiltin('RunAddon(script.ivueguide)')
	elif not xbmc.getCondVisibility('System.HasAddon(pvr.iptvsimple)') and xbmc.getCondVisibility('System.HasAddon(script.ivueguide)'):
		xbmc.executebuiltin('RunAddon(script.ivueguide)')
	elif xbmc.getCondVisibility('System.HasAddon(pvr.iptvsimple)') and not xbmc.getCondVisibility('System.HasAddon(script.ivueguide)'):
		xbmc.executebuiltin('ActivateWindow(TVGuide)')
def stream_video(url):
	url = buildcleanurl(url)
	url = str(url).replace('USERNAME',username).replace('PASSWORD',password)
	liz = xbmcgui.ListItem('', iconImage='DefaultVideo.png', thumbnailImage=icon)
	liz.setInfo(type='Video', infoLabels={'Title': '', 'Plot': ''})
	liz.setProperty('IsPlayable','true')
	liz.setPath(str(url))
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
	
	
def searchdialog():
	search = control.inputDialog(heading='Search MediaHub IPTV:')
	if search=="":
		return
	else:
		return search

	
def search():
	if mode==3:
		return False
	text = searchdialog()
	if not text:
		xbmc.executebuiltin("XBMC.Notification([COLOR blue][B]Search is Empty[/B][/COLOR],Aborting search,4000,"+icon+")")
		return
	xbmc.log(str(text))
	open = tools.OPEN_URL(panel_api)
	all_chans = tools.regex_get_all(open,'{"num":','epg')
	for a in all_chans:
		name = tools.regex_from_to(a,'name":"','"').replace('\/','/')
		url  = tools.regex_from_to(a,'"stream_id":"','"')
		thumb= tools.regex_from_to(a,'stream_icon":"','"').replace('\/','/')
		if text in name.lower():
			tools.addDir(name,play_url+url+'.ts',4,thumb,fanart,'')
		elif text not in name.lower() and text in name:
			tools.addDir(name,play_url+url+'.ts',4,thumb,fanart,'')

	
def settingsmenu():
	if xbmcaddon.Addon().getSetting('meta')=='true':
		META = '[COLOR lime]ON[/COLOR]'
	else:
		META = '[COLOR red]OFF[/COLOR]'
	if xbmcaddon.Addon().getSetting('update')=='true':
		UPDATE = '[COLOR lime]ON[/COLOR]'
	else:
		UPDATE = '[COLOR red]OFF[/COLOR]'
	tools.addDir('Edit Advanced Settings','ADS',10,icon,fanart,'')
	tools.addDir('META for VOD is %s'%META,'META',10,icon,fanart,META)
	tools.addDir('Log Out','LO',10,icon,fanart,'')
	

def addonsettings(url,description):
	url  = buildcleanurl(url)
	if   url =="CC":
		tools.clear_cache()
	elif url =="AS":
		xbmc.executebuiltin('Addon.OpenSettings(%s)'%addon_id)
	elif url =="ADS":
		dialog = xbmcgui.Dialog().select('Edit Advanced Settings', ['Enable Fire TV Stick AS','Enable Fire TV AS','Enable 1GB Ram or Lower AS','Enable 2GB Ram or Higher AS','Enable Nvidia Shield AS','Disable AS'])
		if dialog==0:
			advancedsettings('stick')
			xbmcgui.Dialog().ok('MediaHub IPTV', 'Set Advanced Settings')
		elif dialog==1:
			advancedsettings('firetv')
			xbmcgui.Dialog().ok('MediaHub IPTV', 'Set Advanced Settings')
		elif dialog==2:
			advancedsettings('lessthan')
			xbmcgui.Dialog().ok('MediaHub IPTV', 'Set Advanced Settings')
		elif dialog==3:
			advancedsettings('morethan')
			xbmcgui.Dialog().ok('MediaHub IPTV', 'Set Advanced Settings')
		elif dialog==4:
			advancedsettings('shield')
			xbmcgui.Dialog().ok('MediaHub IPTV', 'Set Advanced Settings')
		elif dialog==5:
			advancedsettings('remove')
			xbmcgui.Dialog().ok('MediaHub IPTV', 'Advanced Settings Removed')
	elif url =="ADS2":
		dialog = xbmcgui.Dialog().select('Select Your Device Or Closest To', ['Fire TV Stick ','Fire TV','1GB Ram or Lower','2GB Ram or Higher','Nvidia Shield'])
		if dialog==0:
			advancedsettings('stick')
			xbmcgui.Dialog().ok('MediaHub IPTV', 'Set Advanced Settings')
		elif dialog==1:
			advancedsettings('firetv')
			xbmcgui.Dialog().ok('MediaHub IPTV', 'Set Advanced Settings')
		elif dialog==2:
			advancedsettings('lessthan')
			xbmcgui.Dialog().ok('MediaHub IPTV', 'Set Advanced Settings')
		elif dialog==3:
			advancedsettings('morethan')
			xbmcgui.Dialog().ok('MediaHub IPTV', 'Set Advanced Settings')
		elif dialog==4:
			advancedsettings('shield')
			xbmcgui.Dialog().ok('MediaHub IPTV', 'Set Advanced Settings')
	elif url =="tv":
		dialog = xbmcgui.Dialog().select('Select a TV Guide to Setup', ['iVue TV Guide','PVR TV Guide','Both'])
		if dialog==0:
			ivueint()
			xbmcgui.Dialog().ok('MediaHub IPTV', 'iVue Integration Complete')
		elif dialog==1:
			pvrsetup()
			xbmcgui.Dialog().ok('MediaHub IPTV', 'PVR Integration Complete')
		elif dialog==2:
			pvrsetup()
			ivueint()
			xbmcgui.Dialog().ok('MediaHub IPTV', 'PVR & iVue Integration Complete')
	elif url =="ST":
		xbmc.executebuiltin('Runscript("special://home/addons/plugin.video.MediaHubIPTV/resources/modules/speedtest.py")')
	elif url =="META":
		if 'ON' in description:
			xbmcaddon.Addon().setSetting('meta','false')
			xbmc.executebuiltin('Container.Refresh')
		else:
			xbmcaddon.Addon().setSetting('meta','true')
			xbmc.executebuiltin('Container.Refresh')
	elif url =="LO":
		xbmcaddon.Addon().setSetting('Username','')
		xbmcaddon.Addon().setSetting('Password','')
		xbmc.executebuiltin('XBMC.ActivateWindow(Videos,addons://sources/video/)')
		xbmc.executebuiltin('Container.Refresh')
	elif url =="UPDATE":
		if 'ON' in description:
			xbmcaddon.Addon().setSetting('update','false')
			xbmc.executebuiltin('Container.Refresh')
		else:
			xbmcaddon.Addon().setSetting('update','true')
			xbmc.executebuiltin('Container.Refresh')
	
		
def advancedsettings(device):
	if device == 'stick':
		file = open(os.path.join(advanced_settings, 'stick.xml'))
	elif device == 'firetv':
		file = open(os.path.join(advanced_settings, 'firetv.xml'))
	elif device == 'lessthan':
		file = open(os.path.join(advanced_settings, 'lessthan1GB.xml'))
	elif device == 'morethan':
		file = open(os.path.join(advanced_settings, 'morethan1GB.xml'))
	elif device == 'shield':
		file = open(os.path.join(advanced_settings, 'shield.xml'))
	elif device == 'remove':
		os.remove(advanced_settings_target)
	
	try:
		read = file.read()
		f = open(advanced_settings_target, mode='w+')
		f.write(read)
		f.close()
	except:
		pass
		
	
def pvrsetup():
	correctPVR()
	return
		
		
def asettings():
	choice = xbmcgui.Dialog().yesno('MediaHub IPTV', 'Please Select The RAM Size of Your Device', yeslabel='Less than 1GB RAM', nolabel='More than 1GB RAM')
	if choice:
		lessthan()
	else:
		morethan()
	

def morethan():
		file = open(os.path.join(advanced_settings, 'morethan.xml'))
		a = file.read()
		f = open(advanced_settings_target, mode='w+')
		f.write(a)
		f.close()

		
def lessthan():
		file = open(os.path.join(advanced_settings, 'lessthan.xml'))
		a = file.read()
		f = open(advanced_settings_target, mode='w+')
		f.write(a)
		f.close()
		
		
def userpopup():
	kb =xbmc.Keyboard ('', 'heading', True)
	kb.setHeading('Enter Username')
	kb.setHiddenInput(False)
	kb.doModal()
	if (kb.isConfirmed()):
		text = kb.getText()
		return text
	else:
		return False

		
def passpopup():
	kb =xbmc.Keyboard ('', 'heading', True)
	kb.setHeading('Enter Password')
	kb.setHiddenInput(False)
	kb.doModal()
	if (kb.isConfirmed()):
		text = kb.getText()
		return text
	else:
		return False
		
		
def accountinfo():
	try:
		open = tools.OPEN_URL(panel_api)
		username   = tools.regex_from_to(open,'"username":"','"')
		password   = tools.regex_from_to(open,'"password":"','"')
		status     = tools.regex_from_to(open,'"status":"','"')
		connects   = tools.regex_from_to(open,'"max_connections":"','"')
		active     = tools.regex_from_to(open,'"active_cons":"','"')
		expiry     = tools.regex_from_to(open,'"exp_date":"','"')
		expiry     = datetime.datetime.fromtimestamp(int(expiry)).strftime('%d/%m/%Y - %H:%M')
		expreg     = re.compile('^(.*?)/(.*?)/(.*?)$',re.DOTALL).findall(expiry)
		for day,month,year in expreg:
			month     = tools.MonthNumToName(month)
			year      = re.sub(' -.*?$','',year)
			expiry    = month+' '+day+' - '+year
			ip        = tools.getlocalip()
			extip     = tools.getexternalip()
			tools.addDir('[COLOR blue]Username :[/COLOR] '+username,'','',icon,fanart,'')
			tools.addDir('[COLOR blue]Password :[/COLOR] '+password,'','',icon,fanart,'')
			tools.addDir('[COLOR blue]Expiry Date:[/COLOR] '+expiry,'','',icon,fanart,'')
			tools.addDir('[COLOR blue]Account Status :[/COLOR] %s'%status,'','',icon,fanart,'')
			tools.addDir('[COLOR blue]Current Connections:[/COLOR] '+ active,'','',icon,fanart,'')
			tools.addDir('[COLOR blue]Allowed Connections:[/COLOR] '+connects,'','',icon,fanart,'')
			tools.addDir('[COLOR blue]Local IP Address:[/COLOR] '+ip,'','',icon,fanart,'')
			tools.addDir('[COLOR blue]External IP Address:[/COLOR] '+extip,'','',icon,fanart,'')
			tools.addDir('[COLOR blue]Kodi Version:[/COLOR] '+str(KODIV),'','',icon,fanart,'')
	except:
		pass
		
	
def correctPVR():

	addon = xbmcaddon.Addon('plugin.video.MediaHubIPTV')
	username_text = addon.getSetting(id='Username')
	password_text = addon.getSetting(id='Password')
	jsonSetPVR = '{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"pvrmanager.enabled", "value":true},"id":1}'
	IPTVon 	   = '{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"pvr.iptvsimple","enabled":true},"id":1}'
	nulldemo   = '{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"pvr.demo","enabled":false},"id":1}'
	loginurl   = "http://mediahubiptv.ddns.net:4545/get.php?username=" + username_text + "&password=" + password_text + "&type=m3u_plus&output=ts"
	EPGurl     = "http://mediahubiptv.ddns.net:4545/xmltv.php?username=" + username_text + "&password=" + password_text + "&type=m3u_plus&output=ts"

	xbmc.executeJSONRPC(jsonSetPVR)
	xbmc.executeJSONRPC(IPTVon)
	xbmc.executeJSONRPC(nulldemo)
	
	moist = xbmcaddon.Addon('pvr.iptvsimple')
	moist.setSetting(id='m3uUrl', value=loginurl)
	moist.setSetting(id='epgUrl', value=EPGurl)
	moist.setSetting(id='m3uCache', value="false")
	moist.setSetting(id='epgCache', value="false")
	xbmc.executebuiltin("Container.Refresh")
	
def ivueint():
	iVue_SETTINGS = xbmc.translatePath(os.path.join('special://home/userdata/addon_data/script.ivueguide','settings.xml'))
	UseriVueSets = xbmc.translatePath(os.path.join('special://home/userdata/addon_data/script.ivueguide','oldsettings.xml'))
	FlawiVueSet = xbmc.translatePath(os.path.join('special://home/addons/'+addon_id+'/resources/ivue','ivueset.xml'))
	ivuetarget   =  xbmc.translatePath(os.path.join('special://home/userdata/addon_data/script.ivueguide/resources/ini/plugin.video.MediaHubIPTV'))
	inizip       = 	xbmc.translatePath(os.path.join('special://home/addons/plugin.video.MediaHubIPTV/resources/ivue','plugin.video.MediaHubIPTV.zip'))
	iVue_DATA = xbmc.translatePath(os.path.join('special://home/userdata/addon_data/script.ivueguide/'))
	RES = xbmc.translatePath('special://home/addons/plugin.video.MediaHubIPTV/resources/ivue/')
	if not xbmc.getCondVisibility('System.HasAddon(script.ivueguide)'):
		install('iVue','https://raw.githubusercontent.com/totaltec2014/ivue2/master/script.ivueguide/script.ivueguide-3.0.7.zip')
		xbmc.executebuiltin("UpdateAddonRepos")
		xbmc.executebuiltin("UpdateLocalAddons")
		time.sleep(5)

	if not xbmc.getCondVisibility('System.HasAddon(xbmc.repo.ivueguide)'):
		install('iVue','https://raw.githubusercontent.com/totaltec2014/ivue2/master/xbmc.repo.ivueguide/xbmc.repo.ivueguide-0.0.1.zip')
		xbmc.executebuiltin("UpdateAddonRepos")
		xbmc.executebuiltin("UpdateLocalAddons")
		time.sleep(5)

	if not os.path.isfile(iVue_SETTINGS):
		if not os.path.exists(iVue_DATA):
			os.makedirs(iVue_DATA)
		shutil.copyfile(FlawiVueSet, iVue_SETTINGS)
	else:
		os.remove(iVue_SETTINGS)
		xbmc.log('Old iVue settings deleted')
		if not os.path.exists(iVue_DATA):
			os.makedirs(iVue_DATA)
		shutil.copyfile(FlawiVueSet, iVue_SETTINGS)
	
	iVueEnable 	   = '{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"script.ivueguide","enabled":true},"id":1}'
	iVueRepoEnable 	   = '{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"xbmc.repo.ivueguide","enabled":true},"id":1}'
	xbmc.executeJSONRPC(iVueEnable)
	xbmc.executeJSONRPC(iVueRepoEnable)

	FullDB = os.path.join(RES, 'fullivue.zip')
	dp = xbmcgui.DialogProgress()
	dp.create("[COLOR white]"+addon_name+"[/COLOR]","Copying DB",'', 'Please Wait')
	unzip(FullDB,iVue_DATA,dp)
	xbmc.log("Full iVue Master DB Copied")
	
	dp = xbmcgui.DialogProgress()
	dp.create("MediaHubIPTV","Copying ini",'', 'Please Wait')
	unzip(inizip,ivuetarget,dp)

def install(name,url):
    from resources.modules import downloader
    path = xbmc.translatePath(os.path.join('special://home/addons','packages'))
    dp = xbmcgui.DialogProgress()
    dp.create("[COLOR white]"+addon_name+"[/COLOR]","Installing...",'', 'Please Wait')
    lib=os.path.join(path, 'content.zip')
    try:
       os.remove(lib)
    except:
       pass
    downloader.download(url, lib, dp)
    addonfolder = xbmc.translatePath(os.path.join('special://home','addons'))
    time.sleep(3)
    dp = xbmcgui.DialogProgress()
    dp.create("[COLOR white]"+addon_name+"[/COLOR]","Installing...",'', 'Please Wait')
    dp.update(0,"", "Installing... Please Wait")
    print '======================================='
    print addonfolder
    print '======================================='
    unzip(lib,addonfolder,dp)

def unzip(_in, _out, dp):
	__in = zipfile.ZipFile(_in,  'r')
	
	nofiles = float(len(__in.infolist()))
	count   = 0
	
	try:
		for item in __in.infolist():
			count += 1
			update = (count / nofiles) * 100
			
			if dp.iscanceled():
				dialog = xbmcgui.Dialog()
				dialog.ok(AddonTitle, 'Process was cancelled.')
				
				sys.exit()
				dp.close()
			
			try:
				dp.update(int(update))
				__in.extract(item, _out)
			
			except Exception, e:
				print str(e)

	except Exception, e:
		print str(e)
		return False
		
	return True	

	
def tvguidesetup():
		dialog = xbmcgui.Dialog().yesno('MediaHubIPTV','Would You like us to Setup the TV Guide for You?')
		if dialog:
			dialog = xbmcgui.Dialog().select('Select a TV Guide to Setup', ['iVue TV Guide','PVR TV Guide','Both'])
			if dialog==0:
				ivueint()
				xbmcgui.Dialog().ok('MediaHub IPTV', 'iVue Integration Complete')
			elif dialog==1:
				pvrsetup()
				xbmcgui.Dialog().ok('MediaHub IPTV', 'PVR Integration Complete')
			elif dialog==2:
				pvrsetup()
				ivueint()
				xbmcgui.Dialog().ok('MediaHub IPTV', 'PVR & iVue Integration Complete')

def num2day(num):
	if num =="0":
		day = 'monday'
	elif num=="1":
		day = 'tuesday'
	elif num=="2":
		day = 'wednesday'
	elif num=="3":
		day = 'thursday'
	elif num=="4":
		day = 'friday'
	elif num=="5":
		day = 'saturday'
	elif num=="6":
		day = 'sunday'
	return day
	
def extras():
	tools.addDir('Create a Short M3U & EPG URL','url',17,icon,fanart,'')
	tools.addDir('Integrate With TV Guide','tv',10,icon,fanart,'')
	tools.addDir('Run a Speed Test','ST',10,icon,fanart,'')
	tools.addDir('Football Guide','url',19,icon,fanart,'')
	tools.addDir('Clear Cache','CC',10,icon,fanart,'')
	
def get():
	url  = 'http://www.wheresthematch.com/live-football-on-tv/'
	open = tools.OPEN_URL(url)
	all_lists = tools.regex_get_all(open,'<td class="home-team">','</tr>')
	tools.addDir('[COLOR blue]Only Shows Main Matches - Find More at http://liveonsat.com[/COLOR]','url',500,icon,fanart,'')
	for a in all_lists:
		name = re.compile('<em class="">(.*?)<em class="">(.*?)</em>.*?<em class="">(.*?)</em>',re.DOTALL).findall(a)
		for home,v,away in name:
			koff  = tools.regex_from_to(a,'<strong>','</strong>')
			chan = tools.regex_from_to(a,'class="channel-name">','</span>')
			if chan == "Live Stream":
				chan = 'Not Televised'
			if chan == 'LFC TV':
				chan = 'LFCTV'
			thumb = tools.regex_from_to(a,'    <img src="','"')
			if 'Bet 365 Live' not in chan:
					tools.addDir(koff+' - '+str(home).replace('</em>','')+' '+v+'  '+away+'   -   [COLOR blue]%s[/COLOR]'%chan,'url',18,'http://www.wheresthematch.com'+str(thumb).replace('..',''),fanart,chan)

def footballguidesearch(description):
	if description=='BBC1 Scotland':
		tools.addDir('BBC1 Scotland','http://a.files.bbci.co.uk/media/live/manifesto/audio_video/simulcast/hls/uk/abr_hdtv/ak/bbc_one_scotland_hd.m3u8',4,icon,fanart,'')
	else:
		xbmc.log(str(description))
		open = tools.OPEN_URL(panel_api)
		all_chans = tools.regex_get_all(open,'{"num":','epg')
		for a in all_chans:
			name = tools.regex_from_to(a,'name":"','"').replace('\/','/')
			url  = tools.regex_from_to(a,'"stream_id":"','"')
			thumb= tools.regex_from_to(a,'stream_icon":"','"').replace('\/','/')
			chan = description.lower()
			if chan in name.lower():
				tools.addDir(name.replace('UK:','[COLOR blue]UK:[/COLOR]').replace('USA/CA:','[COLOR blue]USA/CA:[/COLOR]').replace('All','[COLOR blue]A[/COLOR]ll').replace('International','[COLOR blue]Int[/COLOR]ertaional').replace('Live:','[COLOR blue]Live:[/COLOR]').replace('TEST','[COLOR blue]TEST[/COLOR]').replace('Install','[COLOR blue]Install[/COLOR]').replace('24/7','[COLOR blue]24/7[/COLOR]').replace('INT:','[COLOR blue]INT:[/COLOR]').replace('DE:','[COLOR blue]DE:[/COLOR]').replace('FR:','[COLOR blue]FR:[/COLOR]').replace('PL:','[COLOR blue]PL:[/COLOR]').replace('AR:','[COLOR blue]AR:[/COLOR]').replace('LIVE:','[COLOR blue]LIVE:[/COLOR]').replace('ES:','[COLOR blue]ES:[/COLOR]').replace('IN:','[COLOR blue]IN:[/COLOR]').replace('PK:','[COLOR blue]PK:[/COLOR]'),play_url+url+'.ts',4,thumb,fanart,'')
			
			
def report(url):

	t       = str(time.time()).replace('.',',')
	t       = re.sub(',.+?$','',t)
	
	username     = xbmcaddon.Addon().getSetting('Username')
	if not'@' in username:
		username = username+'@noemail.com'
		
	url          = re.sub('-.*?$','',url)
	
	kb = xbmc.Keyboard ('', 'Please Explain The Issue You Are Having', False)
	kb.doModal()
	if (kb.isConfirmed()):
		problem = kb.getText()
		
		if problem =="":
			xbmcgui.Dialog().ok('MediaHub IPTV','You Must Tell Us The Problem You Are Having')
			return
	else:
		return
	
	
	xbmc.executebuiltin('ActivateWindow(busydialog)')
	
	
	report     = 'http://mediahubiptv.co.uk/report-a-channel'
	
	open       = tools.OPEN_URL(report)
	
	
	headers={'Host':'mediahubiptv.co.uk',
					'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
					'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
					'Accept-Language':'en-US,en;q=0.5',
					'Accept-Encoding':'gzip, deflate',
					'Referer':'http://mediahubiptv.co.uk/report-a-channel',
					'Content-Type':'application/x-www-form-urlencoded',
					'Content-Length':'304',
					'Connection':'keep-alive'}
					
	data={'ccf_field_name-9[first]':'MediaHubIPTV',
					'ccf_field_name-9[last]':'Addon',
					'ccf_field_email-10':username,
					'ccf_field_single-line-text-1':str(url).replace('[COLOR blue]','').replace('[/COLOR]',''),
					'ccf_field_paragraph-text-4':problem,
					'ccf_field_dropdown-3':'?',
					'form_id':'228',
					'form_page':'http://mediahubiptv.co.uk/report-a-channel',
					'my_information':'',
					'ccf_form':'1',
					'form_nonce':tools.regex_from_to(open,'form_nonce" value="','"')}
					
	query={'v':t}
	
	requests.post(report,params=query, data=data, headers=headers)
	
	xbmc.executebuiltin('Dialog.Close(busydialog)')
	
	xbmcgui.Dialog().ok('MediaHub IPTV','Thank You for Reporting %s The Reported Channel Will be Backup Soon'%url)
	
	return
	
def review():
	
	uname     = xbmcaddon.Addon().getSetting('Username')
	if not'@' in uname:
		uname = uname+'@noemail.com'

		
	kb = xbmc.Keyboard ('', 'Please Enter Your Name', False)
	kb.doModal()
	if (kb.isConfirmed()):
		name = kb.getText()
		
		if name =="":
			xbmcgui.Dialog().ok('MediaHub IPTV','Empty Field')
			return
	else:
		return
		
	kb = xbmc.Keyboard ('', 'Please Enter A Title For Your Review', False)
	kb.doModal()
	if (kb.isConfirmed()):
		rtitle = kb.getText()
		
		if rtitle =="":
			xbmcgui.Dialog().ok('MediaHub IPTV','Empty Field')
			return
	else:
		return
	
	kb = xbmc.Keyboard ('', 'Please Enter Your Review', False)
	kb.doModal()
	if (kb.isConfirmed()):
		review = kb.getText()
		
		if review =="":
			xbmcgui.Dialog().ok('MediaHub IPTV','Empty Field')
			return
	else:
		return
		
	d = xbmcgui.Dialog().select('Please Select a Star Rating',['5 Star','4 Star','3 Star','2 Star','1 Star'])
	
	if d==0:
		star = '5'
	elif d==1:
		star = '4'
	elif d==2:
		star = '3'
	elif d==3:
		star = '2'
	elif d==4:
		star = '1'
		
	
	
	
	xbmc.executebuiltin('ActivateWindow(busydialog)')
	
	
	report     = 'http://mediahubiptv.co.uk/wp-admin/admin-ajax.php?action=wpcr3-ajax'
	
	
	headers={'Host':'mediahubiptv.co.uk',
					'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
					'Accept':'application/json, text/javascript, */*; q=0.01',
					'Accept-Language':'en-US,en;q=0.5',
					'Accept-Encoding':'gzip, deflate',
					'Referer':'http://mediahubiptv.co.uk/reviews',
					'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
					'X-Requeted-With':'XMLHttpRequest',
					'Content-Length':'224',
					'Connection':'keep-alive'}
					
	data={'wpcr3_fname':name,
					'wpcr3_femail':uname,
					'wpcr3_fwebsite':'',
					'wpcr3_ftitle':rtitle,
					'wpcr3_frating':star,
					'wpcr3_ftext':review,
					'wpcr3_postid':'42',
					'website':'',
					'url':'',
					'wpcr3_fconfirm1':'0',
					'wpcr3_fconfirm2':'1',
					'wpcr3_fconfirm3':'1',
					'wpcr3_checkid':'42',
					'wpcr3_ajaxAct':'form'}

	
	requests.post(report, data=data, headers=headers)
	
	xbmc.executebuiltin('Dialog.Close(busydialog)')
	
	xbmcgui.Dialog().ok('MediaHub IPTV','Your Review Has been Submitted to mediahubiptv.co.uk','Thankyou For Your Time and Effort %s'%username)
	
	return

	

params=tools.get_params()
url=None
name=None
mode=None
iconimage=None
description=None
query=None
type=None

try:
	url=urllib.unquote_plus(params["url"])
except:
	pass
try:
	name=urllib.unquote_plus(params["name"])
except:
	pass
try:
	iconimage=urllib.unquote_plus(params["iconimage"])
except:
	pass
try:
	mode=int(params["mode"])
except:
	pass
try:
	description=urllib.unquote_plus(params["description"])
except:
	pass
try:
	query=urllib.unquote_plus(params["query"])
except:
	pass
try:
	type=urllib.unquote_plus(params["type"])
except:
	pass

if mode==None or url==None or len(url)<1:
	start()

elif mode==1:
	livecategory(url)
	
elif mode==2:
	Livelist(url)
	
elif mode==3:
	vod(url)
	
elif mode==4:
	stream_video(url)
	
elif mode==5:
	search()
	
elif mode==6:
	accountinfo()
	
elif mode==7:
	tvguide()
	
elif mode==8:
	settingsmenu()
	
elif mode==9:
	xbmc.executebuiltin('ActivateWindow(busydialog)')
	tools.Trailer().play(url) 
	xbmc.executebuiltin('Dialog.Close(busydialog)')
	
elif mode==10:
	addonsettings(url,description)
	
elif mode==11:
	pvrsetup()
	
elif mode==12:
	catchup()

elif mode==13:
	tvarchive(name,description)
	
elif mode==14:
	listcatchup2()
	
elif mode==15:
	ivueint()
	
elif mode==16:
	extras()
	
elif mode==17:
	shortlinks.showlinks()

elif mode==18:
	footballguidesearch(description)
	
elif mode==19:
	get()

elif mode==20:
	report(url)

elif mode==21:
	review()

xbmcplugin.endOfDirectory(int(sys.argv[1]))