# -*- coding: utf-8 -*-

# Deleting this file cripples the entire addon

#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
# http://kodi.wiki/view/How-to:Write_Python_Scripts
################################################

import sys,os,json
import xbmc, xbmcgui, xbmcaddon, xbmcplugin,re
import shutil
import xbmcvfs
import urllib
import time
import datetime

addon         = 'script.ivueguide'
ADDONID       = addon
addon_name    = addon
addonPath     = xbmc.translatePath(os.path.join('special://home/addons', addon))
basePath      = xbmc.translatePath(os.path.join('special://profile', 'addon_data', addon))
tmp_File      = os.path.join(basePath, 'tmp.ini')
icon          = xbmc.translatePath(os.path.join('special://home/addons', addon, 'icon.png'))
dialog        = xbmcgui.Dialog();dp = xbmcgui.DialogProgress()

inipath       = xbmc.translatePath(os.path.join(basePath, 'resources', 'ini', 'plugin.video.FlawlessTv'))
m3upath       = xbmc.translatePath(os.path.join(basePath, 'resources', 'm3u', 'plugin.video.FlawlessTv'))
FLAW           = 'plugin.video.FlawlessTv'


if not os.path.exists(basePath):
    os.makedirs(basePath)
            
if not os.path.exists(os.path.join(basePath, 'resources')):
    os.makedirs(os.path.join(basePath, 'resources'))
def notify(header,msg,icon_path):
    duration=2000
    xbmcgui.Dialog().notification(header, msg, icon=icon_path, time=duration, sound=False)
def validTime(setting, maxAge):
    previousTime = getPreviousTime(setting)
    now          = datetime.datetime.today()
    delta        = now - previousTime
    nSeconds     = (delta.days * 86400) + delta.seconds
    return nSeconds <= maxAge     
def SetSetting(param, value):
    value = str(value)
    if GetSetting(param) == value:
        return
    xbmcaddon.Addon(addon).setSetting(param, value)
def DialogOK(line1, line2='', line3=''):
    d = xbmcgui.Dialog()
    d.ok('Subscriptions', line1, line2 , line3)     
def log(text):
    try:
        output = '%s V%s : %s' % ("Log", 'Error?', str(text))
        if DEBUG:
            xbmc.log(output)
        else:
            xbmc.log(output, xbmc.LOGDEBUG)
    except: pass

def StartCreate():
  
    if os.path.exists(basePath + '/playlist.m3u'):
        os.remove(basePath + '/playlist.m3u')


    if os.path.exists(inipath):
        shutil.rmtree(inipath) 
    if not os.path.exists(inipath):
        os.makedirs(inipath)
              
    if not os.path.exists(m3upath):
        os.makedirs(m3upath)
        
     

    add_pvr()
    add_FLAWini()

    return


def add_FLAWini():
    TheseAddons   =  [FLAW]
    for FoundAddon in TheseAddons:
        if CheckHasThisAddon(FoundAddon):
            notify('generating channels',FoundAddon,os.path.join('special://home/addons', FoundAddon, 'icon.png'))##NOTIFY##
            ParseFLAWData(FoundAddon)
def CheckHasThisAddon(FoundAddon):
    if xbmc.getCondVisibility('System.HasAddon(%s)' % FoundAddon) == 1:
        settingsFileCheck = xbmc.translatePath(os.path.join('special://home/userdata/addon_data',FoundAddon,'settings.xml'))
        if os.path.exists(settingsFileCheck):
            return True
    else:
        return False
#
	
def ParseFLAWData(FoundAddon):
    AddonININame = FoundAddon  + '.ini'   
    Addoninipath  = os.path.join(inipath, AddonININame)
    response = GrabSettingsFromFLAW(FoundAddon)
    result   = response['result'] 
    ChannelsResult = result['files']    
    ExtrasFileToWrite  = file(Addoninipath, 'w')  
    ExtrasFileToWrite.write('[')
    ExtrasFileToWrite.write(FoundAddon)
    ExtrasFileToWrite.write(']')
    ExtrasFileToWrite.write('\n')   
    TheAddonURL = []   
    for channel in ChannelsResult:
        ParsedChannels = channel['label']
        stream  = channel['file']
        ChannelURL  = GetFLAWStuff(FoundAddon, ParsedChannels)
        channel = RemoveFLAWChanCrap(FoundAddon, ChannelURL)
        FinalChannelString = channel + '\t\t=' + stream#Jules: make correct formating for channel names
        TheAddonURL.append(FinalChannelString)
        TheAddonURL.sort()
    for item in TheAddonURL:
      ExtrasFileToWrite.write("%s\n" % item)
    ExtrasFileToWrite.close()
    Clean_Names_FLAW(Addoninipath,tmp_File)
