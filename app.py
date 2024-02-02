import cherrypy
from irods.session import iRODSSession

html_header = '''\
<html>
    <head>
    <title>iRODS Password Booth</title>
    <style>
    .button {
      border: none;
      color: white;
      padding: 20px;
      text-align: center;
      text-decoration: none;
      display: inline-block;
      font-size: 18px;
      margin: 30px 60px;
      cursor: pointer;
      background-color: #008CBA; /* Blue */
    }
    </style>
    </head>
    <body>
'''

html_footer = '''\
    <p><a href='/'>Home</a></p>
    </body>
</html>
'''

class Root(object):

    @cherrypy.expose
    def index(self):
        html_body = '''\
        <p>
        <form method="post" action="modify_password">
        <table border=0>
        <tr><td>Username:</td><td><input type="text" value="" name="username"/></td></tr>
        <tr><td>Current Password:</td><td><input type="password" value="" name="oldpass"/></td></tr>
        <tr><td>New Password:</td><td><input type="password" value="" name="newpass"/></td></tr>
        <tr><td>Confirm New Password:</td><td><input type="password" value="" name="newpassconfirm"/></td></tr>
        <tr><td colspan=2><button class="button" type="submit">Change Password</button></td></tr>
        </table>
        </form>
        </p>
        '''
        return html_header + html_body + html_footer

    @cherrypy.expose
    def modify_password(self, *args, **kwargs):
        if cherrypy.request.method != 'POST':
            return 'only POST supported'
        username = kwargs.get('username')
        oldpass = kwargs.get('oldpass')
        newpass = kwargs.get('newpass')
        newpassconfirm = kwargs.get('newpassconfirm')
        if not username:
            html_body = 'missing username'
            return html_header + html_body + html_footer
        if not oldpass:
            html_body = 'missing oldpass'
            return html_header + html_body + html_footer
        if not newpass:
            html_body = 'missing newpass'
            return html_header + html_body + html_footer
        if not newpassconfirm:
            html_body = 'missing newpassconfirm'
            return html_header + html_body + html_footer
        if newpass != newpassconfirm:
            html_body = 'confirmation did not match'
            return html_header + html_body + html_footer
        with iRODSSession(  host=cherrypy.request.app.config['password_booth']['irods_host'],
                            port=cherrypy.request.app.config['password_booth']['irods_port'],
                            zone=cherrypy.request.app.config['password_booth']['irods_zone'],
                            user=username,
                            password=oldpass) as session:
            try:
                authenticated_user = session.users.get(session.username)
                authenticated_user.modify_password(oldpass, newpass)
                html_body = 'success'
                return html_header + html_body + html_footer
            except Exception as e:
                html_body = repr(e)
                return html_header + html_body + html_footer

if __name__ == '__main__':
    cherrypy.quickstart(Root(), '/', 'app.config')
