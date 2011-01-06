import logging
import optparse
import greenline.providers
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        optparse.make_option(
            "-p", "--provider", 
            dest="providers", 
            action="update", 
            help="Only use certain provider(s)."
        ),
        optparse.make_option(
            "-l", "--list-providers", 
            action="store_true", 
            help="Display a list of active data providers."
        ),
    )
    
    def handle(self, *args, **options):
        level = {
            '0': logging.WARN, 
            '1': logging.INFO, 
            '2': logging.DEBUG
        }[options.get('verbosity', '0')]
        logging.basicConfig(level=level, format="%(name)s: %(levelname)s: %(message)s")

        if options['list_providers']:
            self.print_providers()
            return 0

        if options['providers']:
            for provider in options['providers']:
                if provider not in self.available_providers():
                    print "Invalid provider: %r" % provider
                    self.print_providers()
                    return 0

        greenline.providers.update(options['providers'])

    def available_providers(self):
        return greenline.providers.active_providers()

    def print_providers(self):
        available = sorted(self.available_providers().keys())
        print "Available data providers:"
        for provider in available:
            print "   ", provider