#
def GrabSettingsFromFLAW(FoundAddon):
    Addon    =  xbmcaddon.Addon(FoundAddon)
    username =  Addon.getSetting('Username')
    password =  Addon.getSetting('Password')
    BeginningOfPluginString   = 'plugin://' + FoundAddon    
    urlBody     = '/?action=stream_video&extra&page&plot&thumbnail=&title=All&url='
    endOfString    =  GetFLAWVariables(FoundAddon)
    startOfString  =  BeginningOfPluginString + urlBody + endOfString
    GrabThisUrl = 'username=' + username + '&password=' + password + '&type=get_live_streams&cat_id=0'
    queryURL = BeginningOfPluginString  + '/?action=security_check&extra&page&plot&thumbnail&title=Live%20TV&url'
    query = startOfString +  urllib.quote_plus(GrabThisUrl)
    checkthisurl = ('{"jsonrpc":"2.0", "method":"Files.GetDirectory", "params":{"directory":"%s"}, "id": 1}' % queryURL)
    checkthisurltoo = ('{"jsonrpc":"2.0", "method":"Files.GetDirectory", "params":{"directory":"%s"}, "id": 1}' % query)   
    try:
        xbmc.executeJSONRPC(checkthisurl)
        response = xbmc.executeJSONRPC(checkthisurltoo)
        content = json.loads(response.decode('utf-8', 'ignore'))
        return content
    except Exception as e:
        #RunSetSetting(e)
        print e
        return {'Error' : 'Plugin Error'}
#    
def GetFLAWStuff(FoundAddon, RemoveURLGarbage):
    RemoveURLGarbage = RemoveURLGarbage.replace('COLOR+', '').replace(' [/B]', '').replace('[COLOR steelblue]', '').replace('[/COLOR]', '').replace('[COLOR firebrick]', '').replace('COLOR+steelblue', '')      
    return RemoveURLGarbage
#    
def RemoveFLAWChanCrap(FoundAddon, FoundChannels):
    channel = FoundChannels.rsplit('[/B]', 1)[0].split('[B]', 1)[-1]        
    return channel
#       
def GetFLAWVariables(FoundAddon):
    Addon    =  xbmcaddon.Addon(FoundAddon) 
    addre_ss =  'http://flawless-iptv.net' 
    po_rt =  '4545'
    correct_address = addre_ss + ':' + po_rt + '/enigma2.php?'
    return correct_address
	

def add_pvr():
    iniFle = 'pvr.ini';writestyle = 'w'
    iniPvrAddonName = 'script.ivueguide'
    #iniPvrAddonName = 'pvr.iptvsimple'
    #
    PVRACTIVE   = (xbmc.getCondVisibility('Pvr.HasTVChannels')) or (xbmc.getCondVisibility('Pvr.HasRadioChannels')) == True    
    if not PVRACTIVE:
        return       
    pvrinipath  = os.path.join(inipath, iniFle)
    notify('PVR',iniFle,os.path.join(addonPath, 'resources', 'png', 'pvr.png'))##NOTIFY##
    
    try:
        tryTvChannels  = _getPVRChannels('"tv"')
        tryTvChannelsCommand = tryTvChannels['result']          
    except: pass   
    
    try:
        tryRadio  = _getPVRChannels('"radio"')
        tryRadioCommand = tryRadio['result']
    except: pass
    
    try:
        foundTvChannels  = tryTvChannelsCommand['channels']      
        foundRadioChannels  = tryRadioCommand['channels']
    except: pass    
    ThePVRini  = file(pvrinipath, writestyle)    
    ThePVRini.write('['+iniPvrAddonName+']\n')       
    try:
        for TryToFindStreams in foundTvChannels:
            WhatsTheGroupID  = TryToFindStreams['label']  
            stream = ('%s') % TryToFindStreams['channelid']
            ThePVRini.write('%s' % WhatsTheGroupID)
            ThePVRini.write("=")
            ThePVRini.write(('%s') % stream)            
            ThePVRini.write("\n")
    except: pass    
    try:
        for TryToFindStreams in foundRadioChannels:          
            WhatsTheGroupID  = TryToFindStreams['label']  
            stream = ('%s') % TryToFindStreams['channelid']
            ThePVRini.write('%s' % WhatsTheGroupID)
            ThePVRini.write("=")
            ThePVRini.write('%s' % stream)            
            ThePVRini.write("\n")
    except: pass   
    ThePVRini.write("\n")
    ThePVRini.close()

