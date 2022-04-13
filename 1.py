#!/usr/bin/env python3
import os
import sys
DEBUG=1
if (len(sys.argv) >0):
        if (len(sys.argv) < 4):
            print ("ERROR, brak arguemntow wywolaj:  recover_pacs_by_file_list.py ROK MIESIAC DZIEN")
            exit()

        if (DEBUG): print (sys.argv[1])
