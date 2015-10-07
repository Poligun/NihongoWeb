from django.core.management.base import BaseCommand, CommandError
from nihongo.question import *

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        #parser.add_argument('arg_name', nargs='', type = int)
        pass

    def handle(self, *args, **options):
        startTest()
        #self.stdout.write('')
