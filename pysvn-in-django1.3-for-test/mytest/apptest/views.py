# Create your views here.

from django.http import HttpResponse
import pysvn

def index(request):
    str = ""

    attrs =(
            #'svn_add',
            #'svn_del',
            'svn_get',

            #'passwd_add', 
            #'passwd_set', 
            #'passwd_del', 
            'passwd_get', 

            #'authz_groups_add',
            #'authz_groups_del',
            'authz_groups_get',

            #'authz_groups_user_add',
            #'authz_groups_user_del',
            'authz_groups_user_get',

            #'authz_repos_add',
            #'authz_repos_del',
            'authz_repos_get',

            #'authz_repos_dir_auth_get',
            #'authz_repos_dir_auth_del',
            'authz_repos_dir_auth_add',
            )
    for attr in attrs:
        (status, msgs, results) = getattr(pysvn, attr)()
        str += " \
            %s: <br /> \
            ---------------------------- <br /> \
            status = %d <br/>  \
            msgs = %s <br />   \
            resutls = %s <hr /> \
        " % (attr, status, msgs, results)

    return HttpResponse(str)
