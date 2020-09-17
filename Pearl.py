from gtts import gTTS
import speech_recognition as sr
import time
import re
import webbrowser
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import smtplib
import requests
from pygame import mixer
import urllib.request
import urllib.parse
import bs4
import datetime
import os
from bs4 import BeautifulSoup as soup
import sys
from pyowm import OWM
from newsapi import NewsApiClient
import subprocess
import json

def talk(audio):
    "speaks audio passed as argument"

    print(audio)
    for line in audio.splitlines():
        text_to_speech = gTTS(text=audio, lang='en-uk')
        text_to_speech.save('audio.mp3')
        mixer.init()
        mixer.music.load("audio.mp3")
        mixer.music.play()


def myCommand():
    "listens for commands"
    #Initialize the recognizer
    #The primary purpose of a Recognizer instance is, of course, to recognize speech. 
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('PEARL is Ready...')
        r.pause_threshold = 1
        #wait for a second to let the recognizer adjust the  
        #energy threshold based on the surrounding noise level 
        r.adjust_for_ambient_noise(source, duration=1)
        #listens for the user's input
        audio = r.listen(source)
        print('analyzing...')

    try:
        command = r.recognize_google(audio).lower()
        print('You said: ' + command + '\n')
        time.sleep(2)

    #loop back to continue to listen for commands if unrecognizable speech is received
    except sr.UnknownValueError:
        print('Your last command couldn\'t be heard')
        command = myCommand()

    return command


