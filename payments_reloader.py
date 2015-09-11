# -*- coding: UTF-8 -*-

# Перезагружает платежи из логов  

import pyodbc,datetime,string,re,math
from BeautifulSoup import BeautifulStoneSoup,Tag
import urllib2
import pymongo

def GetMatch(match):
    # возвращает строку из группы совпадений в поиске
    if (match):
        return match.groups(0)[0]
    return ""

def repl(string):
    for i in [("  ",""),(" ",""),(u"?",u""),(",.","."),(",","."),("/","."),("..",".")]:
        string = string.replace(i)
    return string

def log(string):
    if ebug==True:
        print (string)

ebug = True
string = ()
#params = [("localhost,1438","UCCS-CIty"),]

years = [""]
period_ids = []
billcount = 0
cnt =0

for i in xrange(154,160):
    period_ids.append((i,))
#print period_ids

#for param in params:
    #cnctstr = ('DRIVER={SQL Server};SERVER=%s;DATABASE=%s;UID=****;PWD=****')%(param)
    #print cnctstr
    #cnxn = pyodbc.connect(cnctstr)
    #cursor = cnxn.cursor()
    #print ("connected")

f = open("load.log",'r')
lines = f.readlines()

patternrequest = re.compile('.+(<request.+</request>).+')
patternresponse = re.compile('.+(<response.+</response>).+')
rowdatetime     = re.compile ('.+(\w{2})\.(\w{2})\.(\w{4}) (\w{2}):(\w{2}):(\w{2}).+')

urlkgg = "http://dc-kgg.1linegroup.com/api-xml?xmlString="
urldc = "http://dc.1linegroup.com/api-xml?xmlString="

for l in lines:

    timematch = rowdatetime.match(l)
    if timematch:
        reqdate = timematch.groups(0)

    match = patternrequest.match(l)
    req = GetMatch(match)
    if req:
        l=l.replace("<billing_devices />","")
        bxml = BeautifulStoneSoup(l)
        if bxml.request["cmd"] =="MAKE_PAYMENT":
            l= req
            #print l
            if bxml.request.company_id.renderContents() == "KGG":
                url = urlkgg
            else:
                url = urldc

            out = reqdate[0]+"."+reqdate[1]+"  "\
                  + bxml.request.company_id.renderContents() + ":" \
                  + bxml.request.account.renderContents() + ":"\
                  + bxml.request.document.renderContents() + ":"\



            print out

            #print url+l
            #eurl = url+urllib2.quote(l)
            #httpc = urllib2.urlopen(eurl)
            #httpr = httpc.read()
            #print httpr
            #httpc.close()

    #cnxn.close()

"""
        spl_s = line.split("<request")
        if len(spl_s) > 1:
            xmls = spl_s[-1]
            if xmls[0]== '"':
                xmls = xmls.replace('"',"")
            print xmls
            xmls=xmls.replace("<billing_devices />","")
            bxml = BeautifulStoneSoup(xmls)

            if bxml.xml.request["cmd"]=="RENT_MAKEPAY" \
                and not bxml.xml.request.account.renderContents()in ('555000002667'):
                docid = bxml.xml.partner_tid.renderContents()
            print docid
"""


