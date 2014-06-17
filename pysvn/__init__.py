#-*- coding:utf-8 -*-
#!/usr/bin/env python

import re
import string, os, sys
import ConfigParser

import pyssh

REPOSITORY_DIR = "/opt/repository"   # 仓库主目录
REPOSITORY_SVN_DIR = "/opt/repository/svnserver"   # SVN主目录
HTPASSWD = "/opt/repository/.htpasswd"      # 用户密码文件
AUTHZ = "/opt/repository/.authz.conf"       # 授权文件

if not os.path.exists('/opt'):
    os.mkdir('/opt', 0700)
if not os.path.exists(REPOSITORY_DIR):
    os.mkdir(REPOSITORY_DIR, 0700)
if not os.path.exists(REPOSITORY_SVN_DIR):
    os.mkdir(REPOSITORY_SVN_DIR, 0700)
if not os.path.exists(HTPASSWD):
    pyssh.getcmd(cmd="echo '' > %r ; chmod 700 %r"%(HTPASSWD,HTPASSWD))
if not os.path.exists(AUTHZ):
    pyssh.getcmd(cmd="echo '' > %r ; chmod 700 %r"%(AUTHZ, AUTHZ))

CF = ConfigParser.ConfigParser()
CF.read(AUTHZ)

"""
    公共返回值
    @return:status=INT,    # 执行状态, 0=成功执行函数功能, 其他数字=没有成功执行， 错误信息在msgs中
            msgs = STRING, # 执行错误的时候， 返回的错误信息
            results = INT/STRING/LIST/TUPLE/DICT, # 执行结果
"""


def svn_add(proname=""):
    """ 创建svn仓库
        @params: proname=STRING  #工程名，英文字母，数字，下划线
    """
    if proname != "":
        cmd = "export HOME=/home/apache; cd "+REPOSITORY_SVN_DIR+";"
        cmd+= "svnadmin create "+proname+";"
        cmd+= "chown apache.apache -R " + proname + ";"
        cmd+= "chmod 700 -R " + proname
        (status, msgs, results) = pyssh.getcmd(cmd=cmd)
    else:
        status = -1; msgs = u"请输入正确的版本库名称， 它有字母， 下划线， 和数字构成！"; resutls = ""
    return (status, msgs, results)

def svn_del(proname=""):
    """ 删除svn仓库
        @params: proname=STRING  #工程名，英文字母，数字，下划线
    """
    if proname != "":
        cmd = "export HOME=/home/apache; cd "+REPOSITORY_SVN_DIR+"; rm -rf " + proname
        (status, msgs, results) = pyssh.getcmd(cmd=cmd)
    else:
        status = -1; msgs = u"不能删除空的版本库，请正确输入"; resutls = ""
    return (status, msgs, results)

def svn_get():
    """ 得到当前有那些svn仓库, 返回一个版本库名称构成的序列
        @return results=LIST        # LIST=['test1', 'test2']
    """
    cmd = "ls " + REPOSITORY_SVN_DIR
    (status, msgs, results) = pyssh.getcmd(cmd=cmd)
    results = [r for r in results.split() if r]
    return (status, msgs, results)

def passwd_add(username='', password=''):
    """ 创建svn用户密码
        @params:username=STRING
                password=STRING
    """
    cmd = "export HOME=/home/apache; cd "+REPOSITORY_DIR+"; htpasswd -b .htpasswd " + username + " " + password
    (status, msgs, results) = pyssh.getcmd(cmd=cmd)
    return (status, msgs, results)

def passwd_set(username='', password=''):
    """ 修改svn用户密码
        @params:username=STRING
                password=STRING
    """
    cmd = "export HOME=/home/apache; cd "+REPOSITORY_DIR+"; htpasswd -b .htpasswd " + username + " " + password
    (status, msgs, results) = pyssh.getcmd(cmd=cmd)
    return (status, msgs, results)

