#!/usr/bin/env python
#coding:UTF-8
""" 
Автор: riros

RTTY log parser 

Работает параллельно с программой RTTY, которая пишет оповещение из звуковой карты в лог файл.
Читает лог файл и декодирует информацию для считывающего.
Оповещает при нарушениях границы звуковым сигналом.
Отфильтровывает помехи и ошибки оповещения.
Учитывает смену года и часовые пояса.

2011 г.

"""
import re,os,time
import datetime,play
#--------------------------------------------

#TODO: read initialization from db
def ini(s,cmd,d):
    ret = ''
    out_ini_lines=[]
    
    fini=open('/home/riros/work/config.cfg','r')
    ini_lines_data = fini.read()
    ini_lines=ini_lines_data.split("\n")
    fini.close()

    if cmd == 'r':
        for ini in ini_lines:
            ini_spl=ini.split(':')
            if len(ini_spl)>=2 :
                if ini_spl[0] == s:
                    ret = ini_spl[1]
    elif cmd == 'w':
        for ini in ini_lines:
            ini_spl=ini.split(':')
            if len(ini_spl)>1:
                if ini_spl[0] == s:
                    ini_spl[1]=d
                out_ini_lines+= [str(ini_spl[0]+":"+str(ini_spl[1])+"\n")]
        fini=open('/home/riros/work/config.cfg','w')
        fini.writelines(out_ini_lines)
        fini.close()
    return ret
#-------------------------------------------------

def log_get(name,f_cursor): # name = имя файла f_cursor = позиция считывания в файле
    
    datetime_pos = datetime.datetime.now() # позиция во времени для считывания
    tz_delta=datetime.timedelta(hours=0) # зависит от настройки системы, если указан часовой пояс и место положение,
                                        #то необходимо учесть, что в логе gmfsk используется время относительно гринвича
    buff=[] # временный коллектор сообщений
    sz_data = os.path.getsize(name) # размер файла лога
    if f_cursor > sz_data :
        print "warning! размер файла %s меньше ожидаемого. %s<%s"%(name,sz_data,f_cursor)
    zmsg = [0,0,0,0,0,0,0, 0,0,0,0,0] ##буффер сохраняемых сообщений : цели, характеристики, выходы

    mtch=[] # буффер поиска
    ret = () # возвращаемое функцией

    dt          = datetime_pos.replace(second=0,microsecond=0) #время цели при считывании 
    #!!!! Учет разницы в часовых поясах!!!!
    et          = datetime.timedelta() # разница во времени сохраненном и только что считанном...
    err_t       = datetime.timedelta(minutes=10) # допустимая ошибка при асинхронной передачи целей в оповещении
    hour        = datetime.timedelta(hours=1)
    day         = datetime.timedelta(days=1)
    
        # вытащить дату-время
        # начать добавлять в текущее.. если текущее больше считанного то +1 час
        # формат сообщения [datetime,тип сообщения,номер цели,сектор\индекс,м-кв\высота,мк-кв\скорость]
        #			[2011,2,16,1,56,34,55555,1,8888,800,32,21]
        #			[2011,2,16,1,56,34,55577,2,9999,501,32,12]
        #			[2011,2,16,1,56,34,55598,4,0000,0,0,0]
   
#    print ("get:%s"%(name)), "length:",sz_data,'b', "position:",f_cursor
    f = open (name,'rb')
    f.seek (f_cursor)
    new_data = f.read()
    f.close()

    nslines = new_data.split("\n") # разделяем строки
    for s in nslines:
        spl_s_vv = s.split("VV")
        for ss in spl_s_vv:
            spl_ss= ss.split("==")
            if len(spl_ss)> 1:
                for sss in spl_ss:
                    buff+=[sss]
            else:   
                buff+=spl_ss

    #=============== TODO: загружать pattern из отдельного файла
                # Если в структуре оповещения что-либо изменилось, то править это:
    time_pattern        = re.compile('[=V]?99([0-2][0-9][0-6][0-9]).+')
    target_pattern      = re.compile('[=V]?1(\d{4})(\d{3})(\d{2})(\d{2})([0-6]\d).+')
    targetprm_pattern   = re.compile('[=V]?2(\d{4})(\d{3})([01239]\d)?([01239]\d)?(\d{2})?.+')
    datetime_pattern    = re.compile('RX \((\d{4})-(\d{2})-(\d{2}) (\d{2}:\d{2}).+')
    targetout_pattern   = re.compile('[=V]?4(\d{4})(\d{4}).+')
    
