# Introduction #

Cherry ConText is a port of the pyConTextKit to a stand alone desktop application using CherryPy as the webserver. Originally we had done this with Twisted, but Twisted had installation problems on Windows.

# Details #

# Future Work #
## Refinements ##
  * Modify Result class to store not only the label, but the lexical, domain, and report values
## Document Classification ##
Trying to figure out how to make a customizable classification scheme through Django. That is, allowing a user to specify rules based on the annotation for classifying a document

  * http://stackoverflow.com/questions/6142025/django-dynamically-add-field-to-a-form
  * http://stackoverflow.com/questions/8209348/is-there-pluggable-online-python-console
  * [http://code.google.com/p/django-dynamic-formset/](.md)

Basically what I'm thinking is defining a formset (read up on this), allow the user to add what list of modifiers are allowable for identifying a document as interesting. The list of modifiers should be obtained from the knowledge bases used to generate the annotation