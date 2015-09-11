
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