#    print 'dt=',str(dt)
    n = 0           #число сообщений
    err_count = 0   #количество ошибок
    target_count=0  #количество сообщений координат целей
    param_count = 0 #количество сообщений с параметрами

#=======================================================================
#начинаем разбирать кашу сообщений для генерации выходящего форматированного сообщения zmsg
    for i in buff:
        n+=1
        msg= str(i)
        zmsg=[]
#        print msg,">>>>\t",

#=-==============================================================
        if time_pattern.match(msg):
            # время
            mtch = time_pattern.match(msg).groups()
#            print "time_pattern:",str(mtch),"dt:",dt

            #et
            if len(mtch[0])== 4:
                t1 = datetime.timedelta(hours=int(mtch[0][0:2]),minutes=int(mtch[0][2:4]))
                t2 = datetime.timedelta(hours=dt.time().hour,minutes=dt.time().minute)
                et= (t1-t2)
                et_abs = abs(et)
                if (datetime.timedelta(minutes=int(mtch[0][2:4])) < hour):
                    if (t1 < t2):
                        if et_abs < err_t: # разница во времени в пределах допустимой
                            dt = dt - et_abs ## время сообщения меньше и в пределах диапазона
                        else:
                            if (et_abs) > (day-err_t):
                                dt = dt+(day-et_abs)
                            else:
                                 err_count+=1
                                 #print "\terror! ignore next day:", msg

                    else:
                        if et_abs < err_t: 
                            dt = dt + et_abs 
                        else:
                            if et_abs > (day-err_t):
                                dt = dt-(day-et_abs)
                            else:
                                #print "\terror! ignore message:", msg
                                err_count+=1
                else:
                    print "\terror! target time out of range.  ignore message:", msg
                    err_count+=1
                           
# ==================================================================                
        elif target_pattern.match(msg):
            target_count+=1
            # target pos 1_2832_008_51_75_00_*
            # VV991127++8++++++)VV_1_0826 196 86 87 27 *
            # цели могут быть и в предыдущем дне.
            mtch= target_pattern.match(msg).groups()
#            print "target_pattern:",str(target_pattern.match(msg).groups())
            t1 = datetime.timedelta(minutes=int(mtch[4]))
            t2 = datetime.timedelta(minutes=dt.time().minute)
            et= (t1-t2)
            et_abs = abs(et)
            if (datetime.timedelta(minutes=int(mtch[4])) < hour):
                if (t1 < t2):
                    if et_abs < err_t:
                        dt = dt - et_abs
                        zmsg=[
                            str(dt.year),str(dt.month),str(dt.day),str(dt.hour),
                            str(dt.minute),str(dt.second),str(dt.microsecond),
                            1,
                            str(mtch[0]),str(mtch[1]),str(mtch[2]),str(mtch[3])
                            ]
                    else:
                        if et_abs > (hour - err_t):
                            dt = dt + (hour-et_abs) ## next hour
                            zmsg=[
                                str(dt.year),str(dt.month),str(dt.day),str(dt.hour),
                                str(dt.minute),str(dt.second),str(dt.microsecond),
                                1,
                                str(mtch[0]),str(mtch[1]),str(mtch[2]),str(mtch[3])
                                ]
                        else:
                            #print "\terror! ignore next hour:", msg
                            err_count+=1
                else:
                    if et_abs < err_t:
                        dt = dt + et_abs
                        zmsg=[
                            str(dt.year),str(dt.month),str(dt.day),str(dt.hour),
                            str(dt.minute),str(dt.second),str(dt.microsecond),
                            1,
                            str(mtch[0]),str(mtch[1]),str(mtch[2]),str(mtch[3])
                            ]
                    else:
                        if et_abs > (hour-err_t):
                            dt = dt - (hour-et_abs)
                            zmsg=[
                                str(dt.year),str(dt.month),str(dt.day),str(dt.hour),
                                str(dt.minute),str(dt.second),str(dt.microsecond),
                                1,
                                str(mtch[0]),str(mtch[1]),str(mtch[2]),str(mtch[3])
                                ]
                        else:
                            #print "\terror! ignore target message:", msg
                            err_count+=1

