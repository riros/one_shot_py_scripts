__author__ = 'riros'
# -*- coding: UTF-8 -*-

# многопоточный рефаторинг кода прокета на C++, После которого проект был сокращен на 10000 строк
#

import pyodbc,datetime,string,re,math,os

from  multiprocessing import Pool
import multiprocessing

def xfind(dir,xexts):
    """

    :param dir: "/path/to/dir"
    :return: ['/dsfsdf/file.sln','/eeee/file.ext']
    """
    dirs = []
    files = []
    #dir = dir.replace("\\",r"/")
    for dirname, dirnames, filenames in os.walk(dir):
        #dirs.append(dirname)
        #for subdirname in dirnames:
        #    dirs.append(os.path.join(dirname, subdirname))

        for filename in filenames:
            fn,ext =(os.path.splitext(filename))
            if ext in xexts:
                files.append(os.path.join(dirname, filename))
    return files


def GetMatch(match):
    # возвращает строку из группы совпадений в поиске
    if (match):
        return match.groups(0)
    return ""
def xloader(f):
    l=''
    if (f==r'c:\inetpub\cpp\UCCS\PASP\PASP.RegistrationManager\UCCSIsapi.cpp'):
        pass
    ret = 0
    pf = open(f,'r')
    lines = pf.read()
    pf.close()
    try:
        l = lines.decode("cp1251")
    except:
        try:
            l = lines.decode("utf-8")
        except:
            print 'критическая ошибка преобразования файла ',
            print f



    pattern = re.compile('\n*(\s*val\w*\s*=\s*\w+->Fields->Item\[_variant_t\([\"]*\w+[\"]*\)\]->Value;\s*.*[\(\);]*\s*if\s*\(\s*val\w*\.vt\s*!=\s*[\(]*VT_NULL[\)]*\)\s*\w+.Format\(\"%s\",\s*\(char\*\)\s*_bstr_t\(\s*val\w*\)\);[ \n\t]*\n[ \t]*)')
    pattern2 = re.compile('\n*(\s*)val\w*\s*=\s*(\w+)->Fields->Item\[_variant_t\(([\"]*\w+[\"]*)\)\]->Value;\s*.*[\(\);]*\s*if\s*\(\s*val\w*.vt\s*!=\s*[\(]*VT_NULL[\)]*\)\s*(\w+).Format\(\"%s\",\s*\(char\*\)\s*_bstr_t\(\s*val\w*\)\);[ \n\t]*\n([ \t]*)')

    search =  pattern.findall(l)
 #   tests = test.findall(l)
    if len(search) > 0:#and  len(tests)> 0:
        ret =  len (search)#, len(tests)
        print "proc:",f
        out = "".join(l)
        for repl in search:
            param = pattern2.findall(repl)
            #print "repl : ",repl
            #print "param:",param
            out = out.replace(repl,param[0][0]+param[0][3]+" = RS2STR("+param[0][1]+","+param[0][2]+");"+"\n"+param[0][4])
#            out = out.replace("val1;","val;")
#            out = out.replace("val2;","val;")
#            out = out.replace("CComVariant val, val;","CComVariant val;")
            #out = out.replace("CComVariant val;","")
        try:
            out = out.encode('cp1251')
        except:
            out = out.encode('utf8')

        ofile = open (f,'w')
        ofile.write(out)
        ofile.close
        #exit(0)
    return ret

def Main():
    files = xfind(r'c:\inetpub\cpp',['.cpp'])
    print len(files)
    debug = True
    c = 0
    t = 0
    #MULTIPROCESSING
    if debug or __debug__:
        for f in files:
            c = c+ xloader(f)
        print "files:", len(files)
    print "replaces:",c
#    else:
#        p = Pool(multiprocessing.cpu_count())
#        p.map(xloader,files)

if __name__ == "__main__":
    Main()


