__author__ = 'riros'
#coding:UTF-8
# запускает сборку модулей проекта в разных потоках. Так как в старой Visual Studio нет такой возможности.
import os
#import pyodbc
from  multiprocessing import Pool
import multiprocessing
import hashlib
import subprocess

#local
def_setttings = r'''

__author__ = 'riros'

#coding:UTF-8

class ini:
    verbose = True
    deamon = False # повторять с задержкой.
    usekernel = False # не исползьуется.
    BLib_recompileall = False #!!! Очень важный параметр. Перекомпилировать все, если изменились либы
    recompileall = False # В любом случае перекомпилировать все.
    exclude_dir = ["c:\\inetpub\\cpp\\unit.tests"]

    drive = 'C:'
    projpath = r'inetpub'
    apppaths = [r'cpp']
    Libs = [r'C:\inetpub\cpp\LIB\basic_libs\basic_libs.vcproj',
            r'C:\inetpub\cpp\LIB\report\1ls_report_engine.vcproj']

    devtool = r'\Program Files\Microsoft Visual Studio 8\Common7\IDE\devenv.exe'

    # DB-------------

    # PATH

    appprojext = ['.vcproj'] # искать проекты
    srcext =    ['.cpp','.h','.hpp','.c'] # проверять изменяемые файлы
'''
Failed = []

if not os.path.exists("settings.py"):
    f =  open("settings.py",'wb')
    f.write(bytes(def_setttings,'utf-8'))
    f.close()

from settings import *

def getsubs(dir):
# get all
    dirs = []
    files = []
    for dirname, dirnames, filenames in os.walk(dir):
        dirs.append(dirname)
        for subdirname in dirnames:
            dirs.append(os.path.join(dirname, subdirname))
        for filename in filenames:
            files.append(os.path.join(dirname, filename))
    return dirs, files

def xfind(dir,xexts,exclude_dir):
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
            if (ext in xexts):
                btrue = True
                for exclude  in exclude_dir:
                    if (dirname.lower()[:len(exclude)] == exclude):
                        btrue = False
                if btrue :
                    files.append(os.path.join(dirname, filename))
    return files

def check(path ,xexts): # проверяем исходники на изменение в каталоге
    dir = os.path.dirname(path)
    files = []
    if dir ==r"C:\inetpub\cpp\LIB\basic_libs":
        dir = r"C:\inetpub\cpp\LIB"
        #ini.BLIb_changed= True
    #[dirname, dirnames, filenames] = os.walk(path)
    #filenames = []
    for f in os.listdir(dir):
        p = os.path.join(dir,f)
        if os.path.isfile(p):
            #filenames.append(p)
            fn,ext =(os.path.splitext(p))
            if ext in xexts:
                files.append(os.path.join(dir, p))
                #print (os.path.join(os.path.dirname(path), p))
    #---------------------------------------
    #       читаем суммы
    #       проверяем, записываем, компилируем.

    Ghash = hashlib.md5()
    for file in files:
        filehash = hashlib.md5()
        f = open(file,'rb')
        data = f.read()
        f.close()
        filehash.update(data)
        h = filehash.hexdigest()
        Ghash.update(h.encode('utf-8')) # на выходе сумма от сумм всех исходныков

    existspath = os.path.join(dir,'hash')
    if (os.path.exists(existspath)):
        pathtohash =os.path.join(dir,'hash')
        f = open(pathtohash,'rb')
        data = f.read()
        if data==bytes(Ghash.hexdigest(),'utf-8') and not ini.recompileall:
            return False
        else:
            #os.remove(os.path.join(dir,'hash'))
            f = open(os.path.join(dir,'hash'),'wb')
            f.write(bytes(Ghash.hexdigest(),'utf-8'))
            f.close()
            return True # TODO Поправить, записывать хеш только после проверки успешности компиляции.
    else:
        f = open(os.path.join(dir,'hash'),'wb')
        f.write(bytes(Ghash.hexdigest(),'utf-8'))
        f.close()
        return True

