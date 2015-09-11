# -*- coding: CP1251 -*-
import pyodbc,datetime,string,re

def repl(string):
    ret = string
    ret = ret.replace("  ","").replace(" ","").replace(u"г",u"").replace(",.",".").replace(",",".").replace("/",".").replace ("..",".")
    return ret


params = [("localhost,1436","***")]


for param in params:
    cnxn = pyodbc.connect(('DRIVER={SQL Server};SERVER=%s;DATABASE=%s;UID=****;PWD=****')%(param))
    cursor = cnxn.cursor()

    sql = '''
    SELECT 
        s.name
        ,dsp.name
        ,s.value
        ,d.name
        
    FROM
        supplemental_params s
    left JOIN
        [uccskernel].dbo.dependence d
    ON
        d.id = s.useruid
    JOIN
        dir_supplemental_params dsp
    ON
        dsp.id = s.param
    WHERE
        (dsp.id_type = '3' and not(s.value =''))
        and(
        s.value like '__.%.%'
        or
        s.value like '__,%,%'
        )
        '''
    sql_update = '''
    update supplemental_params
    set 
    value = '%s'
    where
    name = '%s' and value = '%s'
    '''
    sql_delete ='''
    delete from supplemental_params
    where
    name = '%s' and value = '%s'
    '''

    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.commit()
    cursor.close()
    i = 0
    for row in rows:
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
    cnxn.close()
            
        