def passwd_del(username=''):
    """ 删除svn用户
        @params:username=STRING
    """
    cmd = "export HOME=/home/apache; cd "+REPOSITORY_DIR+"; htpasswd -D .htpasswd " + username
    (status, msgs, results) = pyssh.getcmd(cmd=cmd)
    return (status, msgs, results)

def passwd_get():
    """ 得到svn仓库的所有用户
        @return: results=LIST   #LIST=['user1', 'user2']
    """
    cmd = "cat " + HTPASSWD
    (status, msgs, results) = pyssh.getcmd(cmd=cmd)

    if status != 0:
        return (status, msgs, results)
    tmp = []
    for res in results.split("\n"):
        if res != "":
            tmp.append(res.split(":")[0])
    return (status, msgs, tmp)


def authz_groups_add(groupname=''):
    """创建分组"""
    if groupname:
        if groupname in CF.options('groups'):
            return (-1,'分组<%r>存在，不能创建！'%groupname,'')   
        else:
            CF.set("groups", groupname, '')
            CF.write(open(AUTHZ, 'w'))
    else:
        return (-1,'分组名<%r>不存在，不能创建！'%groupname,'')   
    return (0, '', '分组<%r>创建成功'%groupname, '')

def authz_groups_del(groupname=''):
    """删除分组"""
    if groupname:
        if groupname not in CF.options('groups'):
            return (-1,'分组<%r>不存在，不能删除！'%groupname,'')   
        else:
            CF.remove_option("groups", groupname)
            CF.write(open(AUTHZ, 'w'))
    else:
        return (-1,'分组名<%r>不存在，不能删除！'%groupname,'')   
        
    return (0, '', '分组<%r>删除成功'%groupname)

def authz_groups_get():
    """ 获得所有的分组
        @return: results=LIST       # LIST=[('group1', 'user1, user2'), ('group2', 'user2, user3, user4')]
    """
    if 'groups' not in CF.sections():
        CF.add_section('groups')
        CF.write(open(AUTHZ, 'w'))
    results = CF.items('groups')
    return (0, '', results)
    

def authz_groups_user_add(groupname='', username=''):
    """给分组增加用户"""
    if groupname and username:
        if groupname not in CF.options('groups'):
            return (-1,'分组不存在，不能增加！','')   
        else:
            if username in CF.get('groups', groupname).split(','):
                return (-1,'用户已经存在于分组中，不能增加！','')   
            else:
                if CF.get('groups', groupname):
                    value = CF.get('groups', groupname) + ',' + username
                else:
                    value = username
                CF.set('groups', groupname, value)
                CF.write(open(AUTHZ, 'w'))
    else:
        return (-1,'分组名/用户名不能为空，不能增加！','')   
    return (0, '', '增加用户到分组成功！')

def authz_groups_user_del(gourname='', username=''):
    """给分组删除用户"""
    if groupname and username:
        if groupname not in CF.options('groups'):
            return (-1,'分组不存在，不能删除！','')   
        else:
            if username not in [i.strip() for i in CF.get('groups', groupname).split(',') if i]:
                return (-1,'用户不存在于分组中，不能删除！','')   
            else:
                value = string.join([i for i in CF.get('groups', groupname).split(',') if i and i!= username], ',')
                CF.set('groups', groupname, value)
                CF.write(open(AUTHZ, 'w'))
    else:
        return (-1,'分组名/用户名不能为空，不能删除！','')   
    return (0, '', '删除分组用户成功！')

def authz_groups_user_get(groupname=''):
    """得到一个分组包含的所有账户"""
    results = []
    if groupname:
        if groupname not in CF.options('groups'):
            return (-1,'分组不存在，不能增加！','')   
        else:
            results = [i for i in CF.get('groups', groupname).split(',') if i]
    else:
        return (-1,'分组名不能为空，不能查询！','')   
    return (0, '', results)

