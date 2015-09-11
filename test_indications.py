# -*- coding: utf8 -*-

# Поиск ошибок и аномалий в показаниях приборов учета

import pyodbc,datetime,string,re,math

def repl(string):
    for i in [("  ",""),(" ",""),(u"�",u""),(",.","."),(",","."),("/","."),("..",".")]:
        string = string.replace(i)
    return string


params = [("localhost,1438","UCCS-City")]
years = [""]
period_ids = []
all_indications = []

for i in xrange(159,160):
    period_ids.append(i)
print (period_ids)

def get_allbd (cur):
    sql = '''
    SELECT DISTINCT 
        e.id
    FROM
        (
            SELECT 
                id
            FROM
                dbo.billing_device
    %s) e
      '''
    arch = ""
    for y in years:
        arch = arch + """
                union all
                        SELECT 
                    id
                FROM dbo.billing_device%s """%(y)
        
    cur.execute(sql%(arch))
    ret = cur.fetchall()
    cur.commit()
    return ret
    

def get_allindications(cur):
    ai = []
    #print "����� ��������� �� %s ���"%(y),len(all_indications)  
    for y in years:
        for period_id in period_ids:    
            sql = '''
                SELECT distinct
                    bd.id bdid,
                    sp.status st,di.*
                FROM
                    dbo.Personal_Accounts%s pa
                    
                left join [TMP-TableForISAPjax] isa
                        on isa.fid = pa.id_object
                left join dbo.[F72ADF02-CFC7-4051-A6B4-1940549C3B84] h 
                    on h.id = isa.hid
                INNER JOIN
                    dbo.[objects_links] ol
                ON
                    ol.obj1_id=pa.id
                INNER JOIN
                    dbo.[sell_points%s] sp
                ON
                    sp.id=ol.obj2_id
                INNER JOIN
                    dbo.[billing_device%s] bd
                ON
                    
                    bd.id=sp.BillingDeviceID
                JOIN
                    dbo.data_Indications%s di
                ON
                    di.BillingDeviceID = bd.id
                    and di.period_id = sp.period_id
                WHERE
                    sp.status ='active' and (di.period_id = %s and sp.period_id = %s)
                    -- and bd.id = 'EA122AD0-0059-413E-B9B3-02077FA3EB44'
                 ORDER BY
                    di.period_id,bd.id,DATETIME,
                    di.First DESC,
                    di.last ASC,
                    di.beginindication,
                    di.endindication
                '''%(y,y,y,y,period_id,period_id)

            #--and isnull(h.controlCompany,'B10BE9C8-CF64-4D4A-90FB-61C376FB0C02') <>'C3DB132A-840E-42EA-AC17-DFD7819E6A65'
            #print sql
            period_indications = cur.execute(sql).fetchall()
            #for i in period_indications:
            #    print i
            #exit

            #cur.commit()
            if len(period_indications)> 0:
                print ("indications:",len(period_indications),period_id,y)
            #if (len(period_indications)>0 ):
            for i in period_indications:
                ai.append(i)
            #print all_indications
            
    return ai


