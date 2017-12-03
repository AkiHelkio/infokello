#! -*- coding:utf8 -*-


from sense_hat import SenseHat
from datetime import datetime
from random import randint
import xml.etree.cElementTree as et
import requests
import json
import sys
import os


class Hakija:
    def __init__(self, FMIapiKey, sijainti):
        self.FMIapiKey = FMIapiKey
        self.sijainti = sijainti
        self.hakuajastus = 3660   # 1h 1min välein haku
        self.timeformat = "%Y-%m-%dT%H:%M:%SZ"
        self.lampotilat = {}
        self.tuuli = {}
    def viimeisinLampotila(self):
        uusinlampo = sorted([datetime.strptime(x,self.timeformat) for x in self.lampotilat.keys()])[-1]
        viimeisinArvo = self.lampotilat[datetime.strftime(uusinlampo, self.timeformat)]
        return viimeisinArvo+"C"
    def viimeisinTuuli(self):
        uusintuuli = sorted([datetime.strptime(x,self.timeformat) for x in self.tuuli.keys()])[-1]
        viimeisinArvo = self.lampotilat[datetime.strftime(uusintuuli, self.timeformat)]
        return viimeisinArvo+"m/s"
    def nayta(self):
        # palautetaan rimpsu uusimmasta säädatasta
        kello = datetime.now().strftime("  %H:%M")
        lampotila = "  "+self.viimeisinLampotila()
        tuuli = "  "+self.viimeisinTuuli()
        return kello+lampotila+tuuli
    def paivitettava(self):
        target = 'data.xml'
        haettava = False
        try:
            # jos tiedostoa ei ole, haetaan. Jos se on, verrataan aikaa:
            if os.path.exists(target):
                # haetaan tiedoston viimeksi muokattu aika:
                muokkausaika = datetime.fromtimestamp(os.lstat(target).st_mtime)
                # lasketaan erotus nykyhetkestä
                viimeksihaettu = datetime.now() - muokkausaika
                # jos sekuntit ovat suuremmat kuin ajastus, haetaan uusi aineisto.
                if viimeksihaettu.seconds > self.hakuajastus:
                    print("Haetaan uusi aineisto "+datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S"))
                    haettava = True
                else:
                    print("Ei haeta uutta")
                    print("Uusi aineisto haetaan "+str(int((self.hakuajastus - viimeksihaettu.seconds)/60))+"min päästä")
            else:
                print("Haetaan uusi aineisto "+datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S"))
                haettava = True
            return haettava
        except Exception as e:
            sys.exit(e.args)

    # hakee FMiltä tiedot ja tallentaa data.xml filuksi.
    def hae_kelidata(self):
        query = "http://data.fmi.fi/fmi-apikey/"+self.FMIapiKey+"/wfs?request=getFeature&storedquery_id=fmi::observations::weather::timevaluepair&place="+self.sijainti+"&timestep=30"
        r = requests.get(query)
        if r.status_code != 200:
            print(r.status)
        # onnistuessaan, tallennetaan data tiedostoon
        else:
            with open('data.xml','w') as f:
                for rivi in r.text:
                    f.write(rivi)
    # sisäänluku data.xml filusta
    def lue_kelidata(self):
        print("luetaan dataa")
        with open('data.xml','r') as f:
            data = f.readlines()
        tree = et.fromstring("".join(data))
        # luodaan dictionary lämpötiloille
        self.lampotilat = {}
        self.tuuli = {}
        for x in tree.iter():
            if x.tag == '{http://www.opengis.net/waterml/2.0}MeasurementTimeseries':
                #{'{http://www.opengis.net/gml/3.2}id': 'obs-obs-1-1-t2m'}
                id = x.attrib.get('{http://www.opengis.net/gml/3.2}id')
                # print(id)
                if id == 'obs-obs-1-1-t2m':
                    for t in x.iter():
                        if t.tag == '{http://www.opengis.net/waterml/2.0}MeasurementTVP':
                            self.lampotilat[t[0].text] = t[1].text
                            # print(t[1].tag, t[1].text)
                elif id == 'obs-obs-1-1-ws_10min':
                    for t in x.iter():
                        if t.tag == '{http://www.opengis.net/waterml/2.0}MeasurementTVP':
                            self.tuuli[t[0].text] = t[1].text

def main():
    # alustukset
    sense = SenseHat()
    sense.clear()
    # koitetaan hakea viite conffiin. Defaulttina 'config.json'
    try:
        conffile = sys.argv[1]
    except IndexError:
        conffile = 'config.json'
    try:
        # Luetaan conffit. Api avain ja sääpaikka oltava tiedostossa.
        with open(conffile,'r') as f:
            conf = json.load(f)
    except Exception as e:
        sys.exit(e.args)
    try:
        # Luodaan uusi hakija käyttäen conffia:
        hakija = Hakija(conf['FMIapiKey'],conf['Location'])
        # Toistetaan ikuisesti
        while True:
            # satunnainen tekstin väritys
            vari = (randint(0,255),randint(0,255),randint(0,255))
            # tekstin nopeus
            nopeus = 0.1
            # Tarkistetaan tarviiko uusi kelitieto hakea fmi:ltä
            if hakija.paivitettava():
                hakija.hae_kelidata()
            # Luetaan datafilu
            hakija.lue_kelidata()
            # pyydetään uusin teksti tila hakijalta:
            teksti = hakija.nayta()
            # lisätään vielä sisäilman paine mittaus:
            teksti += "  {}".format(int(sense.get_pressure()))
            teksti += "hPa"
            print("teksti : "+ teksti)
            # näyetään ledeillä
            sense.show_message(teksti, nopeus, text_colour=vari)
        sense.clear()
    except KeyboardInterrupt:
        sense.clear()


if __name__ == '__main__':
    main()

