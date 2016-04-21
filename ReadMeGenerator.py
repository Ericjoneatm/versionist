import urllib2 
import os
from bs4 import BeautifulSoup

class Pair:
  title = None
  dependency = None

  def __init__(self, title, dependency):
    self.title = title
    self.dependency = dependency

  def __str__(self):
    return self.title + '   ' + self.dependency

def write(text):
  file.write(text)

def addHeader(header):
  file.write("\n\n")
  file.write("# " + header + "\n")

def addItem(title, compileType,  dependency):
  file.write("```groovy\n// " + title + "\n")
  file.write(compileType + " '" + dependency + "'\n```\n")

def addList(compileType, list):
  file.write("```groovy\n")
  for pair in list:
    file.write('// ' + pair.title + "\n")
    file.write(compileType + " '" + pair.dependency + "'\n\n")
  file.write("```\n")

def getSoup(url):
  return BeautifulSoup(urllib2.urlopen(url).read().decode('utf-8'), 'html.parser')

def generatePlatform(url):
  tags = getSoup(url).table
  for a in tags.find_all('a'):
    path = a['href']
    a['href'] = 'http://developer.android.com' + a['href']

  write(str(tags))

def addEspresso(url):
  title = None
  list =[]
  for tag in getSoup(url).find_all('span', ["c1","s1"]):
    if tag['class'][0] == 'c1':
      title = tag
    if tag['class'][0] == 's1':
      list.append(Pair(title.string[3:], tag.string[1:-1]))
  addList('androidTestCompile', list)

def addAndroidStudio(url):
  soup = getSoup(url)
  androidStudio = None
  emulator = None
  for tag in soup.find_all('title'):
    title= tag.string
    if "Android Studio" in title:
      if androidStudio == None:
        androidStudio = title
    if "Emulator" in title:
      if emulator == None:
        index = title.find("Emulator")
        emulator = title[index:]

    if androidStudio != None and emulator != None:
      write(androidStudio + "\n\n" + emulator)
      return

def addGooglePlayService(url):
  soup = getSoup(url)
  tags = soup.find_all(['td'])
  list = []
  iterator = iter(tags);
  # while (iterator.next() != None)
  try:
    while True:
      pair = Pair(iterator.next().string, iterator.next().string)
      list.append(pair)
  except Exception, e:
    pass
  addList('compile', list)

def generateSupportLibraries(url):
  soup = getSoup(url)
  tags = soup.find_all(['h2','h3','pre'])

  list = []
  title = None
  for tag in tags:
    if tag.name == 'h2' or tag.name == 'h3':
      title = tag.string
    if tag.name == 'pre' and "renderscript" not in tag.string:
      pair = Pair(title, str(tag.string).encode('string_escape')[2:-2])
      list.append(pair)

  addList('compile', list)

def addMavenRepo(title, groupId, artifactId):
  url = 'https://maven-badges.herokuapp.com/maven-central/' + groupId+'/' + artifactId
  res = urllib2.urlopen(url)
  finalurl = res.geturl()

  list = finalurl.split('%7C')
  dependency= list[1] + ":" + list[2] + ":" + list[3]
  return Pair(title, dependency)

with open('README.md', 'w+') as file:
  addHeader("Android Platform")
  generatePlatform('http://developer.android.com/guide/topics/manifest/uses-sdk-element.html')

  addHeader("Android Studio")
  addAndroidStudio('https://sites.google.com/a/android.com/tools/recent/posts.xml')

  addHeader("Google Play Services")
  addGooglePlayService('https://developers.google.com/android/guides/setup')

  addHeader("Support Library")
  generateSupportLibraries('http://developer.android.com/tools/support-library/features.html')

  addHeader("Test")
  addEspresso('https://google.github.io/android-testing-support-library/downloads/index.html')

  testList = []
  testList.append(addMavenRepo('JUnit','junit', 'junit'))
  testList.append(addMavenRepo('Mockito','org.mockito', 'mockito-core'))
  testList.append(addMavenRepo('AssertJ','org.assertj', 'assertj-core'))
  testList.append(addMavenRepo('Robolectric','org.robolectric', 'robolectric'))
  testList.append(addMavenRepo('Robolectric Shadows Support v4','org.robolectric', 'shadows-support-v4'))
  testList.append(addMavenRepo('Robolectric Shadows Play Services','org.robolectric', 'shadows-play-services'))
  testList.append(addMavenRepo('MockServer','com.squareup.okhttp3', 'mockwebserver'))
  addList('testCompile', testList)

  addHeader("Others")
  others = []
  others.append(addMavenRepo('Gson','com.google.code.gson', 'gson'))
  others.append(addMavenRepo('OkHttp3','com.squareup.okhttp3', 'okhttp'))
  others.append(addMavenRepo('OkHttp3 Logging Interceptor','com.squareup.okhttp3', 'logging-interceptor'))
  others.append(addMavenRepo('RxJava','io.reactivex', 'rxjava'))
  others.append(addMavenRepo('RxAndroid','io.reactivex', 'rxandroid'))
  others.append(addMavenRepo('Dagger 2','com.google.dagger', 'dagger'))
  addList('compile', others)

with open('README.md') as file:
  print file.read()