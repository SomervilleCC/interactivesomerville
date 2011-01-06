import datetime
import dateutil.parser
import urllib
from django import template
from django.db import models
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType

try:
    from collections import defaultdict
except ImportError:
    defaultdict = None


# Hack until relative imports
Item = models.get_model("greenline_share", "item")

register = template.Library()

def greenlinerender(parser, token):
    """
    Render a greenline_share ``Item`` by passing it through a snippet template.
    
    ::
    
        {% greenlinerender <item> [using <template>] [as <varname>] %}
    
    A sub-template will be used to render the item. Templates will be searched
    in this order:

        * The template given with the ``using <template>`` clause, if given.
    
        * ``greenline_share/snippets/<classname>.html``, where ``classname`` is the
          name of the specific item class (i.e. ``photo``).
          
        * ``greenline_share/snippets/item.html``.
        
    The template will be passed a context containing:
    
        ``item``
            The greenline_share ``Item`` object
    
        ``object``
            The actual object (i.e. ``item.object``).
            
    The rendered content will be displayed in the template unless the ``as
    <varname>`` clause is used to redirect the output into a context variable.
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError("%r tag takes at least one argument" % bits[0])
    
    item = bits[1]
    args = {}
    
    # Parse out extra clauses if given
    if len(bits) > 2:
        biter = iter(bits[2:])
        for bit in biter:
            if bit == "using":
                args["using"] = biter.next()
            elif bit == "as":
                args["asvar"] = biter.next()
            else:
                raise template.TemplateSyntaxError("%r tag got an unknown argument: %r" % (bits[0], bit))
            
    return GreenlinerenderNode(item, **args)
greenlinerender = register.tag(greenlinerender)
    
class GreenlinerenderNode(template.Node):
        
    def __init__(self, item, using=None, asvar=None):
        self.item = item
        self.using = using
        self.asvar = asvar
        
    def render(self, context):
        try:
            item = template.resolve_variable(self.item, context)
        except template.VariableDoesNotExist:
            return ""
                
        if isinstance(item, Item):
            object = item.object
        
        # If the item isn't an Item, try to look one up.
        else:
            object = item
            ct = ContentType.objects.get_for_model(item)
            try:
                item = Item.objects.get(content_type=ct, object_id=object._get_pk_val())
            except Item.DoesNotExist:
                return ""
                
        # Figure out which templates to use
        template_list = [
            "greenline/snippets/%s.html" % type(object).__name__.lower(), 
            "greenline/snippets/item.html"
        ]
        if self.using:
            try:
                using = template.resolve_variable(self.using, context)
            except template.VariableDoesNotExist:
                pass
            else:
                template_list.insert(0, using)
                
        # Render content, and save to self.asvar if requested
        context.push()
        context.update({
            "item" : item,
            "object" : object
        })
        rendered = render_to_string(template_list, context)
        context.pop()
        if self.asvar:
            context[self.asvar] = rendered
            return ""
        else:
            return rendered
            
def get_greenline_share_items(parser, token):
    """
    Load greenline_share ``Item`` objects into the context.In the simplest mode, the
    most recent N items will be returned.
    
    ::
    
        {# Fetch 10 most recent items #}
        {% get_greenline_share_items limit 10 as items %}
        
    Newer items will be first in the list (i.e. ordered by timstamp descending)
    unless you ask for them to be reversed::
    
        {# Fetch the 10 earliest items #}
        {% get_greenline_share_items limit 10 reversed as items %}
    
    You can also fetch items between two given dates::
    
        {% get_greenline_share_items between "2007-01-01" and "2007-01-31" as items %}
        
    Dates can be in any format understood by ``dateutil.parser``, and can of
    course be variables. Items must be limited in some way; you must either pass
    ``limit`` or ``between``.
    
    Dates can also be the magic strings "now" or "today"::
    
        {% get_greenline_share_items between "2007-01-01" and "today" as items %}
    
    You can also limit items by type::
    
        {# Fetch the 10 most recent videos and photos #}
        {% get_greenline_share_items oftype video oftype photo limit 10 as items %}
    
    ``oftype`` can be given as many times as you like; only those types will be
    returned. The arguments to ``oftype`` are the lowercased class names of
    greenline_share'd items. 
    
    You can similarly exclude types using ``excludetype``::
    
        {# Fetch the 10 most items that are not videos #}
        {% get_greenline_share_items excludetype video limit 10 as items %}
        
    You can give ``excludetype`` as many times as you like, but it is an error
    to use both ``oftype`` and ``excludetype`` in the same tag invocation.
    """
    
    # Parse out the arguments
    bits = token.split_contents()
    tagname = bits[0]
    bits = iter(bits[1:])
    args = {}
    for bit in bits:
        try:
            if bit == "limit":
                try:
                    args["limit"] = int(bits.next())
                except ValueError:
                    raise template.TemplateSyntaxError("%r tag: 'limit' requires an integer argument" % tagname)
            elif bit == "between":
                args["start"] = bits.next()
                and_ = bits.next()
                args["end"] = bits.next()
                if and_ != "and":
                    raise template.TemplateSyntaxError("%r tag: expected 'and' in 'between' clause, but got %r" % (tagname, and_))
            elif bit == "oftype":
                args.setdefault("oftypes", []).append(bits.next())
            elif bit == "excludetype":
                args.setdefault("excludetypes", []).append(bits.next())
            elif bit == "reversed":
                args["reversed"] = True
            elif bit == "as":
                args["asvar"] = bits.next()
            else:
                raise template.TemplateSyntaxError("%r tag: unknown argument: %r" % (tagname, bit))
        except StopIteration:
            raise template.TemplateSyntaxError("%r tag: an out of arguments when parsing %r clause" % (tagname, bit))
    
    # Make sure "as" was given
    if "asvar" not in args:
        raise template.TemplateSyntaxError("%r tag: missing 'as'" % tagname)
    
    # Either "limit" or "between" has to be specified
    if "limit" not in args and ("start" not in args or "end" not in args):
        raise template.TemplateSyntaxError("%r tag: 'limit' or a full 'between' clause is required" % tagname)
    
    # It's an error to have both "oftype" and "excludetype"
    if "oftype" in args and "excludetype" in args:
        raise template.TemplateSyntaxError("%r tag: can't handle both 'oftype' and 'excludetype'" % tagname)
    
    # Each of the "oftype" and "excludetype" arguments has be a valid model
    for arg in ("oftypes", "excludetypes"):
        if arg in args:
            model_list = []
            for name in args[arg]:
                try:
                    model_list.append(Item.objects.models_by_name[name])
                except KeyError:
                    raise template.TemplateSyntaxError("%r tag: invalid model name: %r" % (tagname, name))
            args[arg] = model_list
    
    return GetGreenlinerollItemsNode(**args)
get_greenline_share_items = register.tag(get_greenline_share_items)

class GetGreenlinerollItemsNode(template.Node):
    def __init__(self, asvar, limit=None, start=None, end=None, oftypes=[], excludetypes=[], reversed=False):
        self.asvar = asvar
        self.limit = limit
        self.start = start
        self.end = end
        self.oftypes = oftypes
        self.excludetypes = excludetypes
        self.reversed = reversed
        
    def render(self, context):
        qs = Item.objects.all()
        
        # Handle start/end dates if given
        if self.start:
            start = self.resolve_date(self.start, context)
            end = self.resolve_date(self.end, context)
            if start is None or end is None:
                return ""
            qs = qs.filter(timestamp__range=(start, end))
            
        # Handle types
        CT = ContentType.objects.get_for_model
        if self.oftypes:
            qs = qs.filter(content_type__id__in=[CT(m).id for m in self.oftypes])
        if self.excludetypes:
            qs = qs.exclude(content_type__id__in=[CT(m).id for m in self.excludetypes])
            
        # Handle reversed
        if self.reversed:
            qs = qs.order_by("timestamp")
        else:
            qs = qs.order_by("-timestamp")
            
        # Handle limit
        if self.limit:
            qs = qs[:self.limit]
            
        # Set the context
        context[self.asvar] = list(qs)
        return ""
        
    def resolve_date(self, d, context):
        """Resolve start/end, handling literals"""
        try:
            d = template.resolve_variable(d, context)
        except template.VariableDoesNotExist:
            return None
        
        # Handle date objects
        if isinstance(d, (datetime.date, datetime.datetime)):
            return d
        
        # Assume literals or strings
        if d == "now":
            return datetime.datetime.now()
        if d == "today":
            return datetime.date.today()
        try:
            return dateutil.parser.parse(d)
        except ValueError:
            return None

def get_greenline_share_recent_traffic(parser, token):
    oftypes = []
    bits = token.split_contents()
    if len(bits) < 4 or len(bits) > 5:
        raise template.TemplateSyntaxError("%r tag takes three arguments" % bits[0])
    elif bits[2] != 'as':
        raise template.TemplateSyntaxError("second argument to %r tag should be 'as'" % bits[0])
    if len(bits) > 4:
        oftypes = bits[4]
    return GreenlineRecentTrafficNode(bits[1],bits[3],oftypes)
get_greenline_share_recent_traffic = register.tag(get_greenline_share_recent_traffic)

class GreenlineRecentTrafficNode(template.Node):
    def __init__(self, days, context_var, oftypes=[]):
        self.days = int(days)
        self.oftypes = oftypes.split(",")
        self.context_var = context_var

    def render(self, context):
        CT = ContentType.objects.get_for_model
        dt_start = datetime.date.today()
        data = []

        if self.oftypes:
            if defaultdict:
                data = defaultdict(list)
            else:
                for item_type in self.oftypes: data[item_type] = []

        for offset in range(0,self.days):
            dt = dt_start - datetime.timedelta(days=offset)
            step = datetime.timedelta(days=1)
            if self.oftypes:
                for item_type in self.oftypes:
                    qs = Item.objects.filter(content_type__id=CT(Item.objects.models_by_name[item_type]).id)
                    data[item_type].append(
                        qs.filter(timestamp__range=(dt-step,dt)).count()
                        )
            else:
                data.append(
                    Item.objects.filter(timestamp__range=(dt-step,dt)).count()
                    )

        context[self.context_var] = data
        return ''
