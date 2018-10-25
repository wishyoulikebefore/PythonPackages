Python os模块包含普遍的操作系统功能。如果你希望你的程序能够与平台无关的话，这个模块是尤为重要的

常用指令
os.name
输出字符串指示正在使用的平台。如果是window 则用'nt'表示，对于Linux/Unix用户，它是'posix'。
os.getcwd()
函数得到当前工作目录，即当前Python脚本工作的目录路径。
os.chdir("dirname")    
改变当前脚本工作目录到dirname
os.curdir    
返回当前目录
os.listdir()
返回指定目录下的所有文件和目录名。
os.remove()
删除一个文件。
os.makedirs()    
可生成多层递归目录
os.removedirs()    
可删除多层递归空目录，若目录不为空则无法删除
os.mkdir()    
生成单级目录
os.rmdir()    
删除单级空目录，若目录不为空则无法删除，报错，需要用shutil.rmtree
os.pardir()    
获取当前目录的父目录字符串名
os.listdir()    
列出指定目录下的所有文件和子目录，包括隐藏文件
os.tmpfile()    
创建并打开‘w+b’一个新的临时文件
os.remove()    
删除一个文件
os.rename("oldname","newname")    
重命名文件
os.system()
运行shell命令。
>>> os.system('dir')
0
os.linesep字符串给出当前平台使用的行终止符
>>> os.linesep
'\r\n'            #Windows使用'\r\n'，Linux使用'\n'而Mac使用'\r'。

os.path.split()
函数返回一个路径的目录名和文件名
>>> os.path.split('C:\\Python25\\abc.txt')
('C:\\Python25', 'abc.txt')
os.path.isfile()和os.path.isdir()
分别检验给出的路径是一个文件还是目录。
os.path.exists()
检验给出的路径是否真地存在
>>> os.path.exists('C:\\Python25\\abc.txt')
False
os.path.abspath(name)
获得绝对路径
os.path.basename(path)
返回文件基名
>>> os.path.basename('c:\\Python\\a.txt')
'a.txt'
os.path.getsize(name)
获得文件大小
os.path.splitext()
分离文件名与扩展名，用于判断某一类型文件
>>> os.path.splitext('a.txt')
('a', '.txt')
os.path.join(path,name)
连接目录与文件名或目录
>>> os.path.join('c:\\Python','a.txt')
'c:\\Python\\a.txt'
os.path.dirname(path)
返回文件路径
>>> os.path.dirname('c:\\Python\\a.txt')
'c:\\Python'

os.environ    
获取系统环境变量
os.access('pathfile',os.W_OK)  
检验文件权限模式，输出True，False
os.chmod('pathfile',os.W_OK)    

