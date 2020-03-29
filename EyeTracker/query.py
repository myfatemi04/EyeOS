import wolframalpha
import wikipedia
import requests
import os
import speech_recognition as sr

appId = 'APER4E-58XJGHAVAK'
client = wolframalpha.Client(appId)

def search_wiki(keyword=''):
  searchResults = wikipedia.search(keyword)
  if not searchResults:
    os.system("say No result from Wikipedia")
    return
  try:
    page = wikipedia.page(searchResults[0])
  except wikipedia.DisambiguationError, err:
    page = wikipedia.page(err.options[0])

  wikiTitle = str(page.title.encode('utf-8'))
  wikiSummary = str(page.summary.encode('utf-8'))
  print(wikiSummary)
  return wikiSummary


def search(text=''):
  res = client.query(text)
  if res['@success'] == 'false':
     return "Try again"
  else:
    result = ''
    pod0 = res['pod'][0]
    pod1 = res['pod'][1]
    if (('definition' in pod1['@title'].lower()) or ('result' in  pod1['@title'].lower()) or (pod1.get('@primary','false') == 'true')):
      result = resolveListOrDict(pod1['subpod'])
      result = result.replace('Wolfram|Alpha', 'Ingram')
      print(result)

      os.system('say "'+result+'"')
      question = resolveListOrDict(pod0['subpod'])
      question = removeBrackets(question)
      primaryImage(question)
    else:
      question = resolveListOrDict(pod0['subpod'])
      question = removeBrackets(question)
      search_wiki(question)
      primaryImage(question)
  print(result)
  return result

def removeBrackets(variable):
  return variable.split('(')[0]

def resolveListOrDict(variable):
  if isinstance(variable, list):
    return variable[0]['plaintext']
  else:
    return variable['plaintext']

def primaryImage(title=''):
    url = 'http://en.wikipedia.org/w/api.php'
    data = {'action':'query', 'prop':'pageimages','format':'json','piprop':'original','titles':title}
    try:
        res = requests.get(url, params=data)
        key = res.json()['query']['pages'].keys()[0]
        imageUrl = res.json()['query']['pages'][key]['original']['source']
        return imageUrl
    except Exception, err:
        print('')

def webQuery(q):
    r = sr.Recognizer()
    mic = sr.Microphone()
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source)
            print('listening...')
            audio = r.listen(source)
        q = r.recognize_google(audio)
    except:
        q = ' '
    q = q.lower()

    res = search(q)
    print(res)
    return res
