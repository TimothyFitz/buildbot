from buildslave import runprocess
from buildslave.test.util import command
from buildslave.commands import base

class SourceCommandTestMixin(command.CommandTestMixin):
    """
    Support for testing Source Commands; an extension of CommandTestMixin
    """

    def setUpSourceCommand(self):
        self.setUpCommand()

        self.sourcedata = ''

        self.testPaths = {}
        def testPathExists(cmd, path):
            if path not in self.testPaths:
                raise AssertionError('no patch_testPath call for "%s"' % path)
            return self.testPaths[path]
        self.patch(base.SourceBaseCommand, 'testPathExists', testPathExists)

        def testPathIsDir(cmd, path):
            if path not in self.testPaths:
                raise AssertionError('no patch_testPath call for "%s"' % path)
            return self.testPaths[path] == 'dir'
        self.patch(base.SourceBaseCommand, 'testPathIsDir', testPathIsDir)

        def testPathIsFile(cmd, path):
            if path not in self.testPaths:
                raise AssertionError('no patch_testPath call for "%s"' % path)
            return self.testPaths[path] == 'file'
        self.patch(base.SourceBaseCommand, 'testPathIsFile', testPathIsFile)

    def tearDownSourceCommand(self):
        self.tearDownCommand()

    def make_command(self, cmdclass, args, makedirs=False):
        """
        Same as the parent class method, but this also adds some source-specific
        patches:

        * writeSourcedata - writes to self.sourcedata (self is the TestCase)
        * readSourcedata - reads from self.sourcedata
        * doClobber - invokes RunProcess(['clobber', DIRECTORY])
        * doCopy - invokes RunProcess(['copy', cmd.srcdir, cmd.workdir])
        """

        cmd = command.CommandTestMixin.make_command(self, cmdclass, args, makedirs)

        # note that these patches are to an *instance*, not a class, so there
        # is no need to use self.patch() to reverse them

        def readSourcedata():
            return self.sourcedata
        cmd.readSourcedata = readSourcedata

        def writeSourcedata(res):
            self.sourcedata = cmd.sourcedata
            return res
        cmd.writeSourcedata = writeSourcedata

        def doClobber(_, dirname):
            r = runprocess.RunProcess(self.builder,
                [ 'clobber', dirname ],
                self.builder.basedir)
            return r.start()
        cmd.doClobber = doClobber

        def doClobber(_, dirname):
            r = runprocess.RunProcess(self.builder,
                [ 'clobber', dirname ],
                self.builder.basedir)
            return r.start()
        cmd.doClobber = doClobber

        def doCopy(_):
            r = runprocess.RunProcess(self.builder,
                [ 'copy', cmd.srcdir, cmd.workdir ],
                self.builder.basedir)
            return r.start()
        cmd.doCopy = doCopy

    def check_sourcedata(self, _, expected_sourcedata):
        """
        Assert that the sourcedata (from the patched functions - see
        make_command) is correct.  Use this as a deferred callback.
        """
        self.assertEqual(self.sourcedata, expected_sourcedata)
        return _

    def set_sourcedata(self, sourcedata):
        self.sourcedata = sourcedata

    def set_path_status(self, path, answer):
        """
        Configure the testPathXxx methods to return appropriate answers
        for a particular path.  ANSWER can be one of 'dir', 'file', or False
        """
        self.testPaths[path] = answer
