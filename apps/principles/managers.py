import datetime
from django.db.models import Manager

class EntryManager(Manager):

    """
    Model manager for the Principle Entry model. Overrides the default
    latest() method so it returns the latest published entry, and adds a
    published() method that returns only active entries.
    """

    def latest(self, field_name=None):
        """Return the latest published entry."""
        return self.published().latest(field_name)

    def published(self, **kwargs):
        """
        A QuerySet that contains only those entries with a status of "active" 
        and a created_at date earlier than now.
        """
        from principles.models import Entry
        return self.get_query_set().filter(status=1,
            published__lte=datetime.datetime.now, **kwargs)
