import HTMLParser
import urllib2
import re
import codecs
import zipfile
import os
import urllib
import shutil
hPrs = HTMLParser.HTMLParser()

#выясняем количество сезонов в сериале
def seasons_search(url0):
    req = urllib2.Request(url0, headers={'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0"}) 
    page = urllib2.urlopen(req).read()
    page = page.decode(u'latin-1').replace(u'\n', u'').replace(u'\r', u'')
    page = hPrs.unescape(page)
    m = re.search(u'<h2>.+</h2>[ ]*<p class="description"><a href="tvshow-[0-9]+-([0-9]+).html">', page, flags=re.U)
    if m != None:
        return m.group(1)
    else:
        return 1
   
#поиск русских субтитров в сезоне сериала. Сбор рус, (англ)?, (ит)?, (нем)? субтитров
def links_search(url):
    final_links = set()
    arr_lang = [u'en', 'ru', 'de', 'it']
    req = urllib2.Request(url, headers={'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0"}) 
    page = urllib2.urlopen(req).read()
    page = page.decode(u'latin-1').replace(u'\n', u'').replace(u'\r', u'#')
    frame = u'http://www.tvsubtitles.net/'
    page = hPrs.unescape(page)
    arr = page.split(u'#')
    for line in arr:
        if u'html"><img src="images/flags/ru.gif"' in line:
            for lang in arr_lang:
                subtitle = re.search(u'<a href="([a-z]+-[0-9]+(-[a-z][a-z])?.html)"><img src="images/flags/' + lang + u'.gif"', line, flags=re.U)
                #subtitle = re.search(u'<a href="([a-z0-9-]+.html)"><img src="images/flags/' + lang + u'.gif"', line, flags=re.U)
                if subtitle != None:
                    final_links.add(frame + subtitle.group(1))
    return final_links

count = 1
#скачивание субтитров по ссылке
def subtitles_download(link):
    global count
    if link.endswith(u'en.html') or link.endswith(u'ru.html') or link.endswith(u'it.html') or link.endswith(u'de.html'):
        req = urllib2.Request(link, headers={'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0"}) 
        page = urllib2.urlopen(req).read()
        page = page.decode(u'latin-1').replace(u'\n', u'').replace(u'\r', u'')
        page = hPrs.unescape(page)
        m = re.search(u'<a href="(/subtitle-[0-9]+.html)">', page, flags=re.U)
        if m != None:
           link_pre = u'http://www.tvsubtitles.net' + m.group(1)
           link_down = link_pre.replace(u'/subtitle-', u'/download-')
    else:
        link_down = link.replace(u'/subtitle-', u'/download-')
    print link_down
    urllib.urlretrieve(link_down, str(count) + u'.zip')
    count += 1       
    return

#распаковка архивов, удаление исходных файлов-архивов
def zip_archive():
    filelist = os.listdir(u'.')
    for fname in filelist:
        if fname.endswith(u'.zip'):
            try:
                z = zipfile.ZipFile(fname, 'r')
                for name in z.namelist():
                    new_name = name.replace(u'  ', u' ')
                    dirname = new_name.split(u' - ')[0]
                    if not os.path.exists(dirname):
                        os.makedirs(dirname)
                    z.extract(name, u'./' + dirname)
            except UnicodeDecodeError:
                if not os.path.exists(u'bugs'):
                    os.makedirs(u'bugs')
                shutil.copy(fname, u'./bugs')
            finally:
                z.close()
                os.remove(fname)
    return

#главная функция. запуск остальных ф-ций
def main():
    tvshow = 231
    while tvshow <= 1677:
        seasons = 1
        seas = seasons_search(u'http://www.tvsubtitles.net/tvshow-' + str(tvshow) + u'-1.html')
        print seas
        while seasons <= int(seas):
            need_link = u'http://www.tvsubtitles.net/tvshow-' + str(tvshow) + u'-' + str(seasons) + u'.html'
            print need_link
            sub_arrlinks = links_search(need_link)
            for element in sub_arrlinks:
                print element
                almost_result = subtitles_download(element)
                result = zip_archive()
            seasons += 1
        tvshow += 1
    return

if __name__ == '__main__':
    main()
