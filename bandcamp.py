import urllib
import urllib2
import re
import cookielib
from BeautifulSoup import BeautifulSoup

QUALITIES = ['flac', 'mp3-320', 'mp3-V0']

class Bandcamp():
    def __init__(self, url, quality='flac'):
        print url
        self.free_dl = False
        self.quality = quality
        req = urllib2.Request(url)
        resp = urllib2.urlopen(req)
        self.cookie_jar = cookielib.CookieJar()
        self.cookie_jar.extract_cookies(resp, req)
        self.doc = resp.read()
        self.soup = BeautifulSoup(self.doc)
        self.get_album()
        self.check_for_free_download()

    def get_album(self):
        for js in self.soup.findAll('script', type='text/javascript'):
            if 'var tralbumdata' in js.text.lower():
                self.album = js.text

    def check_for_free_download(self):
        alb_finder = re.compile(r'(?<=freeDownloadPage: ")[a-zA-Z:/.?=&0-9,%]+')
        match = re.search(alb_finder, self.album)
        if match:
            self.free_dl = match.group()
            self.get_free_dl()
        else:
            self.get_songs()

    def get_free_dl(self):
        fbd = FreeBandcampDownload(self)


class FreeBandcampDownload():
    def __init__(self, bandcamp):
        print bandcamp.free_dl
        req = urllib2.Request(bandcamp.free_dl)
        resp = urllib2.urlopen(req)
        self.cookie_jar = bandcamp.cookie_jar
        self.cookie_jar.extract_cookies(resp, req)
        print self.cookie_jar
        self.doc = resp.read()
        self.soup = BeautifulSoup(self.doc)
        self.quality = bandcamp.quality
        self.get_qualities()
        self.get_freebies()

    def get_qualities(self):
        for js in self.soup.findAll('script', type='text/javascript'):
            if 'var downloaddata' in js.text.lower():
                self.qualities = js.text


    def get_freebies(self):
        free_finder = re.compile(r'items: [\[\]a-zA-Z":\{\},. _\-0-9/?#%&\(\)=]+')
        match = re.search(free_finder, self.qualities)
        if not match:
            raise ValueError("Didn't find qualities. Blergenspiel!")
        match_dict = eval(match.group().lstrip('items: ').rstrip(',').replace(
            'true', 'True').replace('false', 'False'))
        print match_dict
        try:
            to_acquire = match_dict[0]['downloads'][self.quality]['url']
        except KeyError:
            print 'Key %s not found in %s' % (self.quality,
                                              match_dict[0]['downloads']
                                              .keys())
            for q in QUALITIES:
                try:
                    to_acquire = match_dict[0]['downloads'][q]['url']
                    break
                except KeyError:
                    continue
        self.freebie = to_acquire

        # f = open(r'c:\bc.zip', 'wb')
        # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        # f.write(opener.open(self.freebie).read())
        # f.close()

#for testing
bc = Bandcamp('http://datathrash.bandcamp.com/album/cosmic-hash-chronicles')