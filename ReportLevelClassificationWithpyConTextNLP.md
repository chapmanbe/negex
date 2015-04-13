#Some ideas about doing report-level classification with pyConTextNLP.

# Introduction #

pyConTextNLP is a Python package for sentence level markup of text. It is reasonable to ask how to use the code for document-level classification.

First, while pyConTextNLP marks up text on a sentence level, meaning that modifiers and targets only interact within a sentence, the code actually has a concept of a document and document sections. Each sentence markup is added as a node in a document graph as a child node to a section node. By default the section node is set to "root."

In applications we have been developing we have focused on a "maximum" principle. For example, the most positive finding in a sentence within the document is taken to be the finding value for the document. More generally, we have been specifying a schema where the schema may combine multiple categories (e.g. disease state, uncertainty, temporality) into one ordinal scale, and then our application classifies a document based on the maximum schema score observed at a sentence level.

# Schema #
As we have used them, a schema consists of ordered list of values. Each value is a triplet consisting of
  1. A Numeric value used for comparing schema values
  1. A label summarizing the meaning of the value
  1. A logical rule describing how that value is realized

The logical rules are written as Python expressions relating pyConTextNLP categories defined in lexical and domain knowledge bases to each other through "and" and "or" statements. These rules are modified by the actual value
```
# Lines that start with the # symbol are comments and are ignored
#The schema consists of a numeric value, followed by a label (e.g. "AMBIVALENT"), followed by a Python express that can 
#evaluate to True or False
#The Python expression uses LABELS from the rules. processReports.py will substitute the LABEL with any matched 
#values identified from the corresponding rules
1,AMBIVALENT,DISEASE_STATE == 2
2,Negative/Certain/Acute,DISEASE_STATE == 0 and CERTAINTY_STATE == 1
3,Negative/Uncertain/Chronic,DISEASE_STATE == 0 and CERTAINTY_STATE == 0 and ACUTE_STATE == 0
4,Positive/Uncertain/Chronic,DISEASE_STATE == 1 and CERTAINTY_STATE == 0 and ACUTE_STATE == 0 
5,Positive/Certain/Chronic,DISEASE_STATE == 1 and CERTAINTY_STATE == 1 and ACUTE_STATE == 0 
6,Negative/Uncertain/Acute,DISEASE_STATE == 0 and CERTAINTY_STATE == 0 
7,Positive/Uncertain/Acute,DISEASE_STATE == 1 and CERTAINTY_STATE == 0 and ACUTE_STATE == 1 
8,Positive/Certain/Acute,DISEASE_STATE == 1 and CERTAINTY_STATE == 1 and ACUTE_STATE == 1 
```
# Classification Rules #
For our application we specified classification rules with a text file # symbols indicate a comment line while @ symbols indicate a rule.

We used three categories of rules:
  1. **Classification Rules:** These are rule that classify a particular state of the document based on what modifiers are acting upon targets. They come in a set. The set must have a name (e.g. DISEASE\_STATE) and need at least one RULE and a DEFAULT state. Each rule consists of the set name, the ordinal value of the rule, and the list of modifier categories that if present render the rule true. The DEFAULT state is the rule value that should be assumed if no modifiers are acting upon a relevant target.
  1. **Category Rules:** These are rules that state that a target category should be changed if it is modified by certain categories. the rule consists of the target category to be changed (e.g. "DVT") and the modifier categories that if present would trigger a change the target category by concatenating the category names.
  1. **Severity Rules:** Severity rules state which target categories we should try to extract severity values for.
```
# Lines that start with the # symbol are comments and are ignored
# processReport current has three types of rules: @CLASSIFICATION_RULE, @CATEGORY_RULE, and @SEVERITY_RULE
# classification rules would be for things like disease_state, certainty_state, temporality state
# For each classification_rule set, there is a rule label (e.g. "DISEASE_STATE". This must match
# the terms used in the schema file
# Each rule set requires a DEFAULT which is the schema value to be returned
# if no rule conditions are satisifed
# Each rule set has zero or more rules consisting of a schema value 
#to be returned if the rule evaluates to true
# A rule evalutes to true if the target is modified by one or more of the ConText 
#CATEGORIES listed following
@CLASSIFICATION_RULE,DISEASE_STATE,RULE,0,DEFINITE_NEGATED_EXISTENCE,PROBABLE_NEGATED_EXISTENCE
@CLASSIFICATION_RULE,DISEASE_STATE,RULE,2,AMBIVALENT_EXISTENCE
@CLASSIFICATION_RULE,DISEASE_STATE,RULE,1,PROBABLE_EXISTENCE,DEFINITE_EXISTENCE
@CLASSIFICATION_RULE,DISEASE_STATE,DEFAULT,1
@CLASSIFICATION_RULE,CERTAINTY_STATE,RULE,0,PROBABLE_NEGATED_EXISTENCE,AMBIVALENT_EXISTENCE,PROBABLE_EXISTENCE
@CLASSIFICATION_RULE,CERTAINTY_STATE,DEFAULT,1
@CLASSIFICATION_RULE,ACUTE_STATE,RULE,0,HISTORICAL
@CLASSIFICATION_RULE,ACUTE_STATE,DEFAULT,1
#CATEGORY_RULE rules specify what Findings (e.g. DVT) can have the 
#category modified by the following ANATOMIC modifies
@CATEGORY_RULE,DVT,LOWER_DEEP_VEIN,UPPER_DEEP_VEIN
@CATEGORY_RULE,INFARCT,BRAIN_ANATOMY,HEART_ANATOMY,OTHER_CRITICAL_ANATOMY
@CATEGORY_RULE,ANEURYSM,AORTIC_ANATOMY
#SEVERITY_RUlE specifiy which targets to tryto obtain severity measures for
@SEVERITY_RULE,AORTIC_ANATOMY_ANEURYSM,SEVERITY
```