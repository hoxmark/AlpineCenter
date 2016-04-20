import sqlite3
from flask import g
from app import app
import math
import datetime

DATABASE = 'alpin.db'
app.config.from_object(__name__)


def connect_db():
    """Kobler til databasen."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


# lager databasen
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# Apner forbindelsen til databasen
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


# lukker forbindelsen til databasen
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


class dbManager:
    def __init__(self):
        init_db()

    def getUtleiePakkeFromDb(self, pakkenummer):
        print("getting pakkenummer from DB")
        db = get_db()
        cur = db.execute('select * from utleiepakker WHERE id = ' + pakkenummer)
        entries = cur.fetchone()
        utleiePakke = UtleiePakke(entries[0], entries[1], entries[2], entries[3], entries[4], entries[5], entries[6],
                                  entries[7])
        print ('hentet ut: ' + utleiePakke.name)
        return utleiePakke

    def getUtleiePakkeneFromDb(self):
        utleiePakkene = []
        db = get_db()
        cur = db.execute('SELECT * FROM utleiepakker')
        entries = cur.fetchall()
        for row in entries:
            utleiePakkene.append(UtleiePakke(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        print ('Innlegget ble sendt og lagret i databasen')
        print("get utleiepakkene")
        return utleiePakkene

    def getMember(self, id):
        db = get_db()
        cur = db.execute('select * from members WHERE id =' + str(id))
        entries = cur.fetchone()
        member = Member(entries[0], entries[1], entries[2])
        return member

    def getKvitteringHeiskort(self, id):
        kvitteringHeiskort = []
        db = get_db()
        cur = db.execute('select * from kvitteringHeiskort WHERE owner=' + str(id))
        entries = cur.fetchall()
        for row in entries:
            kvitteringHeiskort.append(KvitteringHeiskort(row[0], row[1], row[2], row[3]))
        return kvitteringHeiskort

    def getReceiptUtleiepakker(self, id):
        receiptUtleiepakker = []
        db = get_db()
        cur = db.execute('select * from receiptUtleiepakker WHERE owner=' + str(id))
        entries = cur.fetchall()
        for row in entries:
            receiptUtleiepakker.append(ReceiptUtleiepakker(row[0], row[1], row[2], row[3], row[4], row[5]))
        return receiptUtleiepakker




    def registerNewMember(self, member):
        print(member.name)
        print(member.email)
        print(member.password)


class UtleiePakke:
    id = -1
    name = ''
    beskrivelse = 'canine'
    ski = 'canine'
    shoes = 'canine'
    skiPoles = 'canine'
    price = 10
    childPrice = 5;
    antLedige = 0;

    def __init__(self, id, name, beskrivelse, ski, shoes, skiPoles, price, antLedige):
        self.name = name
        self.id = id
        self.beskrivelse = beskrivelse
        self.ski
        self.shoes = shoes
        self.skiPoles = skiPoles
        self.price = math.ceil(price)
        self.antLedige = antLedige
        self.childPrice = math.ceil(price / 2);


class Member:
    id = -1
    name = ''
    email = ''
    password = ''


    def __init__(self, id, name, email, password):
        self.name = name
        self.id = id
        self.email = email
        self.password = password

    def __init__(self, name, email, password):
        self.name = name
        self.id = -2
        self.email = email
        self.password = password

class Heiskort:
    id = -1
    categori = 'canine'  # class variable shared by all instances
    price = 10  # class variable shared by all instances

    def __init__(self, id, categori, price):
        self.categori = categori
        self.id = id
        self.price = price


class KvitteringHeiskort:
    id = -1
    owner = ''
    startTime = 'time'
    endTime = 'time'
    heiskort = object;
    outdated = True;

    # datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    def __init__(self, id, owner, startTime, heiskort):
        self.id = "L" + str(id)  # Adding an L to the receiptID so it will be unique
        self.owner = owner
        self.startTime = startTime
        self.heiskort = heiskort

        # now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        startTimeObj = datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')

        if (heiskort == 0):
            self.endTime = startTimeObj + datetime.timedelta(days=1)
            if (self.endTime > datetime.datetime.now()):
                self.outdated = False;

        if (heiskort == 1):
            self.endTime = startTimeObj + datetime.timedelta(days=7)
            if (self.endTime > datetime.datetime.now()):
                self.outdated = False;

        if (heiskort == 2):
            self.endTime = startTimeObj + datetime.timedelta(days=60)
            if (self.endTime > datetime.datetime.now()):
                self.outdated = False;


class ReceiptUtleiepakker:
    id = -1
    owner = ''
    startTime = 'time'
    utleiepakker = '';
    type = -1;
    typeMutiplier = -1;
    outdated = True;

    def __init__(self, id, owner, startTime, type, typeMutiplier, utleiepakker):
        self.id = "R" + str(id)  # Adding an R to the receiptID so it will be unique
        self.owner = owner
        self.startTime = startTime
        self.utleiepakker = self.nameOfUtleiepakke(utleiepakker);

        startTimeObj = datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')

        # type 0 = hourly
        if (type == 0):
            self.endTime = startTimeObj + datetime.timedelta(hours=typeMutiplier)
            if (self.endTime > datetime.datetime.now()):
                self.outdated = False;

        # type 1 = daily
        if (type == 1):
            self.endTime = startTimeObj + datetime.timedelta(days=typeMutiplier)
            if (self.endTime > datetime.datetime.now()):
                self.outdated = False;

        # type2 = weekly
        if (type == 2):
            self.endTime = startTimeObj + datetime.timedelta(days=(7 * typeMutiplier))
            if (self.endTime > datetime.datetime.now()):
                self.outdated = False;

    # Just to save some time.
    def nameOfUtleiepakke(self, nummer):
        if nummer == 1:
            return 'Langrenn Pakka'
        elif nummer == 2:
            return 'Alpin Pakka'
        elif nummer == 3:
            return 'Telemark Pakka'
        elif nummer == 4:
            return 'Twintip Pakka'
        elif nummer == 5:
            return 'Super Pakka'
        else:
            return 'ulistet'


dbM = dbManager();