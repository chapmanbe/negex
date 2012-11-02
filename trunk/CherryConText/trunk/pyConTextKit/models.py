#Copyright 2010-2012 Brian E. Chapman, Annie T. Chen, Glenn Dayton IV,
# Rutu Mulkar-Mehta
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
This module contains the models that are used in the pyConTextKit application.

This application uses the following models:

1) itemDatum: extraction criteria

2) itemDatumSet: a table that stores default extraction criteria settings for
application (e.g. on/off)

3) Report: the reports used by the application

4) Alert: contains a document-level classifications for extracted instances

5) Result: contains each instance identified when Annotate function is run

Note: The get_all_fields method is redundant. A model should be defined for this
application, and then have the other models inherit from it.
"""
from django.db import models
from django.contrib.auth.models import User
import time

# Stores both lexical and Domain data
class Items(models.Model):
    creator = models.ForeignKey(User)
    label = models.CharField(max_length=250)
    category = models.CharField(max_length=250)
    literal = models.CharField(max_length=250)
    re = models.CharField(max_length=250,blank=True)
    re.help_text='<a target="_blank" href="http://www.dhtmlgoodies.com/scripts/regular-expression/regular-expression.html">Regex builder</a>'
    #rule = models.CharField(max_length=250,blank=True)
    RULE_CHOICES = (
        ('forward','Forward'),
        ('backward','Backward'),
        ('terminate','Terminate'),
        ('bidirectional','Bidirectional'),
    )
    rule = models.CharField(max_length=250, choices=RULE_CHOICES, blank=True)
    TYPE_CHOICES = (
    	('domain','Domain'),
    	('linguistic','Linguistic')
    )
    lex_type = models.CharField(max_length=250, choices=TYPE_CHOICES)
    SHOW_CHOICES = (
    	('1','Show'),
    	('0','Hide')
    )
    show = models.CharField(max_length=1, choices=SHOW_CHOICES)
    def __unicode__(self):
        return self.literal

class Report(models.Model):
    dataset = models.CharField(max_length=250)
    reportid = models.TextField()
    report = models.TextField()
    # add label functionality
    def __unicode__(self):
        return str(self.reportid)
    def get_all_fields(self):
        """Returns a list of all field names on the instance."""
        fields = ()
        for f in self._meta.fields:

            fname = f.name
            # resolve picklists/choices, with get_xyz_display() function
            get_choice = 'get_'+fname+'_display'
            if hasattr( self, get_choice):
        	    value = getattr( self, get_choice)()
            else:
                try :
            	    value = getattr(self, fname)
                except User.DoesNotExist:
                    value = None

            # only display fields with values and skip some fields entirely
            if f.editable and value and f.name not in ('id', 'status', 'workshop', 'user', 'complete') :

                fields.append(
                  {
                   'label':f.verbose_name,
                   'name':f.name,
                   'value':value,
                  }
                )
        return fields

# Can we generalize the Alert class to be an application class that is built by
# the user?
class Alert(models.Model):
    reportid = models.IntegerField()
    category = models.TextField()
    alert = models.IntegerField()
    report = models.TextField()
    def __unicode__(self):
        return str(self.reportid)
    def get_all_fields(self):
        """Returns a list of all field names on the instance."""
        fields = ()
        for f in self._meta.fields:

            fname = f.name
            # resolve picklists/choices, with get_xyz_display() function
            get_choice = 'get_'+fname+'_display'
            if hasattr( self, get_choice):
                value = getattr( self, get_choice)()
            else:
                try :
                    value = getattr(self, fname)
                except User.DoesNotExist:
                    value = None

            # only display fields with values and skip some fields entirely
            if f.editable and value and f.name not in ('id', 'status', 'workshop', 'user', 'complete') :

                fields.append(
                  {
                   'label':f.verbose_name,
                   'name':f.name,
                   'value':value,
                  }
                )
        return fields

# Don't know that we want to store this back into the database
# How would we make results general?
class Result(models.Model):
    label = models.CharField(max_length=250)
    date = models.CharField(max_length=35)
    path = models.CharField(max_length=1000)
    #Do we want to store information about what domain and lexical were used?

    def __unicode__(self):
	    return str(self.reportid)