# -*- coding: utf-8 -*-
"""
Created on Fri Jul 03 10:45:17 2015

@author: Pablo Mazzucchi
"""

# More data about Elsevier APIs
# http://api.elsevier.com/documentation/apis.html

# para generar el ejecutable se utilizo pyinstaller, con el siguiente comando
# pyinstaller -F .\ScopusAPIs.py
# mas info: http://pythonhosted.org/PyInstaller/

import requests
import json
import sys
import ConfigParser
import time
import configFile

outputPath=""
scopublicaciones=""
scoafiliaciones=""
scoautores=""
scopubbautafil=""
notProcessed=""
collab=""
summary=""
debugFilePath=""
logFile=""
inputPathAuthorsIDs=""
inputPathPubsIDs=""
MY_API_KEY=""
tecAffiliations=[]
affiliationID=""
yearFromStr=""
yearToStr=""
frameSizeStr=""
configParser=""
limitParser=""

affilCity={}
affilCountry={}
affilName={}
affilCount={}
processFirstPublications=True
publications=[]
executionMode="RUN"
configFilePath='C:\ScopusAPIs\config\config.cfg'
configRateLimitsPath='C:\ScopusAPIs\config\limits.cfg'

##############################################################################################
# Description: This function call the Scopus Search API using the query passed as parameter
# Input: query
# Output: list of publications with their respectives abstracts and metadata
# More info about scopus search API:
#   http://api.elsevier.com/documentation/SCOPUSSearchAPI.wadl
##############################################################################################

