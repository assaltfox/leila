#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import re
import psycopg2
#Wyamagane do uruchomienia programu 
#Skopiowanie /etc/bacula z placówki 
#Tabele w bazie
#create table l_jobs(pk serial primary key, JobID text, count_pliki int, count_bajty int,volume text, status varchar (8));
#create table l_volumes(pk serial primary key,TapeID text, volname text, status varchar (8));
#alter table l_volumes OWNER TO bacula;
#alter table l_jobs OWNER TO bacula;

DEBUG=1
logdir  = "/var/log/leila"
logfile = "/var/log/leila/leila_lto.log"
mtxcmd  = "/usr/sbin/mtx"
changer = "/dev/sg2"
loaded  = ""
kasetki = []
dbname="bacula"
dbuser="bacula"
dbpass="haselko,pixel"
host="localhost"
conn=""
cursor=""



def file_writer(title,writeit):
    f = open(logfile, "a+")
    t = time.ctime()
    logMe0 = str(writeit)
    sidx = (str(t) + " " + title + logMe0 + "\n")
    f.write(sidx)
    f.close()

def init_log():
    subprocess.call(['mkdir','-p',logdir])
    file_writer("title", "Utworzono katalog logow")

def psql_connect():
        try:
            global conn
            conn = psycopg2.connect(dbname=dbname, user=dbuser, host=host, password=dbpass)
        except:
            print ("Can't connected to DB:",dbname)

def pg_dodaj(volname,status):
    cursor = conn.cursor()
    cursor.execute("INSERT into l_volumes(volname,status) values (%s,%s)", [volname, status])
    conn.commit()
 

def list_tapes():
    if DEBUG:print ("mtx cmd",mtxcmd,'-f',changer,'status')
    exec_handl=subprocess.Popen([mtxcmd,'-f',changer,'status'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    out=exec_handl.stdout.readlines()
    for line in out:
            line=line.decode('utf-8').strip()
            if (re.search("Data Transfer Element 0",line)):    
                (element1,loaded)=re.split('VolumeTag =',line)
                if DEBUG:print("zaladowana ",loaded)
            elif (re.search("Storage Element",line)):
                if (re.search("Full",line)):
                    (kasetki)=re.split(':VolumeTag=',line)
                    pg_dodaj(kasetki[1],"NEW")
                    if DEBUG:print (kasetki[1])

def bscan():
# przed mtx unload musimy wykonac mt -f /dev/st0 unlock
# mtx unload demontujemy AKTUALNA KASETE zawsze
# mtx load ktora chcemy
# bscan -s -m -v -V 000004L5 LTO-st >&000004L5-bsca.log
# bscan > logi z prefixem kasety
# update na bazie na status scanned
# przechodzimy do kolejnej kasety
# jesli bconsole zwraca "If this is not a blank tape, try unmounting and remounting"
# kaseta powinan miec status BLANK
    if DEBUG:print ("mtx cmd",mtxcmd,'-f',changer,'status')
    exec_handl=subprocess.Popen([bscan,'-f',changer,'status'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    out=exec_handl.stdout.readlines()
    for line in out:
            line=line.decode('utf-8').strip()
            if (re.search("Data Transfer Element 0",line)):    
                (element1,loaded)=re.split('VolumeTag =',line)
                if DEBUG:print("zaladowana ",loaded)
            elif (re.search("Storage Element",line)):
                if (re.search("Full",line)):
                    (kasetki)=re.split(':VolumeTag=',line)
                    pg_dodaj(kasetki[1],"NEW")
                    if DEBUG:print (kasetki[1])
                                    

def recover_lto():
    print("uruchomiony recover")

def main():
   if (len(sys.argv) >0):
        if (len(sys.argv) < 2):
            print ("ERROR, brak arguemntow wywolaj:  leila_lto.py tryb_pracy (initialise,scan,recover)")
            exit()      
        if (sys.argv[1] == "initialise"):
            list_tapes()
            if DEBUG:print("initialise mode selected")
        if (sys.argv[1] == "scan"):
            bscan()
            if DEBUG:print("scan mode selected")
        if (sys.argv[1] == "recover"):
            recover_lto()
            if DEBUG:print("recover mode selected")


        if (DEBUG): print ("Argumenty uruchomienia",sys.argv)

    

psql_connect()
main()
