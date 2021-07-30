#####################################################
#### Written By: SATYAKI DE                      ####
#### Written On: 26-Jul-2021                     ####
####                                             ####
#### Objective: This script is a config          ####
#### file, contains all the keys for             ####
#### for Prophet API. Application will           ####
#### process these information & perform         ####
#### the call to our newly developed with        ####
#### APIs developed by Facebook & a open-source  ####
#### project called "About-Corona".              ####
#####################################################

import os
import platform as pl

class clsConfig(object):
    Curr_Path = os.path.dirname(os.path.realpath(__file__))

    os_det = pl.system()
    if os_det == "Windows":
        sep = '\\'
    else:
        sep = '/'

    conf = {
        'APP_ID': 1,
        "URL":"https://corona-api.com/countries/",
        "appType":"application/json",
        "conType":"keep-alive",
        "limRec": 10,
        "CACHE":"no-cache",
        "coList": "DE, IN, US, CA, GB, ID, BR",
        "LOG_PATH":Curr_Path + sep + 'log' + sep,
        "MAX_RETRY": 3,
        "FNC": "NewConfirmed",
        "TMS": "ReportedDate",
        "FND": "NewDeaths"
    }
