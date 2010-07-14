import os

from twisted.trial import unittest
from twisted.python import runtime

from buildslave.test.fake.runprocess import Expect
from buildslave.test.util.sourcecommand import SourceCommandTestMixin
from buildslave.commands import svn

class TestSVN(SourceCommandTestMixin, unittest.TestCase):

    def setUp(self):
        self.setUpSourceCommand()
        self.patch_getCommand('svn', 'path/to/svn')
        self.patch_getCommand('svnversion', 'path/to/svnversion')
        self.clean_environ()

    def tearDown(self):
        self.tearDownSourceCommand()

    def svn_command(self, revision=None, mode='copy', **kwargs):
        return self.make_command(svn.SVN, dict(
            workdir='workdir',
            mode=mode,
            revision=revision,
            svnurl='http://svn.local/app/trunk',
            **kwargs
        ))

    def test_copy_fresh(self):
        # if the .svn directory does not exist in the source dir, then 'copy'
        # should do a full checkout
        self.set_path_status(os.path.join(self.basedir_source, ".svn"), False)

        self.svn_command(mode='copy')
        return self.check_clobber_and_copy()

    def test_copy_update(self):
        # if the .svn directory does exist in the source dir, the source data matches,
        # and the dir is not patched, it should update source and copy
        self.set_path_status(os.path.join(self.basedir_source, ".svn"), "dir")
        self.set_path_status(os.path.join(self.basedir_workdir, ".buildbot-patched"), False)
        self.set_sourcedata("http://svn.local/app/trunk\n")

        self.svn_command(mode='copy')
        return self.check_update_and_copy()

    def test_copy_update_if_patched(self):
        # if the workdir is patched, we still update the source dir and copy
        self.set_path_status(os.path.join(self.basedir_source, ".svn"), "dir")
        self.set_path_status(os.path.join(self.basedir_workdir, ".buildbot-patched"), 'file')
        self.set_sourcedata("http://svn.local/app/trunk\n")

        self.svn_command(mode='copy')
        return self.check_update_and_copy()

    # a common set of actual activities from the command

    def check_update_and_copy(self):
        """
        Check that the command clobbers the workdir, updates the source dir,
        and copies
        """
        exp_environ = dict(PWD='.', LC_MESSAGES='C')
        expects = [
            Expect([ 'clobber', 'workdir' ],
                self.basedir)
                + 0,
            Expect([ 'path/to/svn', 'update', '--non-interactive',
                     '--no-auth-cache', '--revision', 'HEAD'],
                self.basedir_source,
                sendRC=False, timeout=120, usePTY=False, environ=exp_environ)
                + 0,
            Expect([ 'path/to/svnversion', '.' ],
                self.basedir_source,
                sendRC=False, timeout=120, usePTY=False, keepStdout=True,
                environ=exp_environ, sendStderr=False, sendStdout=False)
                + { 'stdout' : '9753\n' }
                + 0,
            Expect([ 'copy', 'source', 'workdir'],
                self.basedir)
                + 0,
        ]
        self.patch_runprocess(*expects)

        d = self.run_command()
        d.addCallback(self.check_sourcedata, "http://svn.local/app/trunk\n")
        return d

    def check_clobber_and_copy(self):
        """
        Check that the command clobbers the workdir, clobbers the source dir,
        checks out, and copies
        """
        exp_environ = dict(PWD='.', LC_MESSAGES='C')
        expects = [
            Expect([ 'clobber', 'workdir' ],
                self.basedir)
                + 0,
            Expect([ 'clobber', 'source' ],
                self.basedir)
                + 0,
            Expect([ 'path/to/svn', 'checkout', '--non-interactive', '--no-auth-cache',
                     '--revision', 'HEAD', 'http://svn.local/app/trunk', 'source' ],
                self.basedir,
                sendRC=False, timeout=120, usePTY=False, environ=exp_environ)
                + 0,
            Expect([ 'path/to/svnversion', '.' ],
                self.basedir_source,
                sendRC=False, timeout=120, usePTY=False, keepStdout=True,
                environ=exp_environ, sendStderr=False, sendStdout=False)
                + { 'stdout' : '9753\n' }
                + 0,
            Expect([ 'copy', 'source', 'workdir'],
                self.basedir)
                + 0,
        ]
        self.patch_runprocess(*expects)

        d = self.run_command()
        d.addCallback(self.check_sourcedata, "http://svn.local/app/trunk\n")
        return d