#========================================================================
        elif targetprm_pattern.match(msg):
            mtch= targetprm_pattern.match(msg).groups()
            #print "targetprm_pattern:",str(mtch),msg,dt
            zmsg=[
                str(dt.year),str(dt.month),str(dt.day),str(dt.hour),
                str(dt.minute),str(dt.second),str(dt.microsecond),
                2,
                str(mtch[0]),str(mtch[1]),str(mtch[2]),str(mtch[3])
                ]
#            if debug :print "targetprm_pattern:",str(targetprm_pattern.match(msg).groups())
#==================================================================
        elif datetime_pattern.match(msg):
            mtch= datetime_pattern.match(msg).groups()
#            print "datetime_pattern:",str(mtch)

            tmp = mtch[3].split(":")
            dt = dt.replace(
                year    = int(mtch[0]),
                month   = int(mtch[1]),
                day     = int(mtch[2]),
                hour    = int(tmp[0]),
                minute  = int(tmp[1])
                )
            dt= dt + tz_delta ### Учет часового пояса + 3
#            print "dt=",dt
#==========================================================================
        elif targetout_pattern.match(msg):
            # target out
            mtch= targetout_pattern.match(msg).groups()
            #print "targetout_pattern:",str(mtch),msg,dt
            zmsg=[
                str(dt.year),str(dt.month),str(dt.day),str(dt.hour),
                str(dt.minute),str(dt.second),str(dt.microsecond),
                4,
                str(mtch[0]),str(mtch[1]),None,None
                ]
#            print "targetout_pattern:",str(targetout_pattern.match(msg).groups())
#------------------------------------------------------------------------------
        else:
            # unknown message
            if n==len(buff):
                #print 'last unknown message:',msg
#                print 'sz_data=',sz_data,'sz_data-len(msg)=',sz_data-len(msg)
                sz_data=sz_data-len(msg)
            #continue
#===============================================================================
#        print dt,'\t <<',msg
        if zmsg!=[] :
            ret+=zmsg,
            #print 'datetime_delta:',datetime_delta
#    print 'end=',str(n), 'errors:',err_count,'targets:',target_count
    return ret,sz_data,dt
