##############################
# Author: Peter Kang	     #
# peter.kang@roswellpark.org #
#                            #
# Date: 05/14/2009	     #
##############################

negex.py -- A python module to implement Wendy Chapman's NegEx algorithm.

The original NegEx algorithm is published at:
http://www.dbmi.pitt.edu/chapman/NegEx.html

#####################
# Motivation:       #
#####################
The motivation to release this code is two-fold.

One goal is to make Wendy Chapman's NegEx
algorithm more accessible for server side (that is non-GUI) programming for
Python development for research purposes. The code was tested for research only
and no enterprise purposes of any kind.

The second goal is to try Ted Pedersen's suggestion for code sharing
as he describes in the 2008 Computational Lingusitics article.
Pedersen, T. "Empiricism is not a matter of faith." Computational Linguistics. 34: 465-470, 2008.
http://www.d.umn.edu/~tpederse/Pubs/pedersen-last-word-2008.pdf


######################
# Files:             #
######################
This package includes 5 files.
1) 	negex.py: Source code for the Python implementation of NegEx.
	It can tag definitive negations only or both definitive and possible negations.
	You will need to post process the output of GenNegEx. In a real task
	you might want to use simple regex rules to find the [NEGATED] and [POSSIBLE]
	tags and for example delete those phrases that are tagged before running a 
	concept extraction program.
2) 	wrapper.py: Source code for a short program to demonstrate using negex.py. Simply run this in Python.
3) 	negex_triggers.txt:
	This file lists the rules that were used with wrapper.py to test negex.py.
	Users are free to use anything as a rule but they should follow the style
	of the example rule file.
	Generate your rule file as needed.
4) 	Annotations-1-120-random.txt: The test kit. Format of the test kit and files
	with sentences to check negations for follows this structure:
	Number TAB Phrase TAB Sentence TAB Dummystring
	The output will have the following structure:
	Number TAB Phrase TAB Sentence TAB Dummystring TAB Sentence.with.tags TAB Decision TAB Scope.if.negated
5)	README: This file.


Copyright 2009 Peter Kang

you may not use this file except in compliance with the License. You may obtain a copy of the License at 

http://www.python.org/download/releases/2.5.4/license/

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT 
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and 
limitations under the License. 


######################
# Notes:             #
######################
// NOTES:
// Negation trigger terms are in the file: negex_triggers.txt.
//
// The code was written in Python 2.5.
//
// Tags are:    [PREN] - Prenegation rule tag
//              [POST] - Postnegation rule tag
//              [PREP] - Pre possible negation tag
//              [POSP] - Post possible negation tag
//              [PSEU] - Pseudo negation tag
//              [CONJ] - Conjunction tag
//              [PHRASE] - Term is rcognized from the term list, we search negation for but was NOT negated
//              [NEGATED] - Term was recognized from term list, and it was found being negated
//              [POSSIBLE] - Term was recognized from term list, and was found as possible negation
//
//