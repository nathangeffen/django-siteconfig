'''Utility functions (currently only one)

    get_settings: - returns all settings for the active website. 
                    Tries to get them from cache before accessing db.

    get_setting: - returns a setting. If it doesn't exist
                    returns alternate value
'''

import datetime

from django.core.cache import cache
from django.contrib.sites.models import Site

from models import Website

def get_settings():
    settings_dict = cache.get('_sc_website_settings')

    if settings_dict:
        return settings_dict
    else:
        settings_dict = {'website_settings' : {}}
    
    website = Website.objects.get(site=Site.objects.get_current())
    
    settings = website.setting_set.all()

    for setting in settings:
        if setting.type == 'U':
            settings_dict['website_settings'][setting.key] = setting.value
        elif setting.type == 'I':
            settings_dict['website_settings'][setting.key] = int(setting.value)
        elif setting.type == 'F':
            settings_dict['website_settings'][setting.key] = float(setting.value)
        elif setting.type == 'B':
            settings_dict['website_settings'][setting.key] = bool(setting.value)
        elif setting.type == 'D':
            settings_dict['website_settings'][setting.key] = datetime.datetime.strptime(setting.value,"%Y-%m-%d")
        elif setting.type == 'T':
            settings_dict['website_settings'][setting.key] = datetime.datetime.strptime(setting.value,"%Y-%m-%d")
            
    cache.set('_sc_website_settings', settings_dict, website.cache_period)

    return settings_dict

def get_setting(setting, alternative_value=None):
    try:
        return get_settings()['website_settings'][setting]
    except KeyError:
        if alternative_value:
            return alternative_value
        else:
            raise KeyError
        