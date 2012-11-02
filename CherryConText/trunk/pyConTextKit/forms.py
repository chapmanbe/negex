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
This module contains the forms that are used in the pyConTextKit application.
"""
from django import forms
from django.forms import ModelForm
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from django.utils.safestring import mark_safe
"""
	**TODO**
		Eventually remove import of itemDatum
"""
from pyConTextKit.models import Report, Items

class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
            """Outputs radios"""
            return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

UNCERTAINTY_CHOICES = (('separate_uncertainty','distinguish certainty from uncertainty'), ('allow_uncertainty','do not distinguish certainty from uncertainty'), ('no_uncertainty','do not include instances of uncertainty'))

class SearchForm(forms.Form):
    """
    A form that takes the input for a simple search.
    """
    term = forms.CharField(label = 'Search term', required=False)

class RunForm(forms.Form):
    """
    This form enables the user to specify settings for Annotate (formerly called "Analyze").
    """
    outputLabel = forms.CharField(max_length=150,label='Output Label')
    dataset = forms.ChoiceField(label = 'Report dataset', choices=[], required=False)
    #category = forms.CharField(label = 'Target category', required=False)
    #limit = forms.IntegerField(required=False)
    label = forms.ChoiceField(label = 'Label of linguistic', choices=[], required=False)
    labelDomain = forms.ChoiceField(label = 'Label of domain', choices=[], required=False)
    def __init__(self, *args, **kwargs):
        super(RunForm, self).__init__(*args, **kwargs)
        self.fields['dataset'].choices = Report.objects.all().values_list("dataset","dataset").distinct()
        self.fields['label'].choices = Items.objects.all().filter(lex_type='linguistic').values_list("label","label").distinct()
        self.fields['labelDomain'].choices = Items.objects.all().filter(lex_type='domain').values_list("label","label").distinct()

class DocClassForm(forms.Form):
    """
    This form accepts user input for classifying documents.
    """
    limit_pos = forms.BooleanField(label="Positive Findings Only", required=False,initial=True)
    limit_new = forms.BooleanField(label="New Findings Only", required=False,initial=True)
    uncertainty = forms.ChoiceField(widget=forms.RadioSelect, choices=UNCERTAINTY_CHOICES,initial={'separate_uncertainty','separate_uncertainty'})
    def __init__(self, *args, **kwargs):
        super(DocClassForm, self).__init__(*args, **kwargs)

"""
	UPDATED 7/27/12 G.D.
	Changed model from itemDatum to Lexical
"""
class itemForm(forms.ModelForm):
    """
    This form for the Lexical class employs the default ModelForm.
    """
    CHOICES = (
    	('domain','Domain'),
    	('linguistic','Linguistic')
    )
    lex_type = forms.ChoiceField(label="Lexicon Type",choices=CHOICES, widget=forms.RadioSelect(renderer=HorizRadioRenderer))
    label = forms.CharField(label="Name")
    class Meta:
        model = Items
        exclude = ('show',)

class ReportForm(forms.Form):
    """
    This form enables the user to select a report to view.
    """
    REPORT_CHOICES = [(i.id, i.id) for i in Report.objects.all()]
    REPORT_CHOICES.insert(0, ('', '-- choose a report number first --'))

    id = forms.ChoiceField(choices=REPORT_CHOICES, widget=forms.Select(attrs={'onchange':'get_report_number();'}))
    text = forms.CharField()

class EditReport(forms.ModelForm):

	class Meta:
		report = Report

"""
class UploadDatabase(forms.Form):
	label = forms.CharField(max_length=250)
	csvfile  = forms.FileField()
"""

class UploadDatabaseReports(forms.Form):
    dataset = forms.CharField(max_length=250, required=True)
    csvfile  = forms.FileField(label="CSV File", required=True)

class UploadDatabaseLexicon(forms.Form):
    label = forms.CharField(label="Name",max_length=250, required=True)
    csvfile  = forms.FileField(label="CSV File", required=True)
    CHOICES = (
    	('domain','Domain'),
    	('linguistic','Linguistic')
    )
    like = forms.ChoiceField(label="Lexicon Type",choices=CHOICES, widget=forms.RadioSelect())