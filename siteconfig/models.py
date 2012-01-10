'''There are two models for the siteconfig app.

    Website: Keeps specific information about a website for use in templates.

    Division: Model whose instances represent a tree of HTML div and span sections
        of a website.  
'''

from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext


from sorl.thumbnail import ImageField

VALUE_TYPES = (
    ('U',_('Unicode')),
    ('B', _('Boolean')),
    ('I', _('Integer')),
    ('F', _('Float')),
    ('D', _('Date')),
    ('T', _('DateTime'))
)

class Website(models.Model):
    site = models.ForeignKey(Site, default=Site.objects.get_current().id)
    head_html = models.TextField(blank=True,
                help_text=_('This html is inserted in the '
                            'HEAD tag area of the default template.'))
    logo = ImageField(upload_to='logos', blank=True, null=True, 
                help_text=_('An image used by default template'),)
    icon = ImageField(upload_to='icons', blank=True, null=True,
                help_text=_("Used to set the website's favicon " 
                            "by the default template."))
    style_sheet = models.FileField(upload_to='css', blank=True, null=True,
                help_text=_('Used to set the style sheet in the default '
                            'template. '))
    slogan = models.CharField(max_length=200, blank=True,
                help_text=_('A slogan that appears below the logo '
                            'on the default template and stylesheet.'))
    feed_title = models.CharField(max_length=200, blank=True,
                help_text=_('Title of the feed used in the default '
                            'templates and in Publication Manager feed parser.'))
    feed_description = models.TextField(blank=True, 
                help_text=_('Description of the feed used in the default '
                            'templates and in Publication Manager feed parser.'))
    feed_icon_url = models.CharField(max_length=200, blank=True,
                help_text=_('URL of index to feeds on this used in the '
                            'default templates.'))
    footer_html = models.TextField(blank=True,
                help_text=_('This html is inserted in the '
                            'footer area of the default template.'))
    root_division = models.CharField(max_length=200, default='root',
                    help_text=_('Root of the division tree for this website.'))
    cache_period = models.IntegerField(default=300,
                help_text=_('This is the default time in seconds '
                            'that cached areas of the website are '
                            'kept in memory before being reloaded '
                            'from the database.'))
    
    def __unicode__(self):
        return self.site.name
    

    class Meta: 
        verbose_name = _('website')
        verbose_name_plural = _('websites')
        ordering = ['site',]
    

class Setting(models.Model):
    website = models.ForeignKey(Website, default=1)
    key = models.CharField(max_length=200, unique=True)
    value = models.TextField(blank=True)
    type = models.CharField(max_length=1, choices=VALUE_TYPES, default='U')
      

    def __unicode__(self):
        return unicode(self.website) + u':' + self.key
    
    class Meta:
        ordering = ['key']
        verbose_name = 'setting'
        verbose_name_plural = 'settings'
    
class Division(models.Model):
    website = models.ForeignKey(Website, default=1)
    name = models.CharField(max_length=200,
                help_text=_('This will be the name of the id of the div '
                'HTML tag that is generated.'))
    active = models.BooleanField(default=True,
                help_text=_('Inactive records and their children are ignored. '))
    classes = models.CharField(max_length=200, blank=True, null=True,
                help_text=_('Space separated classes for this div tag.'))
    parent = models.ForeignKey('self', blank=True, null=True,
                help_text=_('Division that is the parent of this division. '
                            'Should only be left blank for the root division. '
                            'Careful not to make recursive connections.'))
    level = models.IntegerField(editable=False)
    order = models.IntegerField(default=0,
            help_text=_('The position of this block relative to its '
                        'siblings.'))
    level_order = models.CharField(max_length=9, editable=False)
    pre_template_HTML = models.TextField(blank=True,
            help_text=_('This is HTML that will be generated before the ' 
            'Django template file.'))
    template_filename = models.CharField(max_length=200, blank=True,
            help_text=_('Django template to include ' 
                        'inside this div tag.'))    
    post_template_HTML = models.TextField(blank=True,
            help_text=_('This is HTML that will be generated after the '
                        'Django template file.'))
    suppress_div = models.BooleanField(default=False,
            help_text=_('The div tag will not be used if this is checked.'))
    use_span = models.BooleanField(default=False,
            help_text=_('If checked, an HTML span tag is used instead of div in the '
                        'default templates. '))
    included_pages = models.TextField(blank=True,
            help_text=_('Web pages to include this division in. Specify each '
                        'page on a separate line using relative URL. ' 
                        'Ignored if blank. '))
    excluded_pages = models.TextField(blank=True, 
            help_text=_('Web pages on which not to use this division. '
                        'Ignored if blank.'))
    cache_period = models.IntegerField(default=300,
            help_text=_('This is the default time in seconds '
                        'that the division is cached '
                        'in memory by the default templates before ' 
                        'being reloaded from the database.'))
    
    def get_children(self):
        return Division.objects.filter(parent__name=self.name, active=True)
   
    def tree_display(self, recursion_depth=0):
        
        if recursion_depth > 10:
            return ugettext("Too many recursion levels: Check for circular reference")
        
        if not self.parent:
            return self.name
        else:
            return self.parent.tree_display(recursion_depth+1) + u'.' + self.name 

    tree_display.admin_order_field = 'level_order' 

    def calculate_level(self, recursion_depth=0):        
        if recursion_depth > 10:
            return -1

        if not self.parent:
            return 0
        else:
            return self.parent.calculate_level(recursion_depth+1) + 1
             
    def save(self, *args, **kwargs):
        self.level = self.calculate_level()
        self.level_order = u'%04d.%04d' % (self.level, self.order) 
        super(Division, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.website) + u'.' + self.name
    
    class Meta:
        verbose_name = _('division')
        verbose_name_plural = _('divisions')        
        ordering = ['level_order',]
