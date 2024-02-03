import cherrypy
import ssl
from irods.session import iRODSSession

defaults = {
  'title': "iRODS Password Booth",
  'custom_html_header': '',
  'custom_html_footer': "<p><a href='/'>Home</a> - <a href='/test'>test</a></p>"
}

def merge_custom_into_default_config(config):
    defaults.update(config)
    return defaults

def get_header(config):
    h = '''\
<html>
    <head>
    <title>{}</title>
    <link rel="stylesheet" href="app.css">
    </head>
    <body>
'''.format(config['title'])
    return h + config['custom_html_header']

def get_footer(config):
    f = '''\
    </body>
</html>
'''
    return config['custom_html_footer'] + f

def get_ssl_settings(config):
    ssl_settings = {'client_server_negotiation': config['client_server_negotiation'],
                    'client_server_policy': config['client_server_policy'],
                    'encryption_algorithm': config['encryption_algorithm'],
                    'encryption_key_size': config['encryption_key_size'],
                    'encryption_num_hash_rounds': config['encryption_num_hash_rounds'],
                    'encryption_salt_size': config['encryption_salt_size'],
                    'ssl_verify_server': config['ssl_verify_server'],
                    'ssl_ca_certificate_file': config['ssl_ca_certificate_file']
    }
    return ssl_settings

class Root(object):

    @cherrypy.expose
    def test(self):
        config = merge_custom_into_default_config(cherrypy.request.app.config['password_booth'])
        html_header = get_header(config)
        html_footer = get_footer(config)
        ssl_settings = get_ssl_settings(config)
        with iRODSSession(  host=config['irods_host'],
                            port=config['irods_port'],
                            zone=config['irods_zone'],
                            user='alice',
                            password='apass',
                            **ssl_settings) as session:
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
        html_header = get_header(config)
        html_footer = get_footer(config)
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
        config = merge_custom_into_default_config(cherrypy.request.app.config['password_booth'])
        html_header = get_header(config)
        html_footer = get_footer(config)
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
        ssl_settings = get_ssl_settings(config)
        with iRODSSession(  host=config['irods_host'],
                            port=config['irods_port'],
                            zone=config['irods_zone'],
                            user=username,
                            password=oldpass,
                            **ssl_settings) as session:
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