def xcompile(path):
    cmd = r'"'+ini.drive+ini.devtool+'" /Rebuild "release" "'+path + '"'
    #print (subprocess.call(cmd+r" /clean"))
    #print ("Execute ",cmd,end=" >>> ")
    if subprocess.call(cmd):
        print ('Fail ',path.replace(ini.drive+"\\"+ini.projpath,"") )
        os.remove(os.path.join(os.path.dirname(path),"hash"))
        #Failed.append(path)
    else:
        if ini.verbose:
            print ("оk" ,path)

def main():
    runpath = (os.getcwd())
    #----------------------------
    #           DBCONNECT

    if ini.usekernel:
        print ("не реализовано еще ")
        #if ini.kernport=="":ini.kernport = "1433"
        #cnctstr = ('DRIVER={SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s')\
        #          %((ini.kernpath+","+ini.kernport,ini.dbname,ini.dbuser,ini.dbkey))
        #print (cnctstr)
        #cnxn = pyodbc.connect(cnctstr)
        #cursor = cnxn.cursor()

    else:
        for apppath in ini.apppaths:
            path = ini.drive +"\\"+ini.projpath+"\\"+apppath
            #dirs,files = getsubs(path)
            projfiles = xfind(path,ini.appprojext,ini.exclude_dir)

            #srcfiles = xfind (path,ini.srcext)
            #print (srcfiles)

    if ini.recompileall:
        print("Задействована принудительная компиляция см settings.py recompileall ")

    #-------------------------------------
    #       проверяем суммы
    projforrecompile = []
    libsforrecompile = []

    #-- сначала билиотеки
    #
    #    if os.path.dirname(path)==r"C:\inetpub\cpp\LIB\basic_libs":
    #        if (ini.BLib_recompileall):
    #            ini.recompileall = True
    #Ошибка	1	fatal error LNK1181: cannot open input file '..\..\..\lib\report\1ls_report_engine.lib'	DisCom.Applet.BarCode

    libs = []
    c = 0
    for i in projfiles:
        if i in ini.Libs:
            libs.append(i)
        c=c+1
    for i in libs:
        projfiles.remove(i)

    for path in libs:
        if check(path,ini.srcext) or ini.recompileall:
            print ("> Перекомпилировать библиотеку! ",end="")
            print (os.path.dirname(path))
            libsforrecompile.append(path)
            if ini.BLib_recompileall:
                ini.recompileall = True
            #else:
            #    print ("> пропускаем ",end=" ")
            #    print (os.path.dirname(path))

    for path in projfiles:
        if check(path,ini.srcext) or ini.recompileall:
            print (">перекомпилировать ",end="")
            print (os.path.dirname(path))
            projforrecompile.append(path)
        #else:
        #    print ("> пропускаем ",end=" ")
        #    print (os.path.dirname(path))
    print ("---------------------------------")
    if not (len(projforrecompile)==0 and len(libsforrecompile)==0):
        if (os.path.exists(ini.devtool)):
            print ("Процессоры:",multiprocessing.cpu_count())
            # ----------------------------------
            #            Красота мультизадачная

            p = Pool(multiprocessing.cpu_count())
            #print (" Перекомпилция библиотек ... ")
            #p.map(xcompile,libsforrecompile)
            if len(libsforrecompile)>0:
                print (" Перекомпиляция библиотек ... ")
            for i in libsforrecompile:
                xcompile(i)

            if len(projforrecompile)>0:
                print ('перекомпиляция проектов ...')
            p.map(xcompile,projforrecompile)

            '''
            print (" Перекомпилция библиотек ... ")
            for i in libsforrecompile:
                xcompile(i)
            print ('перекомпиляция проектов ...')
            for i in projforrecompile:
                xcompile(i)
                '''
            # print ("НЕ скомпилированы:")
            #for i in Failed:
            #    print (i)
    else:
        print ("нечего делать...")
    return

if __name__ == "__main__":
    while 1:
        main()
        if not ini.deamon:
            print ("Окно можно закрыть...")
            #os.system("sleep 120")
            exit()
        else:
            print("Ждем.")
            os.system("sleep 120")

