import cherrypy
from irods.session import iRODSSession

default_css = '''\
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
    input {
      width: 100%;
      font-size: 110%;
      padding: 12px 20px;
      margin: 8px 0;
      box-sizing: border-box;
    }
    td {
      font-size: 110%;
      font-weight: bold;
      text-align: right;
    }
'''

defaults = {
  'title': "iRODS Password Booth",
  'background_color': 'lightblue',
  'custom_html_header': '',
  'custom_html_footer': "<p><a href='/'>Home</a> - <a href='/test'>test</a></p>",
  'custom_css': default_css
}

def merge_custom_into_default_config(config):
    defaults.update(config)
    return defaults

def get_header(config):
    defaults.update(config)
    h = '''\
<html>
    <head>
    <title>{}</title>
    </head>
    <body>
'''.format(defaults['title'])
    bg = '<style>body { background-color: '+defaults['background_color']+'; }</style>'
    style = '<style>'+defaults['custom_css']+'</style>'
    return h + bg + style + defaults['custom_html_header']

def get_footer(config):
    defaults.update(config)
    f = '''\
    {}
    </body>
</html>
'''.format(defaults['custom_html_footer'])
    return f

class Root(object):

    @cherrypy.expose
    def test(self):
        with iRODSSession(  host=cherrypy.request.app.config['password_booth']['irods_host'],
                            port=cherrypy.request.app.config['password_booth']['irods_port'],
                            zone=cherrypy.request.app.config['password_booth']['irods_zone'],
                            user='alice',
                            password='apass') as session:
            html_header = get_header(cherrypy.request.app.config['password_booth'])
            html_footer = get_footer(cherrypy.request.app.config['password_booth'])
            try:
                h = session.collections.get("/{}/home/{}".format(session.zone, session.username))
                html_body = ""
                html_body += "dir[{}]".format(dir(h))
                html_body += "<br/><br/>home collection"
                html_body += "<br/>- id[{}] path[{}] ctime[{}] mtime[{}]".format(h.id, h.path, h.create_time, h.modify_time)
                html_body += "<br/><br/>subcollections"
                for c in h.subcollections:
                    html_body += "<br/>- id[{}] path[{}] ctime[{}] mtime[{}]".format(c.id, c.path, c.create_time, c.modify_time)
                html_body += "<br/><br/>data_objects"
                for d in h.data_objects:
                    html_body += "<br/>- id[{}] name[{}] ctime[{}] mtime[{}]".format(d.id, d.name, d.create_time, d.modify_time)
                return html_header + html_body + html_footer
            except Exception as e:
                html_body = repr(e)
                return html_header + html_body + html_footer

    @cherrypy.expose
    def index(self):
        config = merge_custom_into_default_config(cherrypy.request.app.config['password_booth'])
        html_header = get_header(cherrypy.request.app.config['password_booth'])
        html_footer = get_footer(cherrypy.request.app.config['password_booth'])
        html_body = '''\
        <p>
        <form method="post" action="modify_password">
        <table border=0 align=center>
        <tr><td colspan=2><center><h1>{}</h1></center></td></tr>
        <tr><td>Username:</td><td><input type="text" value="" name="username"/></td></tr>
        <tr><td>Current Password:</td><td><input type="password" value="" name="oldpass"/></td></tr>
        <tr><td>New Password:</td><td><input type="password" value="" name="newpass"/></td></tr>
        <tr><td>Confirm New Password:</td><td><input type="password" value="" name="newpassconfirm"/></td></tr>
        <tr><td colspan=2><center><button class="button" type="submit">Change Password</button></center></td></tr>
        </table>
        </form>
        </p>
        '''.format(config['title'])
        return html_header + html_body + html_footer

    @cherrypy.expose
    def modify_password(self, *args, **kwargs):
        if cherrypy.request.method != 'POST':
            return 'only POST supported'
        html_header = get_header(cherrypy.request.app.config['password_booth'])
        html_footer = get_footer(cherrypy.request.app.config['password_booth'])
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
