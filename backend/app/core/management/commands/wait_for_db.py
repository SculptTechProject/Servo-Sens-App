"""
Django command to wait for the database to be available.
"""

import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    """Django command that blocks until the database is reachable."""

    def handle(self, *args, **options):
        """Entrypoint for command execution."""
        self.stdout.write("Waiting for database...")

        db_up = False
        while not db_up:
            try:
                self.check(databases=["default"])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)

            self.stdout.write(self.style.SUCCESS("--------Database available!--------"))
