import os
import csv

def loadGTutors():
    musics = []
    tutors = []

    currDir = os.path.dirname(os.path.abspath(__file__))
    tutorFilePath = os.path.join(currDir, "tutors.csv")
    if os.path.exists(tutorFilePath):
        with open(tutorFilePath, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for tutor in csv_reader:
                tutor["order"] = int(tutor["order"])
                tutor["paragraph"] = int(tutor["paragraph"]) 
                musics.append(tutor)
        if len(musics) >  0:
            musics.sort(key=lambda x: (x["order"], x["paragraph"]))
            tutors = list(filter(lambda x: x['paragraph'] == 0, musics))


    return tutors, musics

GTutors, GMusics = loadGTutors()