def _getPVRChannels(group):   
    method   = 'PVR.GetChannels'
    params   = 'channelgroupid'
    WhatAreGroupIDs  =  getGroupID(group)
    checkPVR =  sendJSONpvr(method, params, WhatAreGroupIDs)   
    return checkPVR
#
def getGroupID(group):
    method   = 'PVR.GetChannelGroups'
    params   = 'channeltype'   
    checkPVR = sendJSONpvr(method, params, group)
    result   = checkPVR['result']
    groups   = result['channelgroups']
    #
    for group in groups:
        WhatsTheGroupID = group['label']
        if WhatsTheGroupID == 'All channels':
            return group['channelgroupid']
#
def sendJSONpvr(method, params, value):
    JSONPVR  = ('{"jsonrpc":"2.0","method":"%s","params":{"%s":%s}, "id":"1"}' % (method, params, value))    
    checkPVR = xbmc.executeJSONRPC(JSONPVR)
    return json.loads(checkPVR.decode("utf-8"),"ignore")
# PVR End #
def Clean_Names_FLAW(Clean_Name,tmpFile):
    if os.path.exists(tmpFile):
        os.remove(tmpFile)
    os.rename(Clean_Name, tmpFile)
    s=open(tmpFile).read()

    s=s.replace('UK: AMC SD','AMC UK SD')
    s=s.replace('USA/CA: VH1','VH1 USA')
    s=s.replace('USA/CA: E! ENTERTAINMENT SD','E! ENTERTAINMENT USA SD')
    s=s.replace('USA/CA: DISCOVERY CHANNEL','DISCOVERY US')
    s=s.replace('USA/CA: NAT GEO WILD HD','NAT GEO WILD USA HD')
    s=s.replace('USA/CA: NATIONAL GEOGRAPHIC HD','NATIONAL GEOGRAPHIC CHANNEL USA HD')
    s=s.replace('USA/CA: ANIMAL PLANET HD','ANIMAL PLANET US HD')
    s=s.replace('USA/CA: INVESTIGATION DISCOVERY HD','ID US HD')
    s=s.replace('USA/CA: DISNEY CHANNEL HD','DISNEY CHANNEL USA HD')
    s=s.replace('USA/CA: NICKELODEON HD','NICKELODEON US HD')
    s=s.replace('USA/CA: NICK JR HD','NICK JR USA HD')
    s=s.replace('USA/CA: NICKTOONS HD','NICKTOONS USA HD')
    s=s.replace('USA/CA: CARTOON NETWORK HD','CARTOON NETWORK USA HD')
    s=s.replace('USA/CA: FOX HD','FOX USTV')
    s=s.replace('USA/CA: LIFETIME HD','LIFETIME USA HD')
    s=s.replace('USA/CA: SYFY HD','SYFY USA HD')
    s=s.replace('USA/CA: COMEDY CENTRAL HD','COMEDY CENTRAL US HD')
    s=s.replace('USA/CA: NICK JR HD','NICKJR US HD')
    s=s.replace('USA/CA: CI NETWORK HD','CI US')
    s=s.replace('UK: SYFY','SYFY UK')
    s=s.replace('SKY ARTS SD','SKY ARTS 1 SD')
    s=s.replace('TLC HD','TLC USA HD')
    s=s.replace('COMEDY CENTRAL EXTRA','COMEDY CENTRAL XTRA')
    s=s.replace('GOOD FOOD SD','GOOD FOOD UK SD')
    s=s.replace('(HD)NFL: ','NFL ')
    s=s.replace('(HD)NFLFOX: ','NFL ')
    s=s.replace(' # ','')
    s=s.replace(' - ','')
    s=s.replace(' - .','')
    s=s.replace('(HD)NFLN Redzone: 		','NFL ')
    s=s.replace('(HD)NFLN: ','NFL')
    s=s.replace('(HD)NFLNBC:','NFL NBC')
    s=s.replace('CA: ','')
    s=s.replace('[COLOR Normal \e[1mBold]','')
    s=s.replace('CA: ','')
    s=s.replace('USA: ','')
    s=s.replace('ML:','ML')
    s=s.replace('NL: ','')
    s=s.replace('XXX: ','')	
    s=s.replace('SkySports','Sky Sports')		
    s=s.replace('UK:  ','')
    s=s.replace('UK: ','')
    s=s.replace('BBC 1','BBC ONE')
    s=s.replace('BBC 2','BBC TWO')
    s=s.replace('ITV SD','ITV1 SD')
    s=s.replace('ITV HD','ITV1 HD')
    s=s.replace('Uk: ','')
    s=s.replace('SKY CINEMA HITS','SKY CINEMA SHOWCASE')
    s=s.replace('SKY CINEMA CRIME & THRILLER','SKY CINEMA THRILLER')
    s=s.replace('SKY CINEMA SCI FI & HORROR','SKY CINEMA SCI-FI AND HORROR')
    s=s.replace('SKY ONE','Sky1')
    s=s.replace('SKY TWO','Sky2')
    s=s.replace('[COLOR white]','')	
    s=s.replace('USA/','')
    s=s.replace('PL: ','Polish ')
    s=s.replace('INT: ','')
    s=s.replace('FR: ','French ')
    s=s.replace('ES: ','Spanish ')
    s=s.replace('DE: ','German ')
    s=s.replace('AR: ','Arabic ')
    s=s.replace('MIO SPORTS 102','MIO 102 SPORTS')
    s=s.replace('MIO SPORTS 103','MIO 103 SPORTS')
    s=s.replace('MIO SPORTS 104','MIO 104 SPORTS')
    s=s.replace('MIO SPORTS 105','MIO 105 SPORTS')
    s=s.replace('MIO SPORTS 106','MIO 106 SPORTS')
    s=s.replace('MIO SPORTS 107','MIO 107 SPORTS')
    s=s.replace('BEIN HD','BEIN-SPORTS')
    s=s.replace('UNIVERSAL HD','UNIVERSAL CHANNEL HD')
    s=s.replace('UNIVERSAL SD','UNIVERSAL CHANNEL SD')
    s=s.replace('HALLMARK HD','HALLMARK CHANNEL HD')
    s=s.replace('NATIONAL GEOGRAPHIC SD','NATIONAL GEOGRAPHIC CHANNEL SD')
    s=s.replace('NATIONAL GEOGRAPHIC HD','NATIONAL GEOGRAPHIC CHANNEL HD')
    s=s.replace('DISCOVERY HOME & HEALTH SD','DISCOVERY HOME AND HEALTH SD')
    s=s.replace('SKY SPORTS 1 HD BACKUP','SKY SPORTS 1 BACKUP HD')
    s=s.replace('SKY SPORTS 2 HD BACKUP','SKY SPORTS 2 BACKUP HD')
    s=s.replace('SKY SPORTS 3 HD BACKUP','SKY SPORTS 3 BACKUP HD')
    s=s.replace('SKY SPORTS 4 HD BACKUP','SKY SPORTS 4 BACKUP HD')
    s=s.replace('SKY SPORTS 5 HD BACKUP','SKY SPORTS 5 BACKUP HD')
    s=s.replace('SKY SPORTS F1 HD BACK UP','SKY SPORTS F1 BACKUP HD')
    s=s.replace('SKY SPORTS NEWS HQ','SKY SPTS NEWS')
    s=s.replace('SKY SPTS NEWS HD','SKY SPORTS NEWS HD')
    s=s.replace('SKY SPTS NEWS HDS','SKY SPORTS NEWS HDS')
    s=s.replace('BT SPORT 1 HD 2','BT SPORT 1 BACKUP HD')
    s=s.replace('BT SPORT 2 HD 2','BT SPORT 2 BACKUP HD')
    s=s.replace('BT SPORT 3 HD 2','BT SPORT 3 BACKUP HD')
    s=s.replace('EUROSPORT 1','BRITISH EUROSPORT')
    s=s.replace('NBC EXTRA TIME','NotUsedNBCEXTRATIME')
    s=s.replace('BOXNATION','BOX NATION')
    s=s.replace('LIVE NHL','NHL Center Ice')
    s=s.replace('LIVE NBA','NBA LEAGUE PASS')
    s=s.replace('LIVE NFL','NFL SUNDAY TICKET')
    s=s.replace('PAC12','PAC-12')
    s=s.replace('PAC 12','PAC-12')
    s=s.replace('BEIN-SPORTS 1','BEIN-SPORTS-1HD')
    s=s.replace('BEIN-SPORTS 2','BEIN-SPORTS-2HD')
    s=s.replace('BEIN-SPORTS 3','BEIN-SPORTS-3HD')
    s=s.replace('BEIN-SPORTS 4','BEIN-SPORTS-4HD')
    s=s.replace('BEIN-SPORTS 5','BEIN-SPORTS-5HD')
    s=s.replace('BEIN-SPORTS 6','BEIN-SPORTS-6HD')
    s=s.replace('BEIN-SPORTS 7','BEIN-SPORTS-7HD')
    s=s.replace('BEIN-SPORTS 8','BEIN-SPORTS-8HD')
    s=s.replace('BEIN-SPORTS 9','BEIN-SPORTS-9HD')
    s=s.replace('BEIN-SPORTS 10','BEIN-SPORTS-10HD')
    s=s.replace('BEIN-SPORTS 11','BEIN-SPORTS-11HD')
    s=s.replace('BEIN-SPORTS 12','BEIN-SPORTS-12HD')
    s=s.replace('ASTRO SPORTS HD 1','ASTRO SUPERSPORT 1 HD')
    s=s.replace('ASTRO SPORTS HD 2','ASTRO SUPERSPORT 2 HD')
    s=s.replace('ASTRO SPORTS HD 3','ASTRO SUPERSPORT 3 HD')
    s=s.replace('ASTRO SPORTS HD 4','ASTRO SUPERSPORT 4 HD')
    s=s.replace('SETANTA IRELAND','EIR SPORTS 1')
    s=s.replace('SETANTA SPORTS 1','EIR SPORTS 2')
    s=s.replace('HISTORY HD','HISTORY US HD')
    s=s.replace('DISCOVERY SCIENCE SD','DISCOVERY SCIENCE UK SD')
    s=s.replace('DISCOVERY SCIENCE HD','DISCOVERY SCIENCE USA HD')
    s=s.replace('DISCOVERY CRIME AND INVESTIGATION','CI')
    s=s.replace('ID SD','ID SD UK')
    s=s.replace('CI SD','CI SD UK')
    s=s.replace('JR. TOO','NICK JR TOO UK')
    s=s.replace('THE CW','CW')
    s=s.replace('SPIKE HD','SPIKE US HD')
    s=s.replace('A&E TV HD','A AND E HD')
    s=s.replace('STARZ EDGE HD','STARZ EDGEEAST HD')
    s=s.replace('CINEMAX MOREMAX HD','MOREMAX HD')
    s=s.replace('CINEMAX HD','CINEMAX EAST HD')
    s=s.replace('NICKELODEON USA HD','NICKELODEONEAST HD')
    s=s.replace('CNN HD','CNN HD USA')
    s=s.replace('CTV HD','CTV CANADA HD')
    s=s.replace('TENNIS CHANNEL','THE TENNIS CHANNEL')
    s=s.replace('BEIN USA','BEIN SPORTS')
    s=s.replace('TV3 SD','TV3 IRISH SD')
    s=s.replace('DRAMA SD','DRAMA UK SD')
    s=s.replace('AMC HD','AMC US')
    s=s.replace('TRU TV HD','TRUTV US HD')
    s=s.replace('.m3u8','.ts')

    f=open(Clean_Name,'a')
    f.write(s)
    f.close()
    os.remove(tmpFile)
    return

def Clean_Names(Clean_Name,tmpFile):
    if os.path.exists(tmpFile):
        os.remove(tmpFile)
    os.rename(Clean_Name, tmpFile)
    s=open(tmpFile).read()
    s=s.replace('','') 
    f=open(Clean_Name,'a')
    f.write(s)
    f.close()
    os.remove(tmpFile)
    return

if __name__ == '__main__':
    if StartCreate():
        StartCreate()
        print 'Subscriptions1'
    else:
        print 'Subscriptions2'
xbmc.executebuiltin("Dialog.Close(busydialog)")
choice = xbmcgui.Dialog().yesno('[COLOR white]iVue Integrated[/COLOR]','[COLOR white]iVue is now integrated[/COLOR]', ' ', '[COLOR white]Would you like to launch iVue now?[/COLOR]', nolabel='[COLOR white]No, not right now[/COLOR]',yeslabel='[COLOR white]Yes, open iVue[/COLOR]')
if choice == 0:
    quit
elif choice == 1:
    xbmc.executebuiltin('RunAddon(script.ivueguide)')