def main():
    for param in params:
        cnctstr = ('DRIVER={SQL Server};SERVER=%s;DATABASE=%s;UID=*****;PWD=****')%(param)
        print (cnctstr)
        cnxn = pyodbc.connect(cnctstr)
        cursor = cnxn.cursor()

        #get billing devices
        print ("fetch bd...")
        bd_ids = get_allbd(cursor)
        #print len(bd_ids)
        cursor.commit()
        # �������� ���� ��������� �� ��� ������� � ���� � ���� ������� �������
        all_indications = get_allindications(cursor)
        i = 0
        print ("all indications:",len (all_indications))

        bd_cnt = len(bd_ids)
        print ("billing devices: ",bd_cnt)
        bd_pos = 0
        
        for bd_id in bd_ids:
            #if bd_id[0] != 'FD40D293-CEDC-4934-9332-126EE2FF4C51':
            #    continue
            #print bd_id

            bd_pos = bd_pos + 1
            indication_present = False
            last_ind = 0
            dindaccum = 0
            #print "    ----- %d of %d    <<<<<<<   bd:%s..."%(bd_pos,bd_cnt,bd_id[0])
            
            for period_id in period_ids:
                indications = []
                for tmp in all_indications:
                    if (tmp.period_id == period_id ) and (tmp.BillingDeviceID == bd_id[0]):
                        indications.append(tmp)
                #print "len(indications)",len(indications)," inperiod",period_id
                
                dindication = 0
                lind = len(indications)
                first = 1
                last = 1

                first_inperiod = True
                ind_pos = 0
                for ind in indications:
                    #if bd_id[0] == '':
                    #    ind_pos = ind_pos+1
                    if first_inperiod:
                        first_inperiod = False
                        first = 1
                        if  (last_ind!=0) and (ind.BeginIndication != last_ind):
                            print (ind.DateTime,ind.AccountID,bd_id[0],period_id,
                            (ind.BeginIndication-last_ind),0,
                            "ind.BeginIndication_!=_commited_indication,_���������_��_������_�������_���_��_���������_���������_��������_�������. ")
                        tmp_end_indication = ind.BeginIndication
                        indication_present = True
                    else:
                        first = 0
                        
                    if ind_pos == lind:
                        last = 1
                        last_ind = ind.EndIndication
                    else:
                        last = 0

                    # ��������� ����������� � ���������� �� ������
                    if (ind.First !=first and ind.Last!=last):
                        print ind.DateTime,ind.AccountID,ind.DocumentId,bd_id[0],period_id,0, "ind.First !=first and ind.Last!=last) "
                    #if ( ind.BeginIndication + ind.TotalIndication != ind.EndIndication):
                        #print ind.DateTime,ind.AccountID,ind.DocumentId,bd_id[0],period_id,0, "ind.BeginIndication_+_ind.TotalIndication_!=_ind.EndIndication) ",ind.BeginIndication, ind.TotalIndication , ind.EndIndication

                    if ind.BeginIndication != tmp_end_indication: # ����� ��������� ������� � ����������
                        delta = ind.BeginIndication-tmp_end_indication
                        if delta > 0:
                            print ind.DateTime,ind.AccountID,ind.DocumentId,bd_id[0],period_id, ind.BeginIndication-tmp_end_indication,"�����_�_����������_���_�������"
                            '''
                            yy = ""
                            if period_id == 158:
                                yy = "_2013"
                            else :
                                yy = ""
                            sql = """UPDATE
                                    data_indications%s
                                SET
                                    BeginIndication=%s,
                                    TotalIndication=%s
                                WHERE
                                    BillingDeviceID = '%s'
                                AND AccountID = '%s'
                                AND period_id = '%s'
                                and DocumentId = '%s' """%(yy,
                                             tmp_end_indication,
                                             ind.BeginIndication - tmp_end_indication,
                                             bd_id[0],
                                             ind.AccountID,
                                             period_id,
                                             ind.DocumentId)
                            print sql 
                                           
                            cursor.execute(sql)
                            cursor.commit()

                            sql = """delete from dbo.data_Charge%s
                                where AccountID = '%s'
                                and period_id = '%s' """%(yy,ind.AccountID,period_id)

                            print sql

                            cursor.execute(sql)
                            cursor.commit()
                            '''
                        #else:
                            #print ind.DateTime,ind.AccountID,ind.DocumentId,bd_id[0],period_id, ind.BeginIndication-tmp_end_indication,"�������������_�������"
                            

                    tmp_end_indication = ind.EndIndication
                    dindaccum = dindaccum + ind.TotalIndication


                dindications = dindaccum
                    
                    
    #---------------------------------------------------------------------
            """
                i = i+1
                s = row[2]
                try:
                    dt = datetime.datetime.strptime(s,"%d.%m.%Y")
                    if (re.match(r"(\d+)\,(\d+).(\d+)",s) or re.match(r"(\d+)\.(\d+),(\d+)",s)):
                        raise Exception()
                except:
                    if (row):
                        s = repl(s)
                        try:
                            dt = datetime.datetime.strptime(s,"%d.%m.%Y")
                            #update 1
                            print i,row[0],"update",row[2]," >> " ,s
                            #sql2 = sql_update % (s,row[0],row[2])
                            #ucursor.execute(sql2)
                            #ucursor.commit()
                        except:
                            s = repl(s)
                            print i,row[0]," delete: ",row[2]
                            #delete
                            #supd = sql_delete % (row[0],row[2])
                            #print "delete: " + supd
                            #ucursor.execute(sql)
                            #ucursor.commit()
        #cursor.commit()
        #cursor.close()
        """
        cnxn.close()
                
if __name__ == "__main__":
    main()            
