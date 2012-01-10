'''Django admin site configuration for siteconfig app.

Classes:

WebsiteObjectAdmin: Admin for Website model.

DivisionAdmin: Admin for Division model.

'''

import datetime
import time

from django.contrib import admin
from django.utils.translation import ugettext as _
from django.db.models import ImageField
from django import forms

from sorl.thumbnail.admin import AdminImageMixin
from sorl.thumbnail.admin import AdminClearableImageWidget
from sorl.thumbnail.fields import ClearableImageFormField


from siteconfig.models import Website, Division, Setting

class SettingForm(forms.ModelForm):
    model = Setting
    
    def clean(self):
        cleaned_data = self.cleaned_data
        value = cleaned_data.get('value')
        type = cleaned_data.get('type')
        
        if type == 'U':
            pass
        elif type == 'I':
            try:
                int(value)
            except ValueError:
                raise forms.ValidationError(_("Value needs to be an integer"))
        elif type == 'B':
            try:
                bool(value)
            except ValueError:
                raise forms.ValidationError(_("Value needs to be a boolean"))
        elif type == 'F':
            try:
                float(value)
            except ValueError:
                raise forms.ValidationError(_("Value needs to be a float"))
        elif type == 'D':
            try:
                datetime.datetime.strptime(value,"%Y-%m-%d")
            except ValueError:
                raise forms.ValidationError(_("Value needs to be a date in "
                                            "the format YYYY-MM-DD. E.g. 2010-01-31"))            
        elif type == 'T':
            try:
                time.strptime(value,"%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise forms.ValidationError(_("Value needs to be a datetime in "
                                            "the format YYYY-MM-DD HH:MM:SS. E.g. 2010-01-31 09:26:35"))            
        
        return cleaned_data

class SettingInline(admin.TabularInline):
    model = Setting
    setting = SettingForm
    extra = 0
      

class WebsiteObjectAdmin(AdminImageMixin, admin.ModelAdmin):   
    list_display = ['id', '__unicode__', 'logo', 'icon', 'cache_period']
    list_editable = ('cache_period',)
    search_fields = ('site__name', 'site__domain',)
    save_on_top = True
    inlines = [SettingInline]

    formfield_overrides = {
        ImageField: {
            'form_class': ClearableImageFormField,
            'widget': AdminClearableImageWidget,
        },
    }



class SettingAdmin(admin.ModelAdmin):
    form = SettingForm
    list_display = ['website', 'key', 'value', 'type',]
    list_editable = ['key', 'value', 'type',]
    list_filter = ['website']
    

class DivisionAdmin(admin.ModelAdmin):
    list_display = ['name', 'tree_display', 'parent', 'order','active',]
    list_editable = ['parent', 'order', 'active',]
    list_filter = ['website']
    fieldsets = (
        (None, {  
            'fields': ('website', 'name', 'parent', 'order', 'active',),
        }),
        (_('HTML'), {
            'fields': ('pre_template_HTML', 'template_filename', 'post_template_HTML'),
        }),
        (_('Advanced options'), {
            'classes': ['collapse',],
            'fields' : ('classes', 'suppress_div', 'use_span',
                        'included_pages', 'excluded_pages', 
                        'cache_period'),
        })
    )
    
admin.site.register(Website, WebsiteObjectAdmin)    
admin.site.register(Setting, SettingAdmin)
admin.site.register(Division, DivisionAdmin)