def repos_import_add(reposname='', dirs='{trunk,tags,branches,docs}'):
    """ 给一个版本库设置一个目录结构，默认包含{trunk,branches,tags,docs}
        @Params: reposname = STRING; #版本库名称， 是字串
                 dirs = STRING; #版本库的目录结构，多个目录， 由{}括起来， 并由,分割
                    默认是： {trunk,tags,branches,docs} 并在trunk/ 创建文件README.txt
    """
    if reposname:
        cmd = "rm -rf /tmp/repos ; "
        cmd +="mkdir -p /tmp/repos/"+dirs+" ;"
        cmd +="touch /tmp/repos/trunk/README.txt ;"
        cmd +="svn import /tmp/repos/ file://"+ REPOSITORY_SVN_DIR + "/" + reposname + "/ -m 'Set Default Directory'; "
        cmd += "rm -rf /tmp/repos "

        (status, msgs, results) = pyssh.getcmd(cmd=cmd)
    else:
        status = -1; msgs = u'Error:版本库名称不能为空'; results = ''

    return (status, msgs, results)

def authz_repos_add(reposname='', dir=''):
    """ 给一个版本创建一个目录控制"""
    if reposname and dir:
        repos_dir = reposname + ":" +  dir
        if repos_dir in CF.sections():
            return (-1,u"版本库<%r>的目录控制<'%r'>已存在，不能增加！"%(reposname, dir),'')   
        else:
            CF.add_section(repos_dir)
            #CF.set('%r:%r'%(reposname, dir), '*', 'r')
            CF.write(open(AUTHZ, 'w'))
    else:
        return (-1,u"版本库/目录控制不能为空，不能增加！",'')   
    return (0, '', u"给版本<%r>增加要控制的目录<%r>成功！"%(reposname, dir))

def authz_repos_del(reposname='', dir=''):
    """ 给一个版本删除一个目录控制"""
    if reposname and dir:
        repos_dir = reposname + ":" +  dir
        if repos_dir not in CF.sections():
            return (-1,"版本库<%r>的目录控制<'%r'>不存在，不能删除！"%(reposname, dir),'')   
        else:
            CF.remove_section(repos_dir)
            CF.write(open(AUTHZ, 'w'))
    else:
        return (-1,'版本库/目录控制不能为空，不能删除！','')   
    return (0, '', '给版本<%r>删除要控制的目录<%r>成功！'%(reposname, dir))

def authz_repos_get(reposname=''):
    """ 得到一个版本包含的所有授权子目录，也就是配置文件中每一项版本库配置记录中， "："后面的目录
        @params: resposname=STRING # 版本库名称
        @return: results=LIST   # 例如：results=['/','/trunk']
    """
    results = []
    if reposname:
        results = [rep.split(':')[1] for rep in CF.sections() if rep != 'groups' if rep.split(':')[0] == reposname]
    else:
        return (-1,'版本库不能为空，不能查询！','')   
    return (0, '', results)


def authz_repos_dir_auth_add(reposname='', dir='', auth='', auth_value=''):
    """ 给一个版本的一个目录创建访问权限
        @params:reposname=STRING        # 版本库名称
                dir=STRING              # 版本库权限控制子目录, 比如： ‘/’， ‘/trunk', ...
                auth=STRING             # 需要授权的用户或组， 比如： xcluo, @group1
                auth_value=STRING       # 权限, value in ['', 'r', 'rw', 'w']
    """
    if reposname and dir and auth and auth_value:
        repos_dir = reposname + ":" +  dir
        if repos_dir not in CF.sections():
            return (-1,'版本中不存在此项目录控制，不能插入！','')   
        CF.set(repos_dir, auth, auth_value)
        CF.write(open(AUTHZ, 'w'))
    else:
        return (-1,'版本库/目录控制不能为空，不能查询！','')   
    return (0, '', '给版本<%r>删除要控制的目录<%r>成功！'%(reposname, dir))

def authz_repos_dir_auth_del(reposname='', dir='', auth=''):
    """给一个版本的一个目录删除访问权限"""
    if reposname and dir and auth:
        repos_dir = reposname + ":" +  dir
        if repos_dir not in CF.sections():
            return (-1,'版本中不存在此项目录控制，不能删除！','')   
        CF.remove_option(repos_dir, auth)
        CF.write(open(AUTHZ, 'w'))
    else:
        return (-1,'版本库/目录控制不能为空，不能查询！','')   
    return (0, '', '给版本<%r>删除要控制的目录<%r>成功！'%(reposname, dir))


