from django.db.models import fields
from django.db import IntegrityError
from greenline.parsers import slugify
 
class AutoSlugField(fields.SlugField):
    """
    A SlugField that automatically populates itself at save-time from
    the value of another field.
 
    Accepts argument populate_from, which should be the name of a single
    field which the AutoSlugField will populate from (default = 'name').
 
    By default, also sets unique=True, db_index=True, and
    editable=False.
 
    Accepts additional argument, overwrite_on_save.  If True, will
    re-populate on every save, overwriting any existing value.  If
    False, will not touch existing value and will only populate if
    slug field is empty.  Default is False.
 
    """
    def __init__ (self, populate_from='name', overwrite_on_save=False,
                  *args, **kwargs):
        kwargs.setdefault('unique', True)
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('editable', False)
        self._save_populate = populate_from
        self._overwrite_on_save = overwrite_on_save
        super(AutoSlugField, self).__init__(*args, **kwargs)
 
    def _populate_slug(self, model_instance):
        value = getattr(model_instance, self.attname, None)
        prepop = getattr(model_instance, self._save_populate, None)
        if (prepop is not None) and (not value or self._overwrite_on_save):
            value = slugify(prepop)
            setattr(model_instance, self.attname, value)
        return value
 
    def contribute_to_class (self, cls, name):
        # apparently in inheritance cases, contribute_to_class is called more
        #  than once, so we have to be careful not to overwrite the original
        #  save method.
        if not hasattr(cls, '_orig_save'):
            cls._orig_save = cls.save
            def _new_save (self_, *args, **kwargs):
                counter = 1
                orig_slug = self._populate_slug(self_)
                slug_len = len(orig_slug)
                if slug_len > self.max_length:
                    orig_slug = orig_slug[:self.max_length]
                    slug_len = self.max_length
                setattr(self_, name, orig_slug)
                while True:
                    try:
                        self_._orig_save(*args, **kwargs)
                        break
                    except IntegrityError, e:
                        # check to be sure a slug fight caused the IntegrityError
                        s_e = str(e)
                        if name in s_e and 'unique' in s_e:
                            counter += 1
                            max_len = self.max_length - (len(str(counter)) + 1)
                            if slug_len > max_len:
                                orig_slug = orig_slug[:max_len]
                            setattr(self_, name, "%s-%s" % (orig_slug, counter))
                        else:
                            raise
            cls.save = _new_save
        super(AutoSlugField, self).contribute_to_class(cls, name)