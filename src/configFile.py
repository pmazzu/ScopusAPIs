# -*- coding: utf-8 -*-
"""
Created on Mon Jul 06 11:30:18 2015

@author: Pablo Mazzucchi
"""
import ConfigParser
import time
import os

# borrar el archivo de configuracion actual si existe
configPath='C:\ScopusAPIs\config\config.cfg'

configRateLimitsPath='C:\ScopusAPIs\config\limits.cfg'

 ##############################################################################################
# Description: 
# Input: 
# Output: 
############################################################################################## 

def packingConfigVariables():

    configParser=ConfigParser.RawConfigParser()

    if os.path.isfile(configPath):
    	#os.remove(configPath)
    	configParser.read(configPath)

    	tecAffiliations = configParser.get('VARIABLES','tecAffiliations')
    	affiliationID=configParser.get('VARIABLES','affiliationID')
    	yearFromStr=configParser.get('VARIABLES','yearFromStr')
    	yearToStr=configParser.get('VARIABLES','yearToStr')
    	frameSizeStr=configParser.get('VARIABLES','frameSizeStr')

    	configParser.remove_section('API_KEY')
    	configParser.remove_section('FILES')
    	configParser.remove_section('VARIABLES')
    else:
    	affiliationID='60007966'
    	tecAffiliations='60007966;60018640'
        yearFromStr='2009'
        yearToStr='2015'
        frameSizeStr='200'
    
    timeStampStr = time.strftime("%Y%m%d-%H%M%S")  

    configParser.add_section('API_KEY')

    configParser.set('API_KEY', 'MY_API_KEY', 'INSERT YOUR API KEY HERE')
    
    configParser.add_section('FILES')
    configParser.set('FILES', 'outputPath', 'C:\ScopusAPIs\output\/afiliacionTec_'+timeStampStr+'.txt')
    configParser.set('FILES', 'inputPath', 'C:\ScopusAPIs\input\input.txt')
    configParser.set('FILES', 'notProcessed', 'C:\ScopusAPIs\logs\/notProcessed_'+timeStampStr+'.txt')
    configParser.set('FILES', 'collab', 'C:\ScopusAPIs\output\/afiliacionNOTec_'+timeStampStr+'.txt')
    configParser.set('FILES', 'summary', 'C:\ScopusAPIs\output\summary_'+timeStampStr+'.txt')
    configParser.set('FILES', 'debugFilePath', 'C:\ScopusAPIs\logs\debugFile_'+timeStampStr+'.txt')
    configParser.set('FILES', 'logFile', 'C:\ScopusAPIs\logs\logFile_'+timeStampStr+'.txt')

    configParser.add_section('VARIABLES')
    configParser.set('VARIABLES', 'affiliationID', affiliationID)
    configParser.set('VARIABLES', 'tecAffiliations', tecAffiliations)
    configParser.set('VARIABLES', 'frameSizeStr', frameSizeStr)
    configParser.set('VARIABLES', 'yearFromStr', yearFromStr)
    configParser.set('VARIABLES', 'yearToStr', yearToStr)

    with open(configPath, 'wb') as configFile:
    	configParser.write(configFile)

    return


 ##############################################################################################
# Description: 
# Input: 
# Output: 
############################################################################################## 

def initlializeAPIsRateLimits():

	# Limit Rates:
	# http://dev.elsevier.com/api_key_settings.html
	# Scopus Search         - Enabled - 20000
	# Affiliation Search    - Enabled - 5000
	# Author Search         - Enabled - 5000
	# Abstract Retrieval    - Enabled - 10000
	# Author Retrieval      - Enabled - 5000
	# Affiliation Retrieval - Enabled - 5000

	if os.path.isfile(configRateLimitsPath):
		os.remove(configRateLimitsPath)

	config=ConfigParser.RawConfigParser()
	
	configParser=ConfigParser.RawConfigParser()

	if os.path.isfile(configPath):
		configParser.read(configPath)
		apiKey = configParser.get('API_KEY','MY_API_KEY')

		config.add_section(apiKey)
		config.set(apiKey,'scopusSearchMax',20000)
		config.set(apiKey,'scopusSearchUsed',0)
		config.set(apiKey,'SSlastTimeUsed','9999-99-99')
		config.set(apiKey,'affilSearchMax',5000)
		config.set(apiKey,'affilSearchUsed',0)
		config.set(apiKey,'AfilSlastTimeUsed','9999-99-99')
		config.set(apiKey,'authorSearchMax',5000)
		config.set(apiKey,'authorSearchUsed',0)
		config.set(apiKey,'AuthSlastTimeUsed','9999-99-99')
		config.set(apiKey,'absRetrievalMax',10000)
		config.set(apiKey,'absRetrievalUsed',0)
		config.set(apiKey,'AbsRlastTimeUsed','9999-99-99')
		config.set(apiKey,'authorRetrievalMax',5000)
		config.set(apiKey,'authorRetrievalUsed',0)
		config.set(apiKey,'AuthRlastTimeUsed','9999-99-99')
		config.set(apiKey,'affilRetrievalMax',5000)
		config.set(apiKey,'affilRetrievalUsed',0)
		config.set(apiKey,'afillRlastTimeUsed','9999-99-99')

		with open(configRateLimitsPath, 'wb') as configFile:
			config.write(configFile)

	return