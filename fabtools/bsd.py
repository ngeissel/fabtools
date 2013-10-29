"""
Debian packages
===============

This module provides tools to manage Freebsd packages
and repositories.

"""
from __future__ import with_statement

from fabric.api import hide, run, settings

from fabtools.utils import run_as_root
from fabtools.files import is_dir

def pkg_manager():
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        if is_installed('portmaster'):
            manager = 'portmaster'
        elif is_installed('portupgrade'):
            manager = 'portinstall'
        else:
            manager = 'pkg_add -rv'

        return 'LC_ALL=C %s' % manager


def update_index(quiet=True):
    """
    Update port collection.
    """
    manager = 'portsnap'
    options = ""
    first_time = not is_dir('/usr/ports/')
    if first_time:
        run_as_root("%s %s fetch extract" % (manager, options))
    else:
        run_as_root("%s %s fetch update" % (manager, options))


def upgrade(safe=True):
    """
    Upgrade all ports.
    """
    manager = pkg_manager()
    if manager == 'portmaster':
        if safe:
            cmd = '--no-confirm'
    else:
        manager = 'portupgrade'
        if safe:
            cmd = '-aivc'
        else:
            cmd = '-a --batch'
    run_as_root("%(manager)s %(cmd)s" % locals(), pty=False)


def is_installed(pkg_name):
    """
    Check if a port is installed.
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        # we assume that package is underform category/port       
        pkg = pkg_name.split('/')
        pkg_name = pkg.pop()
        res = run("pkg_info|grep %(pkg_name)s" % locals())
        for line in res.splitlines():
            if line.startswith(pkg_name):
                return True
        return False

def install(packages, update=False, options=None, version=None):
    """
    Install one or more packages.

    If *update* is ``True``, the package definitions will be updated
    first, using :py:func:`~fabtools.deb.update_index`.

    Extra *options* may be passed to ``apt-get`` if necessary.

    Example::

        import fabtools

        # Update index, then install a single package
        fabtools.bsd.install('build-essential', update=True)

        # Install multiple packages
        fabtools.bsd.install([
            'python-dev',
            'libxml2-dev',
        ])

        # Install a specific version
        fabtools.bsd.install('emacs', version='23.3+1-1ubuntu9')

    """
    manager = pkg_manager()
    if update:
        update_index()
    if options is None:
        options = []
    if version is None:
        version = ''
    if version and not isinstance(packages, list):
        version = '=' + version
    if not isinstance(packages, basestring):
        packages = " ".join(packages)
    if manager == 'portinstall':
        options.append("--batch")
    if manager == 'portmaster':
        options.append("--no-confirm")
        if update:
            options.append("--update-if-newer")
    options = " ".join(options)
    cmd = '%(manager)s %(options)s %(packages)s' % locals()
    run_as_root(cmd, pty=False)


def uninstall(packages, purge=False, options=None):
    """
    Remove one or more packages.

    If *purge* is ``True``, the package configuration files will be
    removed from the system.

    Extra *options* may be passed to ``pkg_delete`` if necessary.
    """
    manager = 'pkg_delete'
    #command = "purge" if purge else "remove"
    if options is None:
        options = []
    if not isinstance(packages, basestring):
        packages = " ".join(packages)
    #options.append("--assume-yes")
    options = " ".join(options)
    cmd = '%(manager)s %(options)s %(packages)s' % locals()
    run_as_root(cmd, pty=False)



