#!/usr/bin/env python

# update the line below to your email
# if left empty, the password will be asked at runtime (which is good)
student_email = 'first.last@univ.edu'
student_passwd = ''

# Students: do not modify below lines

'''
Project identity
'''

project_name = 'a_cmake_project'
mail_period = 0 # minutes
mail_total = 1  # number of mails

# if empty, look for a folder <project_name> with a CMakeLists.txt containing the same name
# otherwise, look for a folder that matches all listed files (possibly with sub-folders)
project_signature = []

# will not zip the following files or directories (even if they are in the signature)
project_ignores = ['do_not_want.md']

'''
Advanced configuration
'''
prof_email = 'prof.email@univ.edu'
smtp_server = 'smtps.nomade.ec-nantes.fr'

# separator between first name and last name in email address
email_sep = '.' 

# ordered fields: project name / student full name / message count / total messages
email_subject = '[Snapshot {}]  {} - #{}/{}'

# the core of the mail, more or less useless as only the professor will see it
email_body = 'Automated message'

# know proxies that may be needed
proxy_candidates = []
proxy_candidates.append(('http://proxy.irccyn.ec-nantes.fr', 3128))
proxy_candidates.append(('cache.cites-u.univ-nantes.fr', 3128))


# Do not modify below lines

import sys, os, zipfile, smtplib, re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formatdate
from getpass import getpass
from time import sleep
try:
    import socks
except:
    print('Socks module not found, please install python-socks or python3-socks')
    sys.exit(0)
    
    
class SMTPproxy:
    def __init__(self):        
        
        self.passwd = student_passwd
        
        for self.proxy,self.port in [('',0)] + proxy_candidates:
            try:
                if self.proxy:
                    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, self.proxy, self.port)
                    socks.wrapmodule(smtplib)
                server = smtplib.SMTP(smtp_server , 587)
                server.starttls()
                break
            except:
                pass            
        else:
            self.proxy = self.port = None
            
    def ok(self):
        return self.proxy != None
            
    def server(self):
        if self.proxy:
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, self.proxy, self.port)
            socks.wrapmodule(smtplib)
        server = smtplib.SMTP(smtp_server , 587)
        server.starttls()
        
        if not self.passwd:
            self.passwd = getpass('Enter your password for ' + student_email + ' : ')
                
        try:
            server.login(student_email, self.passwd)
            return server
        except smtplib.socket.gaierror:
            print('Could not connect to mail server, check your internet connection')
        except smtplib.SMTPAuthenticationError:
            print('Could not connect to mail server: wrong user/password')
        return None
    
# init SMTP with proxy
proxy = SMTPproxy()
if not proxy.ok():
    print('Could not connect to mail server, check your internet connection and potential proxy')
    sys.exit(0)
    
# test login
if not proxy.server():
    sys.exit(0)
    
# Find project folder
# TODO - test on macOS / Windows

# adapt file lists
if os.path.sep != '/':
    project_signature = [p.replace('/', os.path.sep) for p in project_signature]
    project_ignores = [p.replace('/', os.path.sep) for p in project_ignores]

project_cmake_re = re.compile('.*project *\( *{} *\).*'.format(project_name), flags=re.DOTALL)
def is_project(path, files):
    if project_signature:
        for f in project_signature:
            if not os.path.exists(os.path.join(path,f)):
                return False            
        return True
    
    if 'CMakeLists.txt' in files and path.endswith(project_name):
        with open(os.path.join(path,'CMakeLists.txt')) as f:
            return project_cmake_re.match(f.read())
    return False

project_path = []
print('Looking for project {}...'.format(project_name))
project_path = []
root = os.path.expanduser('~')
ignores = ('build', 'log')

for cur_dir, sub_dirs, files in os.walk(root):
    # avoid hidden / ignored folders when walking
    if '/.' in cur_dir:
        sub_dirs[:] = []
    sub_dirs[:] = [d for d in sub_dirs if d[0] != '.' and d not in ignores]
    
    if is_project(cur_dir, files):
        project_path.append(cur_dir)
        sub_dirs[:] = []
            
if len(project_path) == 0:
    print('  Could not find project {}'.format(project_name))
    sys.exit(0)
    
# do not assume students have Python 2 futures
try:
    input = raw_input
except:
    pass
    
if len(project_path) == 1:
    print('  Found project @ {}'.format(project_path[0]))
    r = input('  Confirm location [Y/n]: ')
    if r == 'n':
        sys.exit(0)
    project_path = project_path[0]
else:
    print('  Found several project locations:\n')
    for i,s in enumerate(project_path):
        print('  ({}) @ {}'.format(i+1, s))
    r = input('\n  Select location to use (enter to cancel): ')
    if r.isdigit() and 0 < int(r) <= len(project_path):
        project_path = project_path[int(r)-1]
    else:
        sys.exit(0)
        
        
# build mailed message

def extract_name(mail):
    name = mail.split('@')[0]
    if email_sep in name:
        first, last = name.split(email_sep)
        return '{} {}'.format(last.upper(), first.title())
    else:
        return name.title()
    
student_name = extract_name(student_email)
prof_name = extract_name(prof_email)

base_dir = os.path.abspath(os.path.dirname(__file__))

to_header = '{} <{}>'.format(prof_name, prof_email)
from_header = '{} <{}>'.format(student_name, student_email)
archive = '%s/%s-_%s_{}.zip' % (base_dir, project_name, student_name.replace(' ', '_'))

os.chdir(project_path)

def build_archive(snapshot_count):
    
    snapshot = archive.format(snapshot_count)
    
    zf = zipfile.ZipFile(snapshot, "w")
    
    for cur_dir, sub_dirs, files in os.walk('.'):
        for ignore in project_ignores:
            if ignore in sub_dirs:
                sub_dirs.remove(ignore)
        zf.write(cur_dir)
        for f in files:
            filepath = cur_dir + '/' + f
            print('Checking ' + filepath)
            keep = True
            for ignore in project_ignores:
                if filepath.endswith(ignore):
                    keep = False
                    break
            if keep:
                print('Writing ' + filepath)
                zf.write(filepath, compress_type=zipfile.ZIP_DEFLATED)
    zf.close()
    return snapshot

# main loop
for snapshot_count in range(1,mail_total+1):
    
    sleep(mail_period * 60)
    
    snapshot = build_archive(snapshot_count)
    
    # build message
    email = MIMEMultipart()
    email['From'] = from_header
    email['To'] = to_header
    email['Subject'] = email_subject.format(project_name, student_name, snapshot_count, mail_total)
    email['Date'] = formatdate(localtime=True)
    
    email.attach(MIMEText(email_body, 'plain'))
    
    with open(snapshot, 'rb') as f:
        attached_file = MIMEApplication(f.read(), _subtype='zip') 
        attached_file.add_header('content-disposition', 'attachment', filename=os.path.basename(snapshot))
    email.attach(attached_file)
    
    # send message
    server = proxy.server()
    if server:
        print('Sending "{}" to {} ...'.format(email['Subject'], prof_email))
        server.sendmail(student_email, prof_email, email.as_string())
        server.close()
    os.remove(snapshot)

os.chdir(base_dir)
