# -*- coding: UTF-8 -*-
import pyodbc,datetime,string,re,math,os

from  multiprocessing import Pool
import multiprocessing

#from bs4 import BeautifulStoneSoup,Tag
import urllib

import pymongo,pymongo.collection

import json,xmltodict

#ebug = True

#obj = objectify.fromstring("<Book><price>1.50</price><author>W. Shakespeare</author></Book>")
#print (objJSONEncoder().encode(obj))

#def log(string):
#    if ebug==True:
#        print (string)



def Connect():
    client = pymongo.MongoClient('localhost',27017)
    return client

def xfind(dir,xexts):
    """

    :param dir: "/path/to/dir"
    :return: ['/dsfsdf/file.sln','/eeee/file.ext']
    """
    dirs = []
    files = []
    #dir = dir.replace("\\",r"/")
    for dirname, dirnames, filenames in os.walk(dir):
        dirs.append(dirname)
        for subdirname in dirnames:
            dirs.append(os.path.join(dirname, subdirname))
        for filename in filenames:
            fn,ext =(os.path.splitext(filename))
            if ext in xexts:
                files.append(os.path.join(dirname, filename))
    return files


def GetMatch(match):
    # возвращает строку из группы совпадений в поиске
    if (match):
        return match.groups(0)[0]
    return ""

def Insert_intodb(collection, obj):
    if collection.save(obj):
        return True
    else:
        return False

def in_db_to_json(collection,obj,odate):
    if (obj):
        obj.update(odate)
        #DBINSERT
        Insert_intodb(collection, obj)
        #convdatetime = obj["datetime"]
        #obj["datetime"] = convdatetime.isoformat()
        #obj.pop('_id')
        #ret = json.dumps(obj).replace("\"@","\"").replace('\'@','\'')
        #return ret
        return
    else:
        return

def xloader(f):

    pf = open(f,'r')
    lines = pf.readlines()
    pf.close()

    collection =  pymongo.collection
    client = Connect()
    db = client.api
    collection = db.rows

    for line in lines:
        l = line.decode("cp1251")
        #print l
        patternrequest = re.compile('.+(<request.+</request>).+')
        patternresponse = re.compile('.+(<response.+</response>).+')
        rowdatetime     = re.compile ('(\w{2})\.(\w{2})\.(\w{4}) (\w{2}):(\w{2}):(\w{2}).+')

        match = patternrequest.match(l)
        req = GetMatch(match)
        match = patternresponse.match(l)
        resp = GetMatch(match)
        match =   rowdatetime.match(l)
        if match:
            d = match.groups()

        if len(d)>0:

            odate=(
                {"datetime":
                     datetime.datetime(
                         int(d[2]),
                         int(d[1]),
                         int(d[0]),
                         int(d[3]),
                         int(d[4]),
                         int(d[5])
                     )
                }
            )
            oreq = {}
            if req:
                FixUUID(req)
                try:
                    oreq = xmltodict.parse(req)
                except:
                    req = req.replace("_EQUALLY_","=")
                    try:
                        oreq = xmltodict.parse(req)
                    except:
                        print "Parse Error: ", req
            oresp = {}
            if resp:
                FixUUID(resp)
                try:
                    oresp=xmltodict.parse(resp)
                except:
                    try:
                        s = resp.replace("_EQUALLY_","=").replace("<=0","&lt;0").replace("< 0","&lt;0")
                        oresp = xmltodict.parse(s)
                    except:
                        print "Parse Error: ",s

            if oreq:
                if oresp:
                    oreq.update(oresp)
                in_db_to_json(collection,oreq,odate)
            else:
                if oresp:
                    in_db_to_json(collection,oresp,odate)
                    #print json.dumps(oreq)

        else:
            print "no datetime in string...."
    client.close()

def FixUUID(str_param):
    seach_uuid = re.search("(\{\w{8}-\w{4}-\w{4}-\w{4}-\w{12}\})",str_param)
    if seach_uuid:
        for search_uuid_elem in seach_uuid.groups():
            search_uuid_elem_mod = search_uuid_elem.replace("{","").replace("}","")
            str_param= str_param.replace(search_uuid_elem[0],search_uuid_elem_mod)
    return str_param

def Main():
    files = xfind('./load',['.log'])


    #MULTIPROCESSING
    p = Pool(multiprocessing.cpu_count())
    p.map(xloader,files)
    #for f in files:
    #    xloader(f)


if __name__ == "__main__":
        Main()
