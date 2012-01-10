'''Three context_processors are provided:

    Use either website or rootdivision in your settings 
    TEMPLATE_CONTEXT_PROCESSORS variable, because website is a subset of 
    rootdivision. 
    
    For sites making full use of the siteconfig app, that would be rootdivision.
    
    website: Returns a dictionary containing the Website model corresponding to the current site.
             The context variable name is website. 

    rootdivision: Returns the above plus a context variable called
              division which is the root Division instance for the website. 

    websitesettings: Returns dictionary containing website settings stored in 
            the database.

'''

from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

from siteconfig.utils import get_settings  
from siteconfig.models import Website, Division


def website(request=None):
    '''Returns a dictionary containing the Website model corresponding to the current site.
       
       The context variable name is website.
    '''
    website_dict = cache.get('_sc_website_context')
    
    if website_dict:
        return website_dict
    else:
        try:
            website_context = Website.objects.get(site=Site.objects.get_current())
        except ObjectDoesNotExist:
            # No website in database, so create a temp one
            website_context = Website(pk=1, site=Site.objects.get_current()) 

    website_dict = {'website' : website_context}

    cache.set('_sc_website_context', website_dict , website_context.cache_period)    
    return website_dict


def rootdivision(request):
    '''Returns the website context as well as a context variable called
       division which is the root Division instance for the website.
    '''
              
    website_dict = cache.get('_sc_website_dict')
    
    if website_dict:
        return website_dict
    else:
        website_dict = website(request)

        try:
            website_context = website_dict['website']
        except KeyError:
            website_context = None 
        
        if website_context:
            cache_period = website_context.cache_period
            try:
                root_division = Division.objects.get(
                                website=website_context, 
                                name=website_context.root_division,
                                active=True)                
            except ObjectDoesNotExist:
                root_division = None
        else:
            cache_period = 300
            root_division = None

    website_dict['division'] = root_division
    cache.set('_sc_website_dict', website_dict, cache_period)

    return website_dict

def websitesettings(request):
    '''Returns user-defined settings stored 
    in the database for this website
    '''

    return get_settings()
    
