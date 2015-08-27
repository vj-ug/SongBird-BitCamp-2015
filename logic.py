from __future__ import division

from pyechonest import config
from pyechonest import song
import os, csv, json, operator, twitter
from metamind.api import set_api_key, ClassificationModel

set_api_key("uqakkdVZiUUr62KISE5pM4GKiAZNaHXXT9B1umpPhIxlOiWZWQ")

config.ECHO_NEST_API_KEY = "DLBFUV54VPZIDBJO7"

def categorize_tweets_csv():
    for tweetsfile in os.listdir(os.getcwd()):
        excitements = []
        happy = 0
        exclamations = 0
        counter_num = 0
        if tweetsfile.endswith(".csv"):
            print tweetsfile
            with open(tweetsfile, 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                for tweet, sentiment, accuracy in csvreader:
                    counter_num += 1
                    if sentiment == "positive" and accuracy >= 50:
                        happy += 1
                    if tweet.count("!") > 1 and tweet.count(".") <= 1:
                       exclamations += 1

            exclamation_percentage = exclamations / float(counter_num)
            # excitement = (sum(excitements) + exclamations) / float(len(excitements))
            happy /= float(counter_num)
            if exclamation_percentage > .15:
                if happy > .4:
                    mood = "happy"
                else:
                    mood = "angry"
            else:
                if happy > .4:
                    mood = "relaxed"
                else:
                    mood = "sad"
            rkp_results = song.search(mood=mood, min_energy=exclamation_percentage, artist_min_familiarity=.6, style="pop", artist_start_year_after="1999")
            resultant_song = rkp_results[0]
            print resultant_song.title + " - " + resultant_song.artist_name + " happy " + str(happy) + " excite " + str(exclamation_percentage)

def pick_song(predict_list):
    mood_counts = {"sad": 0.0, "excited": 0.0, "happy": 0.0, "motivated": 0.0, "angry": 0.0, "energetic": 0.0}
    for input in predict_list["content"]["statuses"]:
        class_result = ClassificationModel(id=25073).predict(input["text"], input_type="text")
        jsonres = json.loads(json.dumps(class_result[0]))
        mood = jsonres['label'].lower()
        mood_counts[mood] += 1.0

    moods = max(mood_counts.iteritems(), key=operator.itemgetter(1))
    total = sum(mood_counts.values())
    proportion = {key: (mood_counts[key]/float(total)) for key in mood_counts.keys()}
    sad = {"max_danceability": .3, "max_tempo": 110.0, "min_acousticness": .3, "min_speechiness": .3}
    excited = {"min_danceability": .3, "min_tempo": 100.0, "min_energy": .5, "max_acousticness": .4}
    happy = {"max_danceability": .5, "max_energy": .6}
    motivated= {"min_danceability": .4, "min_energy": .5, "max_acousticness": .4, "max_speechiness": .5, "min_tempo":100.0}
    angry = {"min_energy": .5, "max_acousticness": .3}
    energetic = {"min_energy": .65, "min_tempo": 110.0, "max_acousticness": .5, "max_speechiness": .6}
    sad = {key: (sad[key] * proportion["sad"]) for key in sad.iterkeys()}
    sad["proportion"] = proportion["sad"]
    excited = {key: (excited[key] * proportion["excited"]) for key in excited.iterkeys()}
    excited["proportion"] = proportion["excited"]
    happy = {key: (happy[key] * proportion["happy"]) for key in happy.iterkeys()}
    happy["proportion"] = proportion["happy"]
    motivated = {key: (motivated[key] * proportion["motivated"]) for key in motivated.iterkeys()}
    motivated["proportion"] = proportion["motivated"]
    angry = {key: (angry[key] * proportion["angry"]) for key in angry.iterkeys()}
    angry["proportion"] = proportion["angry"]
    energetic = {key: (energetic[key] * proportion["energetic"]) for key in energetic.iterkeys()}
    energetic["proportion"] = proportion["energetic"]
    stuff = [sad, excited, happy, motivated, angry, energetic]
    newlist = sorted(stuff, key=operator.itemgetter("proportion"))
    result = newlist[5]

    songs_results = song.search(artist_min_familiarity=.6, style="pop", artist_start_year_after="1999", max_tempo=result.get("max_tempo", 160),
                                min_tempo=result.get("min_tempo", 0), max_danceability=result.get("max_danceability", 1),
                                min_danceability=result.get("min_danceability", 0), max_speechiness=result.get("max_speechiness", 1),
                                min_speechiness=result.get("min_speechiness", 0), max_energy=result.get("max_energy", 1),
                                min_energy=result.get("min_energy", 0), max_acousticness=result.get("max_acousticness", 1),
                                min_acousticness=result.get("min_acousticness", 0))

    oursong = songs_results[0] # is a slammin screen door, stayin out late, sneakin out your window
    print oursong.title + " - " + oursong.artist_name
    return oursong


