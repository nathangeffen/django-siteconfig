'''Siteconfig implements a template tag called showdivision. 

It is used to dynamically and recursively load an HTML div (or span) section
corresponding to an instance of the Division model.   
See the division_item.html template for an example of how it is used.

'''

from django import template
from siteconfig.models import Division
import re

register = template.Library()

@register.inclusion_tag('division_item.html', takes_context=True)
def show_division(context, division):
    ''' Used to dynamically and recursively load an HTML div (or span) section
        corresponding to an instance of the Division model.

        To use the tag in this template put the following line in before using the tag:
        {% load siteconfigtags %}
        Then use the tag as follows:
        {% show_division division %}
        where division is the name of a Division instance in the context.
        
        See the division_item.html template for an example. For most use
        cases you should not need to change this template.             
    '''
    
    def checkpatternmatches(patterns):
        '''Takes a list of regular expressions separated by
        white space and checks if any of them match the request path. 
        '''
        reg_exprs = [re.compile(s) for s in patterns.split()]        
        return True in [(i.match(path)!=None) for i in reg_exprs]
        
    
    if not isinstance(division, Division):
        raise template.TemplateSyntaxError, 'Given argument must be a Division object.'
    
    render_division = True
    
    path = context['request'].path
    
    if division.included_pages:
        if not checkpatternmatches(division.included_pages):
            render_division = False        
    
    if division.excluded_pages:
        if checkpatternmatches(division.excluded_pages):
            render_division = False
            
    context['render_division'] = render_division    
    context['division'] = division
    
    return context


class TemplateStringNode(template.Node):
    def __init__(self, template_string):
        self.template_string = template.Variable(template_string)

    def render(self, context):
        actual_string = self.template_string.resolve(context)
        t = template.Template(actual_string)
        c = template.Context(context)
        return t.render(c)

@register.tag(name="template_string")
def do_template_string(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, template_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % tag_name
    return TemplateStringNode(template_string)


