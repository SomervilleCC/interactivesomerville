import datetime
from django.db import models
from django.db.models import signals
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from tagging.fields import TagField

class SharedItemManager(models.Manager):
    
    def __init__(self):
        super(SharedItemManager, self).__init__()
        self.models_by_name = {}
    
    def create_or_update(self, instance, timestamp=None, url=None, tags="", source="INTERACTIVE", source_id="", **kwargs):
        """
        Create or update a SharedItem from some instace.
        """
        # If the instance hasn't already been saved, save it first. This
        # requires disconnecting the post-save signal that might be sent to
        # this function (otherwise we could get an infinite loop).
        if instance._get_pk_val() is None:
            try:
                signals.post_save.disconnect(self.create_or_update, sender=type(instance))
            except Exception, err:
                reconnect = False
            else:
                reconnect = True
            instance.save()
            if reconnect:
                signals.post_save.connect(self.create_or_update, sender=type(instance))
                
        
        # Make sure the item "should" be registered.
        if not getattr(instance, "greenlinable", True):
            return
        
        # Check to see if the timestamp is being updated, possibly pulling
        # the timestamp from the instance.
        if hasattr(instance, "timestamp"):
            timestamp = instance.timestamp
        if timestamp is None:
            update_timestamp = False
            timestamp = datetime.datetime.now()
        else:
            update_timestamp = True
                    
        # Ditto for tags.
        if not tags:
            for f in instance._meta.fields:
                if isinstance(f, TagField):
                    tags = getattr(instance, f.attname)
                    break

        if not url:
            if hasattr(instance,'url'):
                url = instance.url

        # Create the SharedItem object.
        ctype = ContentType.objects.get_for_model(instance)
        item, created = self.get_or_create(
            content_type = ctype, 
            object_id = force_unicode(instance._get_pk_val()),
            defaults = dict(
                share_date = timestamp,
            )
        )        
        item.tags = tags
        if update_timestamp:
            item.share_date = timestamp
            
        # Save and return the item.
        item.save()
        return item
        
    def follow_model(self, model):
        """
        Follow a particular model class, updating associated Items automatically.
        """
        self.models_by_name[model.__name__.lower()] = model
        signals.post_save.connect(self.create_or_update, sender=model)
        
    def get_for_model(self, model):
        """
        Return a QuerySet of only items of a certain type.
        """
        return self.filter(content_type=ContentType.objects.get_for_model(model))
        
    def get_last_update_of_model(self, model, **kwargs):
        """
        Return the last time a given model's items were updated. Returns the
        epoch if the items were never updated.
        """
        qs = self.get_for_model(model)
        if kwargs:
            qs = qs.filter(**kwargs)
        try:
            return qs.order_by('-timestamp')[0].timestamp
        except IndexError:
            return datetime.datetime.fromtimestamp(0)