def pearl(command):
    errors=[
        "I don't know what you mean",
        "Excuse me?",
        "Can you repeat it please?",
    ]
    "if statements for executing commands"

    if 'help me' in command:
        talk("""
        You can use these commands and I'll help you out:
        1. Search anything on google
        2. Send email to your friend
        3. Tells you about anything from Wikipedia
        4. Current weather in {cityname} : Tells you the current condition and temperature
        5. Greetings
        6. play me a video : Plays song in youtube
        7. change wallpaper : Change desktop wallpaper
        8. news of today : reads top news of today
        9. time : Current system time
        10. top stories from google news (RSS feeds)
        11. Play Music from Local directory
        12. Shuts Down on command
        13. Opens any website you want on your voice command
        14. Tells you some lame jokes
        15. Tells you about Myself
        """)
    # Search on Google
    elif 'open google and search' in command:
        reg_ex = re.search('open google and search (.*)', command)
        search_for = command.split("search",1)[1] 
        talk("Searching for ",command)
        url = 'https://www.google.com/'
        if reg_ex:
            subgoogle = reg_ex.group(1)
            url = url + 'r/' + subgoogle
        talk('Okay!')
        driver = webdriver.Firefox(executable_path='Yor Path here')
        driver.get('http://www.google.com')
        search = driver.find_element_by_name('q')
        search.send_keys(str(search_for))
        search.send_keys(Keys.RETURN) # hit return after you enter search text

    #Send Email
    elif 'email' in command:
        talk('What is the subject?')
        time.sleep(3)
        subject = myCommand()
        talk('What should I say?')
        message = myCommand()
        content = 'Subject: {}\n\n{}'.format(subject, message)

        #init gmail SMTP
        mail = smtplib.SMTP('smtp.gmail.com', 587)

        #identify to server
        mail.ehlo()

        #encrypt session
        mail.starttls()

        #login
        mail.login('senders email', 'senders pass')

        #send message
        mail.sendmail('from', 'to', content)

        #end mail connection
        mail.close()

        talk('Email sent.')

    # search in wikipedia (e.g. Can you search in wikipedia apples)
    elif 'wikipedia' in command:
        reg_ex = re.search('wikipedia (.+)', command)
        if reg_ex: 
            query = command.split("wikipedia",1)[1] 
            response = requests.get("https://en.wikipedia.org/wiki/" + query)
            if response is not None:
                html = bs4.BeautifulSoup(response.text, 'html.parser')
                title = html.select("#firstHeading")[0].text
                paragraphs = html.select("p")
                for para in paragraphs:
                    print (para.text)
                intro = '\n'.join([ para.text for para in paragraphs[0:3]])
                print (intro)
                mp3name = 'speech.mp3'
                language = 'en'
                myobj = gTTS(text=intro, lang=language, slow=False)   
                myobj.save(mp3name)
                mixer.init()
                mixer.music.load("speech.mp3")
                mixer.music.play()

    elif 'stop' in command:
        mixer.music.stop()

    # Search videos on Youtube and play (e.g. Search in youtube believer)
    elif 'youtube' in command:
        talk('Ok!')
        reg_ex = re.search('youtube (.+)', command)
        if reg_ex:
            domain = command.split("youtube",1)[1] 
            query_string = urllib.parse.urlencode({"search_query" : domain})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
            webbrowser.open("http://www.youtube.com/watch?v={}".format(search_results[0]))
            pass

    #play music
    elif 'play music' in command:
        music_dir= 'Your Path here'
        songs=os.listdir(music_dir)   
        mixer.init()
        mixer.music.load(os.path.join(music_dir, songs[0]))
        mixer.music.play()

    #open website
    elif 'open' in command:
        reg_ex = re.search('open (.+)', command)
        if reg_ex:
            domain = reg_ex.group(1)
            print(domain)
            url = 'https://www.' + domain
            webbrowser.open(url)
            talk('The website you have requested has been opened for you')
        else:
            pass

    #joke
    elif 'joke' in command:
        res = requests.get('https://icanhazdadjoke.com/',headers={"Accept":"application/json"})
        if res.status_code == requests.codes.ok:
            talk(str(res.json()['joke']))
        else:
            talk('oops!I ran out of jokes')

    #top headlines 
    elif 'news of today' in command:
        talk('Todays top Headlines are :' )
        newsapi = NewsApiClient(api_key='Your Key Here')
        top_headlines = newsapi.get_top_headlines(q='Covid-19',language='en',)
        for article in top_headlines['articles']:
            print('Title : ')
            talk(article['title'])
            print('Description : ',article['description'],'\n\n')

    #top stories from google news
    elif 'news for today' in command:
        try:
            news_url="https://news.google.com/news/rss"
            Client=urllib.request.urlopen(news_url)
            xml_page=Client.read()
            Client.close()
            soup_page=soup(xml_page,"xml")
            news_list=soup_page.findAll("item")
            for news in news_list[:15]:
                talk(news.title.text.encode('utf-8'))
        except Exception as e:
            print(e)

    #current weather
    elif 'current weather' in command:
        reg_ex = re.search('current weather in (.*)', command)
        if reg_ex:
            city = reg_ex.group(1)
            owm = OWM(api_key='Yoyr Key here')
            obs = owm.weather_at_place(city)
            w = obs.get_weather()
            k = w.get_status()
            x = w.get_temperature(unit='celsius')
            talk('Current weather in %s is %s. The maximum temperature is %0.2f and the minimum temperature is %0.2f degree celcius' % (city, k, x['temp_max'], x['temp_min']))

    elif 'change wallpaper' in command:
        folder = 'Your Path here'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
        api_key = 'Your Key Here'
        url = 'https://api.unsplash.com/photos/random?client_id=' + api_key #pic from unspalsh.com
        f = urllib.request.urlopen(url)
        json_string = f.read()
        f.close()
        parsed_json = json.loads(json_string)
        photo = parsed_json['urls']['full']
        urllib.request.urlretrieve(photo, "Your Path here") # Location where we download the image to.
        subprocess.call(["killall Dock"], shell=True)
        talk('wallpaper changed successfully')

    elif 'hello' in command:
        hour = int(datetime.datetime.now().hour)            # select time (hour)
        
    # conditions for morning, afternoon, evening
        if hour>=0 and hour<12:
            talk('Good Morning')

        elif hour>=12 and hour<=16:
            talk('Good Afternoon')
        else:
            talk('Good Evening')
        # after wishing
        talk('How may I help you?')
        time.sleep(3)

    elif 'time' in command:
        hour = int(datetime.datetime.now().hour)            # select time (hour)
        minute = datetime.datetime.now().time().minute      # select time (minutes)
        talk(f'Time is {hour}:{minute}')

    elif 'who are you' in command:
        talk('I am Pearl - A Virtual Voice Assistant')
        time.sleep(3)

    elif 'thank you' in command:
        talk('My Pleasure')

    elif 'shutdown' in command:
        talk('Bye bye ! Have a nice day')
        sys.exit()
            
    else:
        error = random.choice(errors)
        talk(error)
        time.sleep(3)


talk('Pearl activated!')

#loop to continue executing multiple commands
while True:
    time.sleep(4)
    pearl(myCommand())
