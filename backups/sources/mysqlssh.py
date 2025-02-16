import os, os.path
import subprocess
import logging

from backups.sources import backupsource
from backups.sources.source import BackupSource
from backups.exceptions import BackupException

@backupsource('mysql-ssh')
class MySQLSSH(BackupSource):
    def __init__(self, config, type="MySQLSSH"):
        BackupSource.__init__(self, config, type, "sql.gpg")
        self.__common_init__(config)

    def __common_init__(self, config):
        self.sshhost = config['sshhost']
        self.sshuser = config['sshuser']
        self.dbhost = config['dbhost']
        self.dbuser = config['dbuser']
        self.dbpass = config['dbpass']
        self.dbname = config['dbname']
        self.dbport = config.get("dbport") or '3306'
        if 'noevents' in config:
            self.noevents = config['noevents']
        if 'options' in config:
            self.options = config['options']

    def dump(self):
        # Perform dump and remove creds file
        dumpfilename = '%s/%s.sql' % (self.tmpdir, self.id)
        logging.info("Backing up '%s' (%s)..." % (self.name, self.type))
        dumpfile = open(dumpfilename, 'wb')
        dumpargs = [
            'ssh', ('%s@%s' % (self.sshuser, self.sshhost)),
            'mysqldump', ('--host=%s' % self.dbhost), ('--port=%s' % self.dbport), ('--user=%s' % self.dbuser), ('--password=%s' % self.dbpass), '-R']
        if not 'noevents' in dir(self) or not self.noevents:
            dumpargs.append('--events')
        all_databases = False
        if hasattr(self, 'options'):
            for raw_option in self.options.split():
                option = raw_option.strip()
                dumpargs.append(option)
                if not all_databases and option == '--all-databases':
                    all_databases = True
        if not all_databases:
            dumpargs.append('--databases')
            for dbname in self.dbname.split():
                dumpargs.append(dbname)
        logging.debug("Running '%s'" % (" ".join(dumpargs)))
        dumpproc1 = subprocess.Popen(dumpargs, stdout=dumpfile, stderr=subprocess.PIPE)
        if dumpproc1.stdin:
            dumpproc1.stdin.close()
        dumpproc1.wait()
        exitcode = dumpproc1.returncode
        errmsg = dumpproc1.stderr.read()
        if errmsg != b'':
            logging.error(errmsg)
        if exitcode > 1:
            raise BackupException("Error while dumping (exitcode %d): %s" % (exitcode, errmsg))
        dumpfile.close()

        return [dumpfilename, ]
