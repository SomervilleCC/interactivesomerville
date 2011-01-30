from fabric.api import *
from fabric.contrib.files import *


env.apache_port = 9000
env.fqdn = 'my-host.my-domain.com'
env.admin_user = 'admin'


def pave_server():
    env.user = create_first_user()
    configure_sshd()
    set_hostname()
    #software_update()
    #install_nginx()
    #install_apache()
    #install_postgres()

def create_first_user():
    env.user = 'root'
    username = prompt('Specify a username: ', default=env.admin_user)
    password = prompt('Specify a password for %s: ' % username)
    run('useradd -d /home/%s -s /bin/bash -m %s' % (username, username))
    # hacky way to set password via stdin
    run('yes %s | passwd %s' % (password, username))
    # clear history
    run('history -c')
    append('%s\tALL=(ALL) ALL' % username, '/etc/sudoers')
    # TODO change root password, upload ssh key
    return username
    
def configure_sshd():
    # TODO block root login, change port
    pass

def set_hostname():
    """Setup hostname and FQDN in /etc/hostname and /etc/hosts.conf"""
    # TODO add a regex here to verify a proper fqdn was entered
    env.fqdn = prompt('Specify a fully qualified domain name (FQDN): ', 
                      default=env.fqdn)
    # technically, an FQDN should have a trailing period, but we don't need it
    env.fqdn.strip('.')
    if '.' in env.fqdn:
        hostname_tuple = env.fqdn.split('.')
        hostname_guess = hostname_tuple[0]
        domain_name_guess = '.'.join(hostname_tuple[1:])
    else:
        hostname_guess = 'my-host'
        domain_name_guess = 'my-domain.com'
    hostname = prompt('Specify a hostname: ', default=hostname_guess)
    domain_name = prompt('Specify a domain name: ', default=domain_name_guess)
    sudo('hostname %s' % hostname)
    sudo('echo %s > /etc/hostname' % hostname)
    sudo('echo %s > /etc/mailname' % domain_name)
    conf_file = '/etc/hosts'
    upload_template('templates/%s' % conf_file, 
                    conf_file,
                    context={'hostname': hostname, 'fqdn': env.fqdn},
                    use_sudo=True) 

def software_update():
    """Update package list and apply all available updates"""
    sudo('aptitude update -q -y')
    sudo('aptitude safe-upgrade -q -y')
    # setup build enviroment
    sudo('chown %s /usr/local/src' % env.user)
    sudo('aptitude install -q -y build-essential')
    
def configure_firewall():
    # TODO setup UFW
    pass

def configure_postfix():
    # TODO setup UFW
    pass
    
def install_nginx():
    # TODO setup UFW
    pass

def install_apache():
    # TODO setup UFW
    pass

def install_postgres():
    # TODO setup UFW
    pass
    
    

            sudo('make install')
    sudo('ldconfig')