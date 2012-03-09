# Autosub Db.py - http://code.google.com/p/auto-sub/
#
# The Autosub DB module
# 

import os
import sqlite3
import logging
import autosub

# Settings
log = logging.getLogger('thelogger')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class idCache():
    def __init__(self):
        self.query_getId = 'select bierdopje_id from id_cache where show_name = ?'
        self.query_setId = 'insert into id_cache values (?,?)'
        self.query_flush = 'delete from id_cache'
        
    def getId(self, show_name):
        connection=sqlite3.connect(autosub.DBFILE)
        cursor=connection.cursor()
        cursor.execute(self.query_getId, [show_name.upper()])
        bierdopje_id = None
        
        for row in cursor:
            bierdopje_id = int(row[0])
        
        connection.close()
        return bierdopje_id
    
    def setId(self, bierdopje_id, show_name):
        connection=sqlite3.connect(autosub.DBFILE)
        cursor=connection.cursor()
        cursor.execute(self.query_setId,[bierdopje_id, show_name.upper()])
        connection.commit()
        connection.close()
    
    def flushCache(self):
        connection=sqlite3.connect(autosub.DBFILE)
        cursor=connection.cursor()
        cursor.execute(self.query_flush)
        connection.commit()
        connection.close()
            
class lastDown():
    def __init__(self):
        self.query_get = 'select * from last_downloads'
        self.query_set = 'insert into last_downloads values (NULL,?,?,?,?,?,?)'
        self.query_flush = 'delete from last_downloads'
        
    def getlastDown(self):
        connection=sqlite3.connect(autosub.DBFILE)
        connection.row_factory = dict_factory
        cursor=connection.cursor()
        cursor.execute(self.query_get)
        Llist = cursor.fetchall()
        connection.close()
        
        #return the last 10 items
        return Llist[len(Llist)-10:]

    def setlastDown (self, **data):
        connection=sqlite3.connect(autosub.DBFILE)
        cursor=connection.cursor()
        Ldict = data['dict']
        
        if not 'source' in Ldict.keys():
            Ldict['source'] = None
        
        cursor.execute(self.query_set,[ 
                       Ldict['title'],
                       Ldict['season'],
                       Ldict['episode'],
                       Ldict['quality'],
                       Ldict['source'],
                       Ldict['downlang']])
        connection.commit()
        connection.close()
    
    def flushLastdown(self):
        connection=sqlite3.connect(autosub.DBFILE)
        cursor=connection.cursor()
        cursor.execute(self.query_flush)
        connection.commit()
        connection.close()
        
def initDatabase():
    
    #check if file is already there, if not raise error
    dbFile = os.path.join(autosub.PATH, autosub.DBFILE)
    if os.path.exists(dbFile):
        return False
    
    #create the database
    try: 
        connection=sqlite3.connect(dbFile)
        cursor=connection.cursor()
        
        cursor.execute("CREATE TABLE id_cache (bierdopje_id INTEGER, show_name TEXT);")
        cursor.execute("CREATE TABLE last_downloads (id INTEGER PRIMARY KEY, show_name TEXT, season TEXT, episode TEXT, quality TEXT, source TEXT, language TEXT);")
            
        #create the tables 
        #cursor.execute("CREATE TABLE tv_shows (bierdopje_id INTEGER PRIMARY KEY, showLocationOnDisk TEXT, title TEXT, status TEXT);")
        #cursor.execute("CREATE TABLE tv_episodes (episode_id INTEGER PRIMARY KEY, show_bierdopje_id NUMERIC, title TEXT, season NUMERIC, episode NUMERIC, status NUMERIC, originalFileLocationOnDisk TEXT, quality TEXT, releasegrp TEXT, source TEXT);")
        #cursor.execute("CREATE TABLE status (lastRSScheck NUMERIC, lastScanDir NUMERIC, lastFullBierdopjeScan NUMERIC, lastDownload NUMERIC);")
        #cursor.execute("CREATE TABLE history (action NUMERIC, date NUMERIC, show_bierdopje_id NUMERIC, season NUMERIC, episode NUMERIC, downloadedFilename TEXT);")
        #cursor.execute("CREATE TABLE info (autoSubVersion NUMERIC, databaseVersion NUMERIC);")
        
        connection.commit()
        connection.close()
        
        log.debug("initDatabase: Succesfully created the sqlite database")
    except:
        log.error("initDatabase: Could not create database, please check if AutoSub has write access to write the following file %s" %dbFile)
    
    return True

def wipeDatabase():
    
    dbFile = os.path.join(os.getcwd(), "AutoSub.db")
    
    if not os.path.exists(dbFile):
        return False
    
    try: 
        connection=sqlite3.connect(dbFile)
        cursor=connection.cursor()
        
        cursor.execute("DELETE FROM tv_shows")
        cursor.execute("DELETE FROM tv_episodes")
        cursor.execute("DELETE FROM history")
        cursor.execute("DELETE FROM status")
        
        connection.commit()
        
        log.debug("wipeDatabase: Succesfully wiped database")
    except:
        log.error("wipeDatabase: Could not wipe database, please delete the file manually at %s" %dbFile)
        
    return True

def testDb():
    dbFile = os.path.join(os.getcwd(), "AutoSub.db")
    
    if not os.path.exists(dbFile):
        log.error("testDb: No database found, could not preform tests")
        return False
    noError = True
    
    connection=sqlite3.connect(dbFile) 
    cursor=connection.cursor()
    
    testShows = "SELECT * FROM tv_shows;"
    testEpisodes = "SELECT * FROM tv_episodes;"
    testStatus ="SELECT * FROM status;"
    testHistory = "SELECT * FROM history;"
    testInfo = "SELECT * FROM info;"

    response = None
    
    try:
        response = cursor.execute(testShows)
        log.debug("testDb: Database test of shows table succeeded, amount of rows: %s"  %len(response.fetchall()))
    except:
        noError = False
        log.error("testDb: Database test of shows table failed!!")
    
    try:
        response = cursor.execute(testEpisodes)
        log.debug("testDb: Database test of episodes table succeeded, amount of rows: %s"  %len(response.fetchall()))
    except:
        noError = False
        log.error("testDb: Database test of episodes table failed!!")    

    try:
        response = cursor.execute(testStatus)
        log.debug("testDb: Database test of status table succeeded, amount of rows: %s"  %len(response.fetchall()))
    except:
        noError = False
        log.error("Database test of status table failed!!")

    try:
        response = cursor.execute(testHistory)
        log.debug("testDb: Database test of history table succeeded, amount of rows: %s"  %len(response.fetchall()))
    except:
        noError = False
        log.error("testDb: Database test of history table failed!!")
        
    try:
        response = cursor.execute(testInfo)
        log.debug("testDb: Database test of info table succeeded, amount of rows: %s"  %len(response.fetchall()))
    except:
        noError = False
        log.error("testDb: Database test of info table failed!!")

    cursor.close()
    connection.close()

    if noError == True:
        log.debug("All database tests passed")
        return True
    else:
        return False