def authz_repos_dir_auth_get(reposname='', dir=''):
    """获取一个版本库的一个访问目录的所有访问权限"""
    """
        @Return: Tuple = (0, '', [('*', 'r'), ('xcluo', 'rw')])
    """
    results = []
    if reposname and dir:
        repos_dir = reposname + ":" +  dir
        if repos_dir in CF.sections():
            results = CF.items(repos_dir)
        else:
            return (-1,'版本库目录控制不存在，不能查询！','')   
    else:
        return (-1,'版本库/目录控制不能为空，不能查询！','')   
    return (0, '', results)


def repos_dirtrees(reposname='', depth=2):
    """ 获取版本库的目录结构，默认深度到根之下2级
        @Params: reposname = STRING 版本库的名字
                 depth = INT 搜索的深度
        @Return: (status, msgs, results)
            status = INT, # 状态码， 0正常执行，否则有问题
            msgs = String, # 如果status非零， 错误信息在msgs中体现
            results = LIST, # 正常执行后的返回值，类似于 [
                '/', '/tree',......
            ]
    """
    if not reposname:
        return (-1, u'Error: 版本仓库名不能为空！', '')

    cmd = "svnlook tree " + REPOSITORY_SVN_DIR + "/" + reposname + " | grep \/"
    (status, msgs, results) = pyssh.getcmd(cmd=cmd)
    if status != 0:
        return (status, msgs, results)

    treedirs = [t for t in results.split('\n') if t]  #  所有的目录

    index = [t.count(' ') for t in treedirs if t]     # 每个目录的级别
    
    for j in range(1, len(treedirs)):
        ct_now = treedirs[j].count(' ') # 当前目录的级别

        if ct_now > depth: # 如果超过深度， 就继续处理， 跳过当前
            treedirs[j] = ''
            continue

        for i in range(j-1,-1,-1):
            if index[i] < ct_now: # 如果当前目录的级别小于之前一个目录的，就叠加之
                treedirs[j] = treedirs[i][treedirs[i].count(' '):] + treedirs[j][treedirs[j].count(' '):] 
                ct_now = index[i]
                break
     
    treedirs = ['/'] + [t[0:-1] for t in treedirs if t and t!='/']  #  去除最后的斜线
    return (status, msgs, treedirs)


def reversion_get(reposname='', depth=10):
    """ 获取版本库当前的提交，包含编号，时间，和变化。 默认向前查10个版本库
        @Return: (status, msgs, results)
            status = INT, # 状态码， 0正常执行，否则有问题
            msgs = String, # 如果status非零， 错误信息在msgs中体现
            results = LIST, # 正常执行后的返回值，类似于 [
                    {'1':{'date':'2012-12-05 22:33:44 ()', 'diff':'更新的内容'}}
                    {'0':{'date':'2012-12-05 22:33:44 ()', 'diff':'更新的内容'}}
                ] 
    """
    if not reposname:
        return (-1, u'Error: 版本仓库名不能为空！', '')

    (status, msgs, results) = pyssh.getcmd(cmd="svnlook history " + REPOSITORY_SVN_DIR + "/" + reposname + "  | grep \/")

    if status != 0:
        return (status, msgs, results)

    reversion = [r.split() for r in results.split('\n') if r ][0:depth]

    results = []
    for r in reversion:
        (s1, m1, date) = pyssh.getcmd(cmd="svnlook date " + REPOSITORY_SVN_DIR + "/" + reposname + " -r %s"%r[0])
        (s2, m2, diff) = pyssh.getcmd(cmd="svnlook diff " + REPOSITORY_SVN_DIR + "/" + reposname + " -r %s"%r[0])
        if s1 + s2 == 0:
            results.append({r[0]:{'date':date, 'diff':diff}})

    return (status, msgs, results)