"""

                cnt = cnt+1
                #67155937-ba8a-42c0-9b39-243e94e4287f cash = CF73E146-7E8D-49FB-AC62-3759C6EC8326 ????????????2
                #816ba550-b1d4-4da2-9c69-41e1b3238fb5 cash = 00E4C589-C8E7-45E6-83E1-280F6D1867E3 krayinvest
                #{1403F323-B877-41D8-92C7-AAEFF5AF70D6} cash = 6B3475CC-CC93-44F0-B961-C86009E33B33 CFT
                if bxml.xml.request.partner.renderContents() == "67155937-ba8a-42c0-9b39-243e94e4287f":
                    ucash = "CF73E146-7E8D-49FB-AC62-3759C6EC8326"
                if bxml.xml.request.partner.renderContents() == "816ba550-b1d4-4da2-9c69-41e1b3238fb5":
                    ucash = "00E4C589-C8E7-45E6-83E1-280F6D1867E3"
                if bxml.xml.request.partner.renderContents() == "{1403F323-B877-41D8-92C7-AAEFF5AF70D6}":
                    ucash = "6B3475CC-CC93-44F0-B961-C86009E33B33"

                tag = Tag(bxml,"cash")
                tag.insert(0,ucash)
                bxml.xml.request.insert(0,tag)
                BDdel = bxml.xml.request.billing_devices
                if BDdel:
                    BDdel.extract()
                #print bxml.request.cash
                #cashtag = BeautifulStoneSoup.string

                sql = ''' SELECT  DocumentId
                            FROM   dbo.data_receipts
                            where  documentid = '%s' '''%(docid)

                cursor.execute(sql)
                cursor.commit()
                dbdata = cursor.fetchall()
                if len(dbdata)== 0:
                    #replay payment
                    print "replay...",# bxml,

                    print bxml.xml.request.account.renderContents(),
                    ptid = bxml.xml.request.partner_tid
                    if ptid :
                        print ptid.renderContents()
                    eurl = "http://localhost/terminal_v2?xmlString="+urllib2.quote(str(bxml))
                    #print eurl,
                    httpc = urllib2.urlopen(eurl)

                    httpr = httpc.read()
                    #print httpr
                    httpc.close()
                    #if cnt > 0:
                    #    exit(0)

                else:
                    print line[:20],"skip.."
#                    print len(dbdata),bxml.xml.partner_tid.renderContents(),"skip.."
    """
"""
                if bxml.xml.request["cmd"]=="PAYMENT_ORDER_REGISTER":
                    ppnum = bxml.xml.request.payment_order.renderContents()
                    ppdate= bxml.xml.request.date.renderContents()
                    print
                    print "Дата ПП:",ppdate

                    sql = ''' SELECT  id,datetime
                                FROM   dbo.payment_order
                                where  name = '%s'
                                 order by datetime desc'''%(ppnum)
                    cursor.execute(sql)
                    dbdata = cursor.fetchall()
                    cursor.commit()

                    if len(dbdata)> 0:
                        #ppid = dbdata.id
                        ppid =  dbdata[0][0]
                        log( ppid+ppnum+ "ПП в базе ============Проверяем платежи указанные в ПП=====================")
                        for pay in bxml.xml.request.payments.findAll("payment"):
                            #pdate =  pay.date.renderContents()
                            pacc = pay.account.renderContents()
                            pdoc = pay.document.renderContents()

                            sql = ''' SELECT  DocumentId,id_payment
                                        FROM   dbo.data_receipts
                                        where  documentid = '%s' '''%(pdoc)

                            cursor.execute(sql)
                            dbdata = cursor.fetchall()
                            cursor.commit()

                            if len(dbdata)> 0:
                                #print "DOC", pdoc ,"Present!",
                                #print dbdata
                                dbrow = dbdata[0]
                                if dbrow.id_payment =="00000000-0000-0000-0000-000000000000":

                                    log(str(dbrow.DocumentId)+" платежа нет в ПП: "+ppid+ " ДОБАВЛЯЕМ!")
                                    sql = ''' update dbo.data_receipts
                                    set id_payment='%s'
                                    where  documentid = '%s' '''%(ppid, pdoc)

                                    cursor.execute(sql)
                                    #dbdata = cursor.fetchall()
                                    cursor.commit()
                                    #print sql
                                    #exit(0)

                                    #for dbrow in dbdata:

                                    #    print dbrow.DocumentId,dbrow.id_payment
                                        #if dbrow.id_payment == ppid:
                                else:
                                    log(str(dbrow.DocumentId) + " платеж уже привязан к ПП" + str(dbrow.id_payment))
                            else:
                                log( "Платежа "+ pdoc +"нет в базе!")
                    else:
                        log( "ПП "+ppnum+"НЕТ В БАЗЕ!!!")
                        #TODO: Автоматическое добавление ПП В базу с Привязкой платежей.

                        """


