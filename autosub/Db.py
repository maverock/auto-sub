# Autosub Db.py - http://code.google.com/p/auto-sub/
#
# The Autosub DB module
# 

import os
import sqlite3
import logging


# debug purposes, remove when fully integrated
import AutoSub
AutoSub.initLogging('test.log')

# Settings
log = logging.getLogger('thelogger')

def initDatabase():
    
    #check if file is already there, if not raise error
    dbFile = os.path.join(os.getcwd(), "AutoSub.db")
    if os.path.exists(dbFile):
        return False
    
    #create the database
    try: 
        connection=sqlite3.connect(dbFile)
        cursor=connection.cursor()
            
        #create the tables 
        cursor.execute("CREATE TABLE tv_shows (bierdopje_id INTEGER PRIMARY KEY, showLocationOnDisk TEXT, title TEXT, status TEXT);")
        cursor.execute("CREATE TABLE tv_episodes (episode_id INTEGER PRIMARY KEY, show_bierdopje_id NUMERIC, title TEXT, season NUMERIC, episode NUMERIC, status NUMERIC, originalFileLocationOnDisk TEXT, quality TEXT, releasegrp TEXT, source TEXT);")
        cursor.execute("CREATE TABLE status (lastRSScheck NUMERIC, lastScanDir NUMERIC, lastFullBierdopjeScan NUMERIC, lastDownload NUMERIC);")
        cursor.execute("CREATE TABLE history (action NUMERIC, date NUMERIC, show_bierdopje_id NUMERIC, season NUMERIC, episode NUMERIC, downloadedFilename TEXT);")
        cursor.execute("CREATE TABLE info (autoSubVersion NUMERIC, databaseVersion NUMERIC);")
        
        connection.commit()
        
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