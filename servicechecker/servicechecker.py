#coding:UTF-8
__author__ = 'riros@ya.ru'

'''
Мультипоточные тестировщик доступности сервиса api-xml

pip install requests
or
easy_install requests
'''
from requests import get
import smtplib
import logging
import socket
import time
import multiprocessing
import os

class config:
    sender = 'riros@ya.ru'
    smtpserver= "smtp.ya.ru"
    sender_pass = '#######'
    sender_user ="riros"
    logfile = "servicechecker.log"
    logformat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    roots = ["ivanvalenkov@gmail.com"] #все системные сообщения

    works = [
        {
            "type":"http",
            "receivers" :["ivanvalenkov@gmail.com"], # можно сделать подобие юнитеста и для каждого сервиса свои адресаты-разработчики
            "name":"ya_ru",
            "server":"ya.ru",
            "url":r'http://ya.ru',
            "response_timeout":45, #todo
            "repeat_delay":60,
            "error_action":"logandwait"
            },
        {
            "type":"http",
            "receivers" :["ivanvalenkov@gmail.com"], # можно сделать подобие юнитеста и для каждого сервиса свои адресаты-разработчики
            "name":"api-xml",
            "server":"dev.1linegroup.com",
            "url":r'http://dev.1linegroup.com/api-xml?<request>ping</request>',
            "response_timeout":45, #todo
            "repeat_delay":60,
            "error_action":"sendmail"# при каждом чихе будет отсылать письмо
            },
    ]
    
def sendmail(work,logger,message):
    try:
        obj = smtplib.SMTP(config.smtpserver)
        obj.login(config.sender_user,config.sender_pass)
        for recv in work["receivers"]:
            m = "Subject: ServiceChecker\r\n\r\n on %s:%s \n\r %s" %(socket.gethostname(),socket.gethostbyname_ex(socket.gethostname())[2],message)
            obj.sendmail(config.sender,[recv],m)
            logger.info("email to " + recv+" sending Message:"+message)
        obj.close()
    except :
        logger.error("exception in send mail to " + recv +" Message:"+message)
        return

def do(work,init = False):
    EmailSended = False
    try:
        logger = logging.getLogger(work["name"])
        logger.setLevel(logging.DEBUG)
        if not init:
            #fh = logging.FileHandler(work["name"]+".log")
            fh = logging.FileHandler("workers.log")
            formatter = logging.Formatter(config.logformat)
            fh.setFormatter(formatter)
            logger.addHandler(fh)


        #logger.setLevel(logging.DEBUG)
        logger.info("start")
    except:
        print ("Exceptino in logging system. IO Error")
        sendmail(work,logger,"Exceptino in logging system. IO Error")
        return True
    while True:
        if not os.path.exists("process"):
            logger.info("stop")
            return False # нормальное завершение

        if work["type"]=="http":
            try:
                resp = get(work["url"])
                if resp.status_code == 200:
                    logger.debug("test OK - "+"time to response:"+str(resp.elapsed))
                    if EmailSended and work["error_action"] == "sendmail":
                        sendmail(work,logger,"service '%s'"%work["name"]+" restored")
                        EmailSended = False
                    if init:
                        return False
                else:
                    logger.error("response code:"+resp.status_code)
                    if not EmailSended:
                        if work["error_action"] == "sendmail":
                            sendmail(work,logger,"response code:"+resp.status_code)
                        EmailSended = True
                    if init:
                        return True
                resp.close()
            except :
                print ("Exception in do('%s')"%work["name"])
                logger.error("Exception in do('%s')"%work["name"])
                if not EmailSended:
                    if work["error_action"] == "sendmail":
                        sendmail(work,logger,"Exception in do('%s')"%work["name"])
                    EmailSended = True
                if init:
                    return True

        time.sleep(work["repeat_delay"])
        #break

def init(rootlog):
    rootlog.info("init...")
    #check smtp service
    rootlog.info("check smtp service")
    try:
        obj = smtplib.SMTP(config.smtpserver)
        obj.login(config.sender_user,config.sender_pass)
        obj.close()
        rootlog.info("done")
    except :
        rootlog.error("Except smtp service")
        print ("except smtp service")
        raise

    for work in config.works:
        err = do(work,True)
        if err:
            rootlog.error("init fail in:"+work["name"])
            print ("INIT FAIL!")
            return False
    rootlog.info("init done.")
    return True

def main():
    rootlog = logging.getLogger("")
    rootlog.setLevel(logging.DEBUG)
    fh = logging.FileHandler(config.logfile)
    formatter = logging.Formatter(config.logformat)
    fh.setFormatter(formatter)
    rootlog.addHandler(fh)
    rootlog.info("================================================================================")
    rootlog.info("start")
    if init(rootlog):
        rootlog.info("sending emails to roots")
        try:
                obj = smtplib.SMTP(config.smtpserver)
                errcode,smtp_server_message = obj.login(config.sender_user,config.sender_pass)
                for recv in config.roots:
                    obj.sendmail(config.sender,[recv],"Subject: ServiceChecker\r\n\r\n service started on server %s"%socket.gethostbyname_ex(socket.gethostname())[2])
                obj.close()
        except:
            rootlog.error("sending email message:service started")
        rootlog.info("done")
        rootlog.info("spawn workers...")

        if not os.path.exists("process"):
            f =  open("process",'wb')
            f.write(bytes("1",'utf-8'))
            f.close()

        print ("works:"+str(len(config.works)))
        # а вот тут магия! ;)
        p = multiprocessing.Pool(len(config.works))
        p.map(do,config.works)

    rootlog.info("stop")
    rootlog.info("---------------------------------------------------------------------------------------------")
    print ("exit")

if __name__ == "__main__":
    main()
