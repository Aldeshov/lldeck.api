import os.path

from django.core.management import BaseCommand
from django.core.management.utils import get_random_secret_key

from lldeck.settings import BASE_DIR


class Command(BaseCommand):
    help = 'Setup required settings of this project'

    file_name = '.env'
    file_path = os.path.join(BASE_DIR, file_name)
    secret_key = get_random_secret_key()

    defaults__allowed_hosts = 'localhost,127.0.0.1'
    defaults__cors_allowed_origins = 'http://localhost,http://127.0.0.1'

    defaults__db_name = 'postgres'
    defaults__db_username = 'postgres'
    defaults__db_password = 'postgres'
    defaults__db_host = 'localhost'
    defaults__db_port = '5432'

    def add_arguments(self, parser):
        parser.add_argument('-N', '--db_name', type=str, help='Define a name of database', )
        parser.add_argument('-H', '--db_host', type=str, help='Define a host of database', )
        parser.add_argument('-P', '--db_port', type=str, help='Define a port of database', )
        parser.add_argument('-u', '--db_username', type=str, help='Define a username for database access', )
        parser.add_argument('-p', '--db_password', type=str, help='Define a username for database access', )

        parser.add_argument('-d', '--defaults', action="store_true", help="Sets up defaults for project", )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('┌──────────────────────────────────────────────────────────┐'))
        self.stdout.write(self.style.SUCCESS('│ Welcome to the LLDeck project settings setup management! │'))
        self.stdout.write(self.style.SUCCESS('└──────────────────────────────────────────────────────────┘'))
        self.stdout.write()

        try:
            if options['defaults']:
                self.stdout.write(self.style.WARNING('Setting up project defaults below (will overwrite if exists):'))
                self.stdout.write('ALLOWED_HOSTS: %s' % self.defaults__allowed_hosts)
                self.stdout.write('CORS_ALLOWED_ORIGINS: %s' % self.defaults__cors_allowed_origins)
                self.stdout.write(
                    'POSTGRESQL_DB_DEFAULT_NAME: %s' %
                    (self.defaults__db_name if not options['db_name'] else options['db_name'])
                )
                self.stdout.write(
                    'POSTGRESQL_DB_DEFAULT_HOST: %s' %
                    (self.defaults__db_host if not options['db_host'] else options['db_host'])
                )
                self.stdout.write(
                    'POSTGRESQL_DB_DEFAULT_PORT: %s' %
                    (self.defaults__db_port if not options['db_port'] else options['db_port'])
                )
                self.stdout.write(
                    'POSTGRESQL_DB_DEFAULT_USERNAME: %s' %
                    (self.defaults__db_username if not options['db_username'] else options['db_username'])
                )
                self.stdout.write(
                    'POSTGRESQL_DB_DEFAULT_PASSWORD: %s' %
                    (self.defaults__db_password if not options['db_password'] else options['db_password'])
                )
                self.stdout.write()

                answer = str(input('Do you want to continue? [yY (Yes) / nN (No)]: ')).lower()
                if answer == 'y' or answer == 'yes':
                    successful = self.setup(
                        force=True,
                        secret_key=self.secret_key,
                        allowed_hosts=self.defaults__allowed_hosts,
                        cors_allowed_origins=self.defaults__cors_allowed_origins,
                        database_name=self.defaults__db_name if not options['db_name'] else options['db_name'],
                        database_host=self.defaults__db_host if not options['db_host'] else options['db_host'],
                        database_port=self.defaults__db_port if not options['db_port'] else options['db_port'],
                        database_username=self.defaults__db_username if not options['db_username'] else options[
                            'db_username'],
                        database_password=self.defaults__db_password if not options['db_password'] else options[
                            'db_password'],
                    )
                    if successful:
                        self.stdout.write(self.style.SUCCESS('Settings have been written successfully!'))
                    else:
                        self.stdout.write(self.style.ERROR('There was an error while writing settings.'))

                elif answer == 'n' or answer == 'no':
                    self.stdout.write(self.style.WARNING('Operation canceled.'))
                else:
                    self.stdout.write(self.style.NOTICE('Unknown answer specified.'))
            else:
                self.stdout.write(self.style.WARNING('Setting up project configs (will overwrite if exists)'))

                response = str(input('ALLOWED_HOSTS (default=%s): ' % self.defaults__allowed_hosts))
                allowed_hosts = response if response else self.defaults__allowed_hosts

                response = str(input('CORS_ALLOWED_ORIGINS (default=%s): ' % self.defaults__cors_allowed_origins))
                cors_allowed_origins = response if response else self.defaults__cors_allowed_origins

                response = str(input('DATABASE_NAME (default=%s): ' % self.defaults__db_name))
                database_name = response if response else self.defaults__db_name

                response = str(input('DATABASE_HOST (default=%s): ' % self.defaults__db_host))
                database_host = response if response else self.defaults__db_host

                response = str(input('DATABASE_PORT (default=%s): ' % self.defaults__db_port))
                database_port = response if response else self.defaults__db_port

                response = str(input('DATABASE_USERNAME (default=%s): ' % self.defaults__db_username))
                database_username = response if response else self.defaults__db_username

                response = str(input('DATABASE_PASSWORD (default=%s): ' % self.defaults__db_password))
                database_password = response if response else self.defaults__db_password

                self.stdout.write()
                self.stdout.write(self.style.WARNING('Got all required information. Start setup?'))
                input('Press ENTER to continue, Ctrl+C to cancel.')

                successful = self.setup(
                    force=True,
                    secret_key=self.secret_key,
                    allowed_hosts=allowed_hosts,
                    cors_allowed_origins=cors_allowed_origins,
                    database_name=database_name,
                    database_host=database_host,
                    database_port=database_port,
                    database_username=database_username,
                    database_password=database_password,
                )
                if successful:
                    self.stdout.write(self.style.SUCCESS('Settings have been written successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('There was an error while writing settings.'))

        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR('\nOperation canceled by keyboard interrupt!'))

    def setup(self, force=False, **kwargs):
        if not force and os.path.exists(self.file_path):
            return False

        with open(self.file_path, "w") as file:
            strings = str()
            strings += "SECRET_KEY = '%s'\n" % kwargs['secret_key']
            strings += "ALLOWED_HOSTS = '%s'\n" % kwargs['allowed_hosts']
            strings += "CORS_ALLOWED_ORIGINS = '%s'\n" % kwargs['cors_allowed_origins']
            strings += "DATABASE_NAME = '%s'\n" % kwargs['database_name']
            strings += "DATABASE_USERNAME = '%s'\n" % kwargs['database_username']
            strings += "DATABASE_PASSWORD = '%s'\n" % kwargs['database_password']
            strings += "DATABASE_HOST = '%s'\n" % kwargs['database_host']
            strings += "DATABASE_PORT = '%s'\n" % kwargs['database_port']
            file.write(strings)
            return True
