#!/usr/bin/python
#encoding:utf-8
import web

#为了启用session关闭调试模式
web.config.debug = False

render = web.template.render('templates/')

#url和类的对应关系
urls = (
    '/', 'index',
    '/change_password', 'verify_id',
    '/succeed', 'change_password',
)

#连接数据库
db  = web.database(dbn='mysql', user='root', pw='omproot', host='localhost', port=3306, db='svn_aa', charset='utf8', use_unicode=0)

class index:
    def GET(self):
        cookies = web.cookies(username = "")
        #打开index.html，在里面输入登录信息
        return render.index(cookies.username)

class verify_id:
    def POST(self):
        formInput = web.input()
        username = formInput.username.strip()
        password = formInput.password.strip()
        #简单防止sql注入攻击
        if username.find("'") != -1 or password.find("'") != -1:
            return render.wrongusernameorpassword("Easter_egg")

        #把username作为cookie保存，过期时间是3600*24*365/2
        web.setcookie("username", username, 15768000)
        passwd = db.query("SELECT pass FROM svn_user WHERE name='" + username + "';")
        #如果根据username查不出结果，说明username输入错误
        if len(passwd) == 0:
            return render.wrongusernameorpassword("verify_id")
        else:
            #由于pass是python的保留字，所以用这种方式从数据库查询返回的结果集中取出password
            passwordFromDb = passwd[0]['pass']
            #如果输入的password与从数据库中取出的一致，打开修改密码页面，否则说明password输入错误
            if password == passwordFromDb:
                return render.changepassword(username)
            else:
                return render.wrongusernameorpassword("verify_id")

class change_password:
    def POST(self):
        formInput = web.input()
        username = formInput.username.strip()
        password = formInput.password.strip()
        #简单防止sql注入攻击
        if username.find("'") != -1 or password.find("'") != -1:
            return render.wrongusernameorpassword("Easter_egg")

        #根据输入的值更新svn_user表中对应用户的密码
        try:
            db.query("UPDATE svn_user SET pass = '" + password + "' WHERE name = '" + username + "';")
        except SystemExit:
             print "System Exit due to an error!"
        except:
             traceback.print_exc()
        return render.succeed()        

if __name__ == "__main__":
    app = web.application(urls, locals())
    #启用session
    #if web.config.get('_session') is None:
    #    session = web.session.Session(app, web.session.DiskStore('sessions'))
    #    web.config._session = session
    #else:
    #    session = web.config._session
    session = web.session.Session(app, web.session.DiskStore('sessions'))
    web.config.session_parameters['timeout'] = 600, #似乎没有生效啊
    web.config.session_parameters['ignore_change_ip'] = False
    web.config.session_parameters['expired_message'] = 'Session 已过期，请重新登录'
    app.run()