def scopusSearchAPI(searchParameters):

    global executionMode
    
    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("entré en: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))
            debugFilex|(searchParameters+"\n")

    query = "http://api.elsevier.com/content/search/scopus?query=" + searchParameters

    resp = requests.get(query, headers={'Accept':'application/json', 'X-ELS-APIKey': MY_API_KEY})

    section=MY_API_KEY
    variable="scopusSearchUsed"
    value=int(getConfigVarValue(section, variable))+1
    updateConfigVarValue(section,variable,value)
    
    variable="SSlastTimeUsed"
    value=time.strftime("%Y%m%d-%H%M%S")
    updateConfigVarValue(section,variable,value)
    
    functionName=sys._getframe().f_code.co_name

    results=resultsHandler(resp,functionName,"NA",query)

    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("salí de: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    return results

##############################################################################################
# Description: 
# Input: 
# Output: 
##############################################################################################

def getConfigVarValue(section, variable):
    global limitParser

    return limitParser.get(section,variable)

##############################################################################################
# Description: 
# Input: 
# Output: 
##############################################################################################

def updateConfigVarValue(section, variable, value):

    global limitParser

    limitParser.set(section, variable, value)

    with open(configRateLimitsPath, 'wb') as configFile:
        limitParser.write(configFile)

    return

##############################################################################################
# Description: 
# Input: 
# Output: 
##############################################################################################

def resultsHandler(resp,function,identif,query):

    global executionMode

    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("entré en: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    # dictionary with common errors
    dic = {'""$" :':'"',']"$" :}':'] }'}
    results={}
    fstring = '[{ResultCode}]-[{ErrorCode}]-[{ErrorMsg}]-[{FunctionName}]-[{Query}]-[{Time}]'
    resultCode=''
    
    if resp != '' :
        resultCode = str(resp)
        if resultCode == "<Response [200]>":
            try:
                temp = replaceAll(resp.text,dic)
                partialResults = json.loads(temp.encode('utf-8') )
                if isEmpty(partialResults):
                    results={}
                    s = fstring.format(ResultCode    = resultCode,
                                       ErrorCode     = "",
                                        ErrorMsg     = "Ya no se obtuvieron resultados",
                                        FunctionName = function,
                                        Query        = query,
                                        Time         = time.strftime("%Y%m%d-%H%M%S"))
                    
                    if executionMode=="RUN":
                        with open(logFile,"a") as log:
                            log.write(s +"\n")
                else:
                    results=partialResults

            except ValueError, e:

                results={}
                s = fstring.format(ResultCode    = resultCode,
                                   ErrorCode     = identif , 
                                    ErrorMsg     = "corruptJSON - " + e.message, 
                                    FunctionName = function,
                                    Query        = query,
                                    Time         = time.strftime("%Y%m%d-%H%M%S")) 

                if executionMode=="RUN":
                    with open(logFile,"a") as log:
                        log.write(s +"\n")
        else:
            try:
                temp=resp.json()
                
                if not(isEmpty(temp)):
                    error = temp['service-error']['status']        
                    errorMsg = str(error['statusText'])
                    errorCode = str(error['statusCode'])
                      
                    s = fstring.format(ResultCode    = resultCode,
                                       ErrorCode     = errorCode,
                                        ErrorMsg     = errorMsg,
                                        FunctionName = function,
                                        Query        = query,
                                        Time         = time.strftime("%Y%m%d-%H%M%S"))
                    
                    if executionMode=="RUN":
                        with open(logFile,"a") as log:
                            log.write(s +"\n")
            except:
                s = fstring.format(ResultCode    = resultCode,
                                   ErrorCode     = '', 
                                    ErrorMsg     = "No se pudo procesar el error",
                                    FunctionName = function,
                                    Query        = query,
                                    Time         = time.strftime("%Y%m%d-%H%M%S"))
                
                if executionMode=="RUN":
                    with open(logFile,"a") as log:
                        log.write(s +"\n")

    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("salí de: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))
               
    return results


##############################################################################################
# Description: 
# Input: 
# Output: 
##############################################################################################

def isEmpty(tempResults):

    empty=False

    try: 
        amountOfPubsRec=tempResults['search-results']['opensearch:totalResults']
        if ( amountOfPubsRec == '0') or (amountOfPubsRec == None):
            empty=True
        #if tempResults['search-results']['entry'][0]['error']=='Result set was empty':
        #    empty=True
    except KeyError, e:
        pass

    return empty

##############################################################################################
# Description: This function obtains just the publication'IDs, processing the results obtained
#              by the scopus search API
# Input: results of scopus search API in JSON format
# Output: list of publication IDs
##############################################################################################

def getListOfPublications(results):

    global executionMode
    
    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("entré en: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    try:
        listPublications =  map(mapperListOfPubs, results['search-results']['entry'])
    except ValueError, e:

        if executionMode=="RUN":
            with open(logFile,"a") as log:
                log.write('Decoding JSON has failed: [%s] - [%s] \n' % (str(e), time.strftime("%Y%m%d-%H%M%S")))

        listPublications = []
    except KeyError, e:

        if executionMode=="RUN":
            with open(logFile,"a") as log:
                log.write('KeyError because: [%s] - [%s] \n' % (str(e), time.strftime("%Y%m%d-%H%M%S")))

        listPublications = []

    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("salí de: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    return listPublications

##############################################################################################
# Description: 
# Input: 
# Output: 
##############################################################################################

def mapperListOfPubs(searchResults):
    return str(searchResults['dc:identifier'])

##############################################################################################
# Description: This function remove specific characters (specified in the dictionary) from 
#              the string passed as parameter.
# Input: the string to be analized & the dictionary with the specific values to be removed
# Output: the string passed as input with less characters
##############################################################################################

def replaceAll(text,dic):
    for i,j in dic.iteritems():
        text = text.replace(i,j)
    return text

##############################################################################################
# Description: This function retrieve information of a certain affiliation, using
#              the Affiliation Search API.  For more information about this API:
#              1. http://api.elsevier.com/documentation/AFFILIATIONSearchAPI.wadl#N10027
# Input: scopus ID of the affiliation
# Output: amount of publications that has the respective affiliation
# Note: To validate json structure, go to http://jsonlint.com/
##############################################################################################

def affiliationSearchAPI(AFFIL_ID):

    global executionMode
    
    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("entré en: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))
            debugFile.write(AFFIL_ID+"\n")

    query="AF-ID(" + AFFIL_ID + ")&field=dc:identifier,document-count"
    url = ("http://api.elsevier.com/content/search/affiliation?query="+query)
    resp = requests.get(url,
                    headers={'Accept':'application/json',
                             'X-ELS-APIKey': MY_API_KEY})

    section=MY_API_KEY
    variable="affilsearchused"
    value=int(getConfigVarValue(section, variable))+1
    updateConfigVarValue(section,variable,value)
    
    variable="afilslasttimeused"
    value=time.strftime("%Y%m%d-%H%M%S")
    updateConfigVarValue(section,variable,value)
    
    functionName=sys._getframe().f_code.co_name

    results=resultsHandler(resp,functionName,AFFIL_ID,query)
  
    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("salí de: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    return results

##############################################################################################
# Description: This function process the results obtained by the Affil search API
# Input: results obtained by the affil search API in json format
# Output: amount of publications that has the respective affiliation (as INT)
##############################################################################################

def processAffilResults(resp):

    global executionMode
    
    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("entré en: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    totalPublications=0
    affilID=''

    # Validating if the dictionary is not empty
    if resp:
        try:
            affilID=resp['search-results']['entry'][0]['dc:identifier']
            totalPublications = str(resp['search-results']['entry'][0]['document-count'])
        except ValueError, e:

            if executionMode=="RUN":
                with open(logFile,"a") as log:
                    log.write('Affiliation could not be proccesed: [%s] - Error Message: [%s] - [%s]\n' % (affilID,e.message,time.strftime("%Y%m%d-%H%M%S")))

        except KeyError, e:

            if executionMode=="RUN":
                with open(logFile,"a") as log:
                    log.write('KeyError because: [%s] - [%s] - [%s] - [%s]\n' % (str(e), affilID, sys._getframe().f_code.co_name,time.strftime("%Y%m%d-%H%M%S")))

    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("salí de: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    return totalPublications

##############################################################################################
# Description: This function retrieve information of a certain publication, using
#              the Abstract Retrieval API.  For more information about this API:
#              1. http://api.elsevier.com/documentation/AbstractRetrievalAPI.wadl
#              2. http://api.elsevier.com/documentation/retrieval/AbstractRetrievalViews.htm
# Input: scopus ID of a publication
# Output: Type of publication, title, authors, issue date, cite count, affiliation
# Note: To validate json structure, go to http://jsonlint.com/
##############################################################################################

def abstractRetrievalAPI(SCOPUS_ID):
    
    query=SCOPUS_ID+"?field=title,publicationName,authors,coverDate,affiliation,citedby-count,prism:aggregationType"

    url = ("http://api.elsevier.com/content/abstract/scopus_id/"+query)
    resp = requests.get(url,headers={'Accept':'application/json','X-ELS-APIKey': MY_API_KEY})

    section=MY_API_KEY
    variable="absretrievalused"
    value=int(getConfigVarValue(section, variable))+1
    updateConfigVarValue(section,variable,value)
    
    variable="absrlasttimeused"
    value=time.strftime("%Y%m%d-%H%M%S")
    updateConfigVarValue(section,variable,value)

    functionName=sys._getframe().f_code.co_name
    
    results=resultsHandler(resp,functionName,SCOPUS_ID,query)
    
    return results

##############################################################################################
# Description: This function retrieve information of a certain author, using
#              the Author Retrieval API.  For more information about this API:
#              1. http://api.elsevier.com/documentation/AuthorRetrievalAPI.wadl#N101F4
# Input: scopus ID of the author
# Output: orcID, Name and Surname, Affiliation, amount of documents authored, citations made
#         cited by
# Note: To validate json structure, go to http://jsonlint.com/
##############################################################################################

def authorRetrievalAPI(SCOPUS_ID):

    query = SCOPUS_ID+ "?field=dc:identifier,surname,given-name,document-count,cited-by-count,citation-count,affiliation-current,affiliation-history"
            
    url = ("http://api.elsevier.com/content/author/author_id/"+query)
    resp = requests.get(url, headers={'Accept':'application/json','X-ELS-APIKey': MY_API_KEY})

    section=MY_API_KEY
    variable="authorretrievalused"
    value=int(getConfigVarValue(section, variable))+1
    updateConfigVarValue(section,variable,value)
    
    variable="authrlasttimeused"
    value=time.strftime("%Y%m%d-%H%M%S")
    updateConfigVarValue(section,variable,value)

    functionName=sys._getframe().f_code.co_name
    
    results=resultsHandler(resp,functionName,SCOPUS_ID,query)
                
    return results

##############################################################################################
# Description: This function reads an input file (with a defined format) a loads in memory
#              all the authorsIDs that appear in the file, for further processing
# Input: file with scopus ID of the authors
# Output: list with all the scopus IDs
##############################################################################################

def processInputFile(inputPath):
   
    listOfObjects=[]

    with open (notProcessed, 'a') as log:

        try:
            with open (inputPath,'r') as input:

                for line in input:
                    listOfObjects.append(line)

                return listOfObjects

        except IOError as e:
            log.write("Operation failed: %s \n" % e.strerror) 

##############################################################################################
# Description: This function obtains the authors'IDs that belongs to a respective affiliation
#              (current affiliation)  (using Author Search API)
#              source: http://api.elsevier.com/content/search/author
# Input: affiliation ID, maximum amount of publications, index (to avoid getting the same
#        publications IDs over and over if there is more than frameSizeStr to download)
# Output: list of authors
##############################################################################################

def authorSearchAPI(affiliationID, index):
        
    listAuthorsIDs = []
    index = str(index)
    
    query = "http://api.elsevier.com/content/search/author?query=AF-ID(" + affiliationID + ")&field=dc:identifier&start="+index+"&count="+frameSizeStr

    resp = requests.get(query, headers={'Accept':'application/json', 'X-ELS-APIKey': MY_API_KEY})

    section=MY_API_KEY
    variable="authorsearchused"
    value=int(getConfigVarValue(section, variable))+1
    updateConfigVarValue(section,variable,value)
    
    variable="authslasttimeused"
    value=time.strftime("%Y%m%d-%H%M%S")
    updateConfigVarValue(section,variable,value)

    functionName=sys._getframe().f_code.co_name
    
    results=resultsHandler(resp,functionName,affiliationID,query)

    if results:
        try:
            listAuthorsIDs = [[str(r['dc:identifier'])] for r in results['search-results']['entry']]
        except:
            listAuthorsIDs = []
    else:
        listAuthorsIDs = []

    return listAuthorsIDs

##############################################################################################
# Description: This function obtains the publications'IDs published by a certain affiliation
#              in a defined period of time (using Scopus Search API)
#              source: 
# Input: affiliation ID, year(you should use 2009 if you are looking publications since 2010,
#        for example), maximum amount of publications, index (to avoid getting the same
#        publications IDs over and over if there is more than frameSizeStr to download)
# Output: list of publications
# More info: http://api.elsevier.com/documentation/search/SCOPUSSearchTips.htm
#            http://api.elsevier.com/content/search/fields/scopus
##############################################################################################

def getPublicationsIDsByAffiliation(affiliationID, index):
    
    affiliationIDStr = str(affiliationID)
    indexStr = str(index)
    
    query = "http://api.elsevier.com/content/search/scopus?query=AF-ID(" + affiliationIDStr + ")AND+PUBYEAR+>+"+yearFromStr+"&field=dc:identifier&start="+indexStr+"&count="+frameSizeStr
    
    resp = requests.get(query, headers={'Accept':'application/json', 'X-ELS-APIKey': MY_API_KEY})

    section=MY_API_KEY
    variable="scopussearchused"
    value=int(getConfigVarValue(section, variable))+1
    updateConfigVarValue(section,variable,value)
    
    variable="sslasttimeused"
    value=time.strftime("%Y%m%d-%H%M%S")
    updateConfigVarValue(section,variable,value)

    functionName=sys._getframe().f_code.co_name
    
    results=resultsHandler(resp,functionName,affiliationID,query)
        
    if results:       
        try:
            listPublications =  [[str(r['dc:identifier'])] for r in results['search-results']['entry']] 
        except:
            listPublications = []
    else:
        listPublications = []
       
    return listPublications

##############################################################################################
# Description: the function get all the authors that currently publish using the affiliation
#              ID given as a parameter (throw authorSearchAPI()) and then obtains
#              more info about them using authorRetrievalAPI()
# Input: affiliation ID
# Output: author name, surname, citations, documents published, amout of papers that cite 
#         their publications, and current affiliation info
##############################################################################################

def getListofAuthorsByAffil(listOfAffiliations):
        
    with open(outputPath, 'w') as f:
        
        f.write('affiliationID' + '|'+ 'AuthorID' + '|'+ 'Name' + '|'+ 'Citations #' + '|'+ 'Documents #' + '|'+ 'Cited by' + '|'+ 'Current Affil Name' + '|'+ 'Current Affil City' + '|'+ 'Current Affil Country' + '\n')
                  
        for affiliationID in listOfAffiliations:
            affiliationIdStr= str(affiliationID)
            index = 0
            listOfAuthorsIDs = authorSearchAPI(affiliationIdStr, index);

            while len(listOfAuthorsIDs) > 0:
                for sid in listOfAuthorsIDs:
                    # some entries seem to have json parse errors, so we catch those
                    try:
                        scopusID = sid[0].split(':')[1];
                        
                        results = authorRetrievalAPI(scopusID)
                       
                        try:
                            surname=results['author-retrieval-response'][0]['preferred-name']['surname'].encode('utf-8');
                            givenName=results['author-retrieval-response'][0]['preferred-name']['given-name'].encode('utf-8');
                            affiliation_current_name=results['author-retrieval-response'][0]['affiliation-current']['affiliation-name'].encode('utf-8');                        
                            affiliation_current_city=results['author-retrieval-response'][0]['affiliation-current']['affiliation-city'].encode('utf-8');                        
                            affiliation_current_country=results['author-retrieval-response'][0]['affiliation-current']['affiliation-country'].encode('utf-8');                        
                            citation_count=int(results['author-retrieval-response'][0]['coredata']['citation-count'].encode('utf-8'))
                            document_count=int(results['author-retrieval-response'][0]['coredata']['document-count'].encode('utf-8'))
                            cited_by_count=int(results['author-retrieval-response'][0]['coredata']['cited-by-count'].encode('utf-8'))

                            name=""
                            name = surname + ", " + givenName
                                      
                            fstring = '{affiliationID}|{authorID}|{preferred_name}|{citations_count}|{document_count}|{cited_by_count}|{affiliation_current_name}|{affiliation_current_city}|{affiliation_current_country}'
            
                            s = fstring.format(affiliationID               = affiliationIdStr,
                                               authorID                    = scopusID,
                                               preferred_name              = name,
                                               citations_count             = citation_count,
                                               document_count              = document_count,
                                               cited_by_count              = cited_by_count,
                                               affiliation_current_name    = affiliation_current_name,
                                               affiliation_current_city    = affiliation_current_city,
                                               affiliation_current_country = affiliation_current_country)

                            f.write(s+'\n')

                        except Exception:
                            fstring = '{affiliationID}|{author}';
                            s = fstring.format(affiliationID = affiliationIdStr, 
                                                       author = scopusID)  

                    except Exception:
            
                        fstring = '{affiliationID}|{author}';
                        s = fstring.format(affiliationID = affiliationIdStr, 
                                           author = 'No se pudo recuperar este ID')

                        f.write(s+'\n')
                             
                index = index + int(frameSizeStr)
               
                if len(listOfAuthorsIDs) <= index:
                    #There are more records than expected
                    listOfAuthorsIDs=[]
                else:
                    listOfAuthorsIDs = authorSearchAPI(affiliationIdStr, index);
                
    return    
      
 ##############################################################################################
# Description: the function get info of certain publications published using the affiliation
#              given as parameter.  It uses the Scopus Search API and the Abstract Retrieval API 
# Input: affiliation ID and initial year the API should starts looking at (not inclusive)
# Output: affiliation info, publication info and authors info
##############################################################################################   
    
def getPublicationInfoByAffiliation(queryConditions, indexStr, frameSizeStr):

    global executionMode
    global processFirstPublications
    morePublications=True
    
    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("entré en: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))
                
    while morePublications:
    
        query=queryConditions+"&field=dc:identifier&start="+indexStr+"&count="+frameSizeStr

        results=scopusSearchAPI(query)
            
        if results:
            scopusPubsIDs = getListOfPublications(results)

            if len(scopusPubsIDs)>=int(frameSizeStr):
                indexStr=str(int(indexStr)+int(frameSizeStr))
            else:
                morePublications=False

            processPublications(scopusPubsIDs)

        else:
            morePublications=False
    
    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("salí de: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    return

 ##############################################################################################
# Description: 
# Input: 
# Output: 
############################################################################################## 

def removeDuplicates(scopusPubsIDs):

    global executionMode
    global publications
    scopusPubsIDs_filtered=[]
    
    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("entré en: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))
    
    for sid in scopusPubsIDs:
        scopusID = sid.split(':')[1]

        if not (scopusID in publications):
            publications.append(scopusID)
            scopusPubsIDs_filtered.append(sid)

    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("salí de: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    return scopusPubsIDs_filtered


 ##############################################################################################
# Description: 
# Input: 
# Output: 
############################################################################################## 

def transformAffilIntoScopusFormat(tecaffiliations):

    firstTime=True

    for affiliation in tecaffiliations:
        if firstTime:
            firstTime=False
            affilToScopus="AF-ID("+affiliation+")"
        else:
            affilToScopus=affilToScopus+"+OR+AF-ID("+affiliation+")"

    return affilToScopus

 ##############################################################################################
# Description: 
# Input: 
# Output: 
############################################################################################## 

def optionHandler(opcion):

    global executionMode
    global tecAffiliations

    # The needed variables are uploaded in memory
    unpackingConfigFileVariables()
    
    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("entré en: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    if opcion==1:
        # Obtain the list of authors 
        authorList=processInputFile(inputPathAuthorsIDs)
        # Obtain each author papers
        for author in authorList:
            query="AU-ID(" + author.strip() + ")+AND+PUBYEAR+>+"+yearFromStr+"+AND+PUBYEAR+<+"+yearToStr+"&field=dc:identifier&count="+frameSizeStr
            obtainAndProcessPublic(query)

        affiliationStatistics()

    elif opcion==2:
        query="((AFFIL(tecnológico de monterrey)+OR+AFFIL(itesm))+OR+AFFIL(hosp* san josé tec* monterrey))+AND+NOT((AF-ID(60018640)))+OR+(AF-ID(60007966))+AND+PUBYEAR+>+"+yearFromStr+"+AND+PUBYEAR+<+"+yearToStr+"&field=dc:identifier&count="+frameSizeStr
        obtainAndProcessPublic(query)

    elif opcion==3:
        query="(AFFIL(tec de monterrey))+AND+NOT((AFFIL(tecnológico de monterrey)+OR+AFFIL(itesm))+OR+AFFIL(hosp* san josé tec* monterrey))+AND+PUBYEAR+>+"+yearFromStr+"+AND+PUBYEAR+<+"+yearToStr+"&field=dc:identifier&count="+frameSizeStr
        obtainAndProcessPublic(query)

    elif opcion==4:
        affilParameters=transformAffilIntoScopusFormat(tecAffiliations)
        queryParameters=affilParameters+"+ AND+PUBYEAR+>+"+yearFromStr+"+AND+PUBYEAR+<+"+yearToStr
        getPublicationInfoByAffiliation(queryParameters, "0", frameSizeStr)

    elif opcion==5:
        queryParameters=transformAffilIntoScopusFormat(tecAffiliations)
        getPublicationInfoByAffiliation(queryParameters, "0", frameSizeStr)

    elif opcion==6:
        # Obtain list of SCOPUS ID of the publications
        pubList=processInputFile(inputPathPubsIDs)
        processPublications(pubList)

    elif opcion==7:
        getListofAuthorsByAffil(tecAffiliations)
        

    return

##############################################################################################
# Description: The function return the amount of publication linked to an affiliation in a
#              respective period of time
# Input: id of the affiliation
# Output: amount of publications in a period of time
##############################################################################################

def obtainAndProcessPublic(query):

    global executionMode

    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("entré en: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    results=scopusSearchAPI(query)

    if results:
        scopusPubsIDs = getListOfPublications(results) # Just keep the scopus ID

        if  len(scopusPubsIDs) > 0:
            # In this case, there is results to process and publications to obtain more info from
            scopusPubsIDs_filtered=removeDuplicates(scopusPubsIDs) # duplicates publications are removed to avoid calling the API multiple times looking for a publication that already was retrieved
            processPublications(scopusPubsIDs_filtered) # All the info from the publications is extracted, formatted and saved in a file
            
    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("salí de: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    return

##############################################################################################
# Description: The function return the amount of publication linked to an affiliation in a
#              respective period of time
# Input: id of the affiliation
# Output: amount of publications in a period of time
##############################################################################################

def affiliationStatistics():

    global affilCity
    global affilCountry
    global affilName
    global affilCount

    # Process the affiliation info collected in processPublications(), to create a summary of the 
    # collaboration with other universities/research centers
    try:
        with open (summary, 'w') as su:    

            su.write('affiliationID' + '|'+ 'affilName' + '|'+ 'affilCity' + '|'+ 'affilCountry' + '|' + 'pubCount' + '|' + 'totalPubPeriod' + '|' +'totalPub' + '\n')
            sstring = '{affiliationID}|{affilName}|{affilCity}|{affilCountry}|{counterPub}|{totalPubPeriod}|{totalPub}'

            for id, count in affilCount.iteritems():
                
                affName=affilName[id]
                affCity=affilCity[id]
                affCountry=affilCountry[id]
                countPub=count

                totalPublicationsSamePeriod=getAmountOfPubsByAffilInaPeriod(id,"0")

                totalPublications=processAffilResults(affiliationSearchAPI(id))

                s = sstring.format(affiliationID = id,
                                       affilName = affName, 
                                       affilCity = affCity,
                                    affilCountry = affCountry,
                                      counterPub = countPub,
                                totalPubPeriod   = totalPublicationsSamePeriod,
                                      totalPub   = totalPublications)

                su.write(s +'\n')

    except IOError as e:

        if executionMode=="RUN":
            with open(logFile,"a") as log:
                log.write('Operation failed at: [%s] - [%s] - [%s]\n' % (sys._getframe().f_code.co_name, e.strerror, time.strftime("%Y%m%d-%H%M%S")))

    return

##############################################################################################
# Description: The function return the amount of publication linked to an affiliation in a
#              respective period of time
# Input: id of the affiliation
# Output: amount of publications in a period of time
############################################################################################## 

def getAmountOfPubsByAffilInaPeriod(idAffiliation,indexStr):

    global executionMode
    
    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("entré en: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    morePublications=True
    totalAmount=0

    while(morePublications):
        amountOfPubs=0
        query = "AF-ID(" + idAffiliation + ")AND+PUBYEAR+>+"+yearFromStr+"AND+PUBYEAR+<+"+yearToStr+"&field=dc:identifier&start="+indexStr+"&count="+frameSizeStr  
        results=scopusSearchAPI(query)

        if results:
            amountOfPubs = len(getListOfPublications(results))
            totalAmount+=amountOfPubs

            if amountOfPubs>=int(frameSizeStr):
                indexStr=str(int(indexStr)+int(frameSizeStr))
            else:
                morePublications=False
        else:
            morePublications=False

    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("salí de: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    return totalAmount

##############################################################################################
# Description: The function process the JSON of all the list of publications given a parameter,
#              and save into files all the necessary information
# Input: scopus IDs of publications
# Output: 
##############################################################################################  

def processPublications(scopusPubsIDs):
    
    global executionMode
    global affilCity
    global affilCountry
    global affilName
    global affilCount
    global processFirstPublications
    
    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("entré en: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    if (processFirstPublications):
        mode='w'
        processFirstPublications=False
    else:
        mode='a'

    try:
        with open (scopubbautafil, mode) as f1, open (scoautores, mode) as f2, open (scoafiliaciones, mode) as f3, open (scopublicaciones, mode) as f4, open (notProcessed, mode) as l, open (collab, mode) as c:
        
            # First time header is written
            if mode=='w':
                #f.write('affiliationID' + '|'+ 'affilName' + '|'+ 'affilCity' + '|'+ 'affilCountry' + '|' + 'ScopusIDPub' + '|'+ 'TipoPub' + '|'+ 'Title' + '|' + 'Source'+ '|' +  'Date'+ '|'+'Cantidad Citas' + '|' + 'Author' + '|' + 'AuthorID' + '|' + '\n')
                f1.write('affiliationID' + '|'+ 'ScopusIDPub' + '|'+ 'AuthorID' + '\n')
                f2.write('AuthorID' + '|' + 'Author' + '\n')
                f3.write('affiliationID' + '|'+ 'affilName' + '|'+ 'affilCity' + '|'+ 'affilCountry' + '\n')
                f4.write('ScopusIDPub' + '|'+ 'TipoPub' + '|'+ 'Title' + '|' + 'Source'+ '|' +  'Date'+ '|'+'Cantidad Citas' + '\n')
                c.write('affiliationID' + '|'+ 'affilName' + '|'+ 'affilCity' + '|'+ 'affilCountry' + '|' + 'ScopusIDPub' + '|'+ 'TipoPub' + '|'+ 'Title' + '|' + 'Source'+ '|' +  'Date'+ '|'+'Cantidad Citas' + '|' + 'Author' + '|' + 'AuthorID' + '|' + '\n')
                l.write('affiliationID' + '|'+ 'affilName' + '|'+ 'affilCity' + '|'+ 'affilCountry' + '|' + 'ScopusIDPub' + '|'+ 'TipoPub' + '|'+ 'Title' + '|' + 'Source'+ '|' +  'Date'+ '|'+'Cantidad Citas' + '|' + 'Author' + '|' + 'AuthorID' + '|' + '\n')
            
            fstring = '{affiliationID}|{affilName}|{affilCity}|{affilCountry}|{scopusIDPub}|{tipoPub}|{title}|{source}|{date}|{cites}|{author}|{authorID}'
            f1string = '{affiliationID}|{scopusIDPub}|{authorID}'
            f2string = '{authorID}|{author}'
            f3string = '{affiliationID}|{affilName}|{affilCity}|{affilCountry}'
            f4string = '{scopusIDPub}|{tipoPub}|{title}|{source}|{date}|{cites}'

            if  len(scopusPubsIDs) > 0:  
                i = 0
                for sid in scopusPubsIDs:

                    tipoPub = ''
                    title = ''
                    source = ''
                    date = ''
                    cites = ''
                    author = ''
                    authorID = ''
                    affID = ''
                    affIDConcat = ''
                    affNameConcat = ''
                    sameAffiliation = False
                    affName=''
                    affCity=''
                    affCountry=''
                    scopusID=sid

                    # some entries seem to have json parse errors, so we catch those
                    try:
                        #scopusID = sid[0].split(':')[1]
                        scopusID = sid.split(':')[1]

                        #results = abstractRetrievalAPI(str(sid[0]))  # index 0 because the input data is a 2d array     
                        results = abstractRetrievalAPI(str(sid))

                        if results:
                            if 'prism:aggregationType' in results['abstracts-retrieval-response']['coredata'].keys():
                                tipoPub = results['abstracts-retrieval-response']['coredata']['prism:aggregationType'];
                            if 'dc:title' in results['abstracts-retrieval-response']['coredata'].keys():
                                title=results['abstracts-retrieval-response']['coredata']['dc:title'].encode('utf-8');
                            if 'prism:publicationName' in results['abstracts-retrieval-response']['coredata'].keys():
                                source=results['abstracts-retrieval-response']['coredata']['prism:publicationName'].encode('utf-8');
                            if 'prism:coverDate' in results['abstracts-retrieval-response']['coredata'].keys():
                                date=results['abstracts-retrieval-response']['coredata']['prism:coverDate'].encode('utf-8');
                            if 'citedby-count' in results['abstracts-retrieval-response']['coredata'].keys():
                                cites=int(results['abstracts-retrieval-response']['coredata']['citedby-count'].encode('utf-8'))                       
                            
                            affilID=''
                            affiliation_city=''
                            affilname=''
                            affiliation_country=''

                            listAffil=[]
                            # Primero verificar que si se pudieron recuperar las afiliaciones
                            if ('affiliation' in results['abstracts-retrieval-response'].keys()):
                                if (type(results['abstracts-retrieval-response']['affiliation']) is dict):
                                    listAffil.append(results['abstracts-retrieval-response']['affiliation'])
                                else:
                                    listAffil=results['abstracts-retrieval-response']['affiliation']

                                for affil in listAffil:

                                    if affil['@id']==None:
                                        affilID='No_Affil_ID'
                                    else:
                                        affilID = affil['@id'].encode('utf-8')

                                    if affil['affiliation-city'] == None:
                                        affiliation_city='No_Affil_City'
                                    else:
                                        affiliation_city = affil['affiliation-city'].encode('utf-8')

                                    if affil['affilname'] == None:
                                        affilname='No_Affil_Name'
                                    else:
                                        affilname = affil['affilname'].encode('utf-8')

                                    if affil['affiliation-country'] == None:
                                        affiliation_country='No_Affil_Country'
                                    else:
                                        affiliation_country = affil['affiliation-country'].encode('utf-8')

                                    if affilCount.get(affilID) == None:
                                        affilCount[affilID]=1
                                        affilCity[affilID] = affiliation_city
                                        affilCountry[affilID] = affiliation_country
                                        affilName[affilID] = affilname
                                    else:
                                        affilCount[affilID]=affilCount[affilID]+1

                            else:
                                affilID = 'No_Afilliation'

                                if affilCount.get(affilID) == None:
                                    affilCount[affilID]=1
                                    affilCity[affilID] = 'No_Affil_City'
                                    affilCountry[affilID] = 'No_Affil_Country'
                                    affilName[affilID] = 'No_Affil_Name'
                                else:
                                    affilCount[affilID]=affilCount[affilID]+1

                            # Process all the authors of the publication
                            for au in results['abstracts-retrieval-response']['authors']['author']:
                                author = ''
                                authorID = ''
                                affID = ''
                                affName=''
                                affCity=''
                                affCountry=''
                                affIDConcat = ''
                                affCountryConcat= ''
                                affCityConcat = ''
                                affNameConcat = ''
                                sameAffiliation = False
                                author = au['ce:indexed-name'].encode('utf-8')
                                authorID = au['@auid'].encode('utf-8')

                                if ('affiliation' in au.keys()):
                                    
                                    # Could have 1 (dictionary) or more affiliations (list of dictionaries)                                
                                    if (type(au['affiliation']) is dict):
                                        
                                        affID = au['affiliation']['@id']

                                        if affID in affilName.keys():
                                            # the author has an affiliation and it was also listed at ['abstracts-retrieval-response']['affiliation'].
                                            affName =affilName[affID]
                                            affCity=affilCity[affID]
                                            affCountry=affilCountry[affID]
                                        else:
                                            # the author has an affiliation but it was not listed at ['abstracts-retrieval-response']['affiliation']
                                            # TODO : to get the affiliation data, the affilAPI should be called.  The result should be handled
                                            # results=affiliationSearchAPI(affID)
                                            affCity = 'Affil_City_Not_Available'
                                            affCountry = 'Affil_Country_Not_Available'
                                            affName = 'Affil_Name_Not_Available'

                                        if(affID in tecAffiliations):
                                            sameAffiliation = True
                                        
                                    elif type(au['affiliation']) is list:
                                        for affIDs in au['affiliation']:

                                            affID = affIDs['@id']

                                            if (affID in tecAffiliations):
                                                sameAffiliation = True
                                                
                                            if affIDConcat == '':
                                                affIDConcat = affID
                                            else:
                                                affIDConcat =  affIDConcat + '#' + affID

                                            if affCityConcat == '':
                                                affCityConcat = affilCity[affID]
                                            else:
                                                affCityConcat =  affCityConcat + '#' + affilCity[affID]

                                            if affCountryConcat == '':
                                                affCountryConcat = affilCountry[affID]
                                            else:
                                                affCountryConcat =  affCountryConcat + '#' + affilCountry[affID]

                                            if affNameConcat == '':
                                                affNameConcat = affilName[affID]
                                            else:
                                                affNameConcat =  affNameConcat + '#' + affilName[affID]
                                        
                                        affID = affIDConcat
                                        affCountry=affCountryConcat
                                        affCity=affCityConcat
                                        affName=affNameConcat
                              
                                else:
                                    affID = 'No_Afilliation'
                                
                                # s = fstring.format(affiliationID=affID,
                                #                        affilName=affName, 
                                #                        affilCity=affCity,
                                #                     affilCountry=affCountry,
                                #                      scopusIDPub=scopusID,
                                #                          tipoPub=tipoPub,
                                #                            title=title,
                                #                           source=source,
                                #                             date=date,
                                #                            cites=cites,
                                #                           author=author,
                                #                         authorID=authorID)
                                s1 = f1string.format(affiliationID=affID,
                                                      scopusIDPub=scopusID,
                                                         authorID=authorID)
                                s2 = f2string.format(authorID=authorID,
                                                      author=author)
                                s3 = f3string.format(affiliationID=affID,
                                                        affilName=affName, 
                                                        affilCity=affCity,
                                                     affilCountry=affCountry)
                                s4 = f4string.format(scopusIDPub=scopusID,
                                                        tipoPub=tipoPub,
                                                          title=title,
                                                         source=source,
                                                           date=date,
                                                          cites=cites)

                                
                                #if (sameAffiliation):
                                f1.write(s1 +'\n')
                                f2.write(s2 +'\n')
                                f3.write(s3 +'\n')
                                f4.write(s4 +'\n')
                                # else:
                                #     c.write(s +'\n')
                        else:
                            if executionMode=="RUN":
                                with open(logFile,"a") as log:
                                    log.write('No existen datos sobre la publicacion: [%s] en abstractRetrievalAPI - [%s]\n' % (scopusID,time.strftime("%Y%m%d-%H%M%S")))

                    except:
                        s = fstring.format(affiliationID = affID,
                                   affilName = affName, 
                                   affilCity = affCity,
                                affilCountry = affCountry,
                                 scopusIDPub = scopusID,
                                     tipoPub = tipoPub,
                                        title=title,
                                      source=source,
                                         date=date,
                                        cites=cites,
                                       author=author,
                                     authorID=authorID)

                        l.write(s+'\n')
    except IOError as e:
        
        if executionMode=="RUN":
            with open(logFile,"a") as log:
                log.write('Operation failed: %s - [%s]\n' % (e.strerror,time.strftime("%Y%m%d-%H%M%S")))

    if executionMode=="DEBUG":
        with open(debugFilePath,"a") as debugFile:
            debugFile.write("salí de: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))

    return

##############################################################################################
# Description: 
# Input: 
# Output:
# source: 
# http://stackoverflow.com/questions/30384712/issue-doing-a-basic-option-menu-system-aways-getting-the-message-option-not-a
##############################################################################################

def userInterface():
    response_options = {'1': ('Proceso Semestral', "optionHandler"),
                        '2': ('Query 1', "query_1"),
                        '3': ('Query 2', "query_2"),
                        '4': ('Publicaciones con Afiliaciones TEC', "Pubs_Afil_TEC"),
                        '5': ('Publicaciones con Afiliaciones TEC, sin filtro de fechas', "Pubs_Afil_TEC_sin"),
                        '6': ('Publicaciones pasando los SCOPUS ID de las mismas', "Pubs_With_SCOPUSID"),
                        '7': ('Autores con Afiliacion del Tec', "authorsTECAffil"),
                        '8': ('Exit', "exit"),    
                        '9': ('Inicializar variables', "init_variables"),
                        '10': ('Inicializar limites API', "init_limits")}
                        
    response_func = make_choice(response_options)

    if response_func == "optionHandler":
        optionHandler(1)
    elif response_func == "query_1":
        optionHandler(2)
    elif response_func == "query_2":
        optionHandler(3)
    elif response_func == "Pubs_Afil_TEC":
        optionHandler(4)
    elif response_func == "Pubs_Afil_TEC_sin":
        optionHandler(5)
    elif response_func == "Pubs_With_SCOPUSID":
        optionHandler(6)
    elif response_func == "authorsTECAffil":
        optionHandler(7)
    elif response_func == "exit":
        sys.exit()
    elif response_func == "init_variables":
        configFile.packingConfigVariables()
    elif response_func == "init_limits":
        configFile.initlializeAPIsRateLimits()

    return

##############################################################################################
# Description: 
# Input: 
# Output: 
##############################################################################################

def make_choice(optiontable):
    for resp, msg_func in optiontable.items():
        msg, _ = msg_func
        print("{} - {}".format(resp, msg))
    usr_resp = raw_input(">> ")
    try:
        result = optiontable[usr_resp][1]
    except KeyError:   
        if executionMode=="RUN":
            with open(logFile,"a") as log:
                log.write("La opción ingresada no está en el menú: [%s] - [%s]\n" % (sys._getframe().f_code.co_name, time.strftime("%Y%m%d-%H%M%S")))
    return result

##############################################################################################
# Description: 
# Input: 
# Output: 
##############################################################################################    
    
def unpackingConfigFileVariables():

    global outputPath
    global scopublicaciones
    global scoafiliaciones
    global scoautores
    global scopubbautafil
    global notProcessed
    global collab
    global summary
    global debugFilePath
    global logFile
    global inputPathPubsIDs
    global inputPathAuthorsIDs
    global MY_API_KEY
    global tecAffiliations
    global affiliationID
    global yearFromStr
    global yearToStr
    global frameSizeStr
    global configParser
    global limitParser

    limitParser=ConfigParser.RawConfigParser()
    limitParser.read(configRateLimitsPath)

    configParser=ConfigParser.RawConfigParser()
    configParser.read(configFilePath)

    outputPath=configParser.get('FILES','outputPath')
    scopublicaciones=configParser.get('FILES','scopublicaciones')
    scoafiliaciones=configParser.get('FILES','scoafiliaciones')
    scoautores=configParser.get('FILES','scoautores')
    scopubbautafil=configParser.get('FILES','scopubbautafil')

    notProcessed=configParser.get('FILES','notProcessed')
    collab=configParser.get('FILES','collab')
    summary=configParser.get('FILES','summary')
    debugFilePath=configParser.get('FILES','debugFilePath')
    logFile=configParser.get('FILES','logFile')
    inputPathAuthorsIDs=configParser.get('FILES','inputPathAuthorsIDs')
    inputPathPubsIDs=configParser.get('FILES','inputPathPubsIDs')
    MY_API_KEY=configParser.get('API_KEY','MY_API_KEY')
    tecAffiliations = configParser.get('VARIABLES','tecAffiliations').split(";")
    affiliationID=configParser.get('VARIABLES','affiliationID')
    yearFromStr=configParser.get('VARIABLES','yearFromStr')
    yearToStr=configParser.get('VARIABLES','yearToStr')
    frameSizeStr=configParser.get('VARIABLES','frameSizeStr')

    return

##############################################################################################
# Description: 
# Input: 
# Output: 
##############################################################################################    
    
if __name__ == "__main__":
    
    userInterface()