#=========================================================================
def main():
   
   #---- READ LOG FILE-------------------
    target_collector=set([]) # хранит текущие цели на оповещении
    param_collector=set([]) # хранит номера целей с характеристиками
    sectors = set([902,900,470,909,908,474]) # разрешенные секторы, !!! ПРАВИТЬ, ЕСЛИ ИЗМЕНИЛИСЬ
    warn_param = set([7,6,3,4,8]) # индексы принадлежности с свуковым сигналом

    target_lastseen=[] # сохраним время последней засечки для цели в секундах с нулевого времени.
    for i in range(9999):
        target_lastseen.append(0)

    timesleep = 20
    #delta_10 = datetime.timedelta(minutes=10)
    loops = 1
    delay = True
    '''
        if (datetime_now - datetime_pos) < delta_10:
            print datetime_now , '  ' , datetime_pos , delta_10    
            delay = True
        else: delay = False
    '''
    while loops:
        datetime_now= datetime.datetime.now()
        f_cursor = ini("cursor",'r',0) ## read position from ini file
        if f_cursor !='' :
            mesh,sz,datetime_pos = log_get("/home/riros/gMFSK.log",int(f_cursor))
        else :
            mesh,sz,datetime_pos = log_get("/home/riros/gMFSK.log",0)
        ini("cursor",'w',sz) # sz

        for i in mesh:
            #print i
            loops+=1
            mtype=i[7]

            tmptimestamp = datetime.datetime(year=int(i[0]),month=int(i[1]),day=int(i[2]),hour=int(i[3]),minute=int(i[4]))-datetime.datetime.fromordinal(1)
            timestamp = tmptimestamp.days*86400+tmptimestamp.seconds
            if mtype==1:
                if i[8] in target_collector:
                    print '%003d %0004d'%(loops,int(i[8])),i[9],i[10],i[11],'за',"%02d:%02d"%(int(i[3]),int(i[4]))
                else:
                    print '%003d*%0004d'%(loops,int(i[8])),i[9],i[10],i[11],'за',"%02d:%02d"%(int(i[3]),int(i[4]))
                    target_collector.add(i[8])
                target_lastseen[int(i[8])]=timestamp
    #           if delay: time.sleep(9)

            elif mtype==2:
    #    	    print int(i[9][0]), int(i[8])
                if int(i[9][0]) in warn_param:
                    print '%003d'%(loops),'характеристика ',i[8],i[9],'%0.2s %0.2s'%(i[10],i[11]), '<<<<<<<'
                    if not (i[8] in param_collector):
                        if delay: play.play('/home/riros/work/voice/ringout.wav')
                        param_collector.add(i[8])
                        timesleep=5
                else:
                    print '%003d'%(loops),'характеристика ',i[8],i[9],'%0.2s %0.2s'%(i[10],i[11])
                    if not (i[8] in param_collector):
                        param_collector.add(i[8])
                        #if delay: time.sleep(10)   		    
                    
            elif mtype==4:
                if i[8]==i[9]:
                    if i[8] in target_collector:
                        target_collector.remove(i[8])
                    if i[8] in param_collector:    
                        param_collector.remove(i[8])
                    print '%003d'%(loops),i[8],'вышла '
                else:
                    if i[8] in target_collector:
                        target_collector.remove(i[8])
                        if i[8] in param_collector:
                            param_collector.remove(i[8])
                        target_collector.add(i[9])
                        param_collector.add(i[9])
                        print '%003d'%(loops),i[8],'переименована в ',i[9]
                        target_lastseen[int(i[9])]=target_lastseen[int(i[8])]
                    else:
                        if i[9] in target_collector:
                            if i[8] in target_collector:target_collector.remove(i[8])
                            if i[8] in param_collector:param_collector.remove(i[8])
                            print '%003d'%(loops),i[8],'вышла '

                if set([]) == target_collector:
                    print 'на оповещении целей нет'
                    timesleep = 20
                else:
                    # вычищаем невышедшие цели
                    tmp_target_collector_remove = set()
                    for j in target_collector:
                        if timestamp - target_lastseen[int(j)] > 1200:
                            print "цели ",j, "не было ",timestamp - target_lastseen[int(j)],"секунд => удалена"
                            tmp_target_collector_remove.add(j)
                            if j in param_collector:    
                                param_collector.remove(j)
                    target_collector=target_collector - tmp_target_collector_remove
                    if set([]) == target_collector:
                        print 'на оповещении целей нет'
                        timesleep = 20
                    else:
                        print "на оповещении остались: ",
                        for j in target_collector:
                            print j,
                        print
        time.sleep(timesleep)
              
        #----TODO: COMMIT TO DATABASE SQL -------------

if __name__ == '__main__':
        main()
