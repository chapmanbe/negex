#Copyright 2010 Annie T. Chen
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

"""
This specifies the admin classes.
"""
from pyConTextKit.models import *
from django.contrib import admin

class itemDatumAdmin(admin.ModelAdmin):
    list_display = ('literal','category','re')
    search_fields = ['literal']
    fieldsets = (
        (None, {
            'fields': ('literal', 'category', 're', 'rule','creator','label'),
            'description': 'This application employs Python regular expressions. Refer to the key below for guidance on how to create regular expressions.<br>\s: space<br>|: or<br>\w: alphanumeric character or underscore (equivalent to [a-zA-Z0-9_])<br>*: match one or more repetitions of the preceding regular expression<br>?: matches 0 or 1 of the preceding regular expressions'}),
    )

class ReportAdmin(admin.ModelAdmin):
    fields = ['dataset','reportid']#also, reportType got rid of dataset from the this field
    list_display = ('dataset','reportid')#also, reportType got rid of dataset at first position

class AlertAdmin(admin.ModelAdmin):
    fields = ['reportid','category','alert','report']
    list_display = ('reportid','category','alert','report')
    list_filter = ['alert']

class ResultAdmin(admin.ModelAdmin):
    fields = ['label','path']
    list_display = ('label','path')

admin.site.register(Items, itemDatumAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(Result, ResultAdmin)
