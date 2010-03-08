##############################
# Author: Xiuyun Shen        
# email: xis22@pitt.edu   
#                            
# Date: 07/28/09       
# Modified:     
#   
#                            
# 
##############################

GenConText -- genConText is an modification version of genNegEx which is A JAVA class to implement Wendy Chapman's 
NegEx algorithm. genCOntext program can annotate not only negation status but also temporality and experiencer.

#####################
# Motivation:       #
#####################
the motivation of releasing this code is to extend the genNegex to annotate other Context features, like temporality and experiencer


######################
# Files:             #
######################
This package includes 11 files.
1) 	GenContext.java: Source code for the JAVA implementation of ConText.
	it takes a phrase, sentence, rulelist, negationPossible and ConText feature as a parameter and assigns the feature value and 
	also give the scope of the trigger which changes the condition's feature value.
2) 	callGenConText.java: Source code for a short program to demonstrate using GenConText.
	It describes how to call GenContext from another program and the parameters
	that modify the behavior of GenConText.
3) 	trigger-neg.txt:
	This file lists the rules that were used with callGenConText.java to test GenConText for Negation.
	Users are free to use anything as a rule but they should follow the style
	of the example rule file.
	Generate your rule file as needed.
4,5,6) 	history_triggers.txt, hypothetical_triggers.txt, experiencer_triggers.txt: 
    Those files list the rules that were used with callGenConText.java to test GenConText for Temporality and experiencer.
    Users are free to use anything as a rule but they should follow the style
	of the example rule file.
7)	Sorter.java( from NegEx package): Source code for the simple exchange sorting algorithm to sort the rules
	by length in descending order. For faster sorting generate your own sorting class.
8) 	rsAnnotations-1-120-random.txt: The test kit. Format of the test kit and files
	with sentences to check negations for follows this structure:
	Number TAB note TAB Phrase TAB Sentence TAB reference_standard_for_negation TAB reference_standard_for_temporality TAB reference_standard_for_experiencer
	The output will have the following structure:
	Number TAB note TAB Phrase TAB Sentence TAB reference_standard_for_negation TAB reference_standard_for_temporality TAB reference_standard_for_experiencer
	TAB system_result_for_negation TAB system_result_for_temporality TAB system_result_for_experiencer
9)	evaluation.java that generates the statistics based on the output file for the
	test kit.
10)	ConTextFeatureCheckResults.txt output file for the test kit
	
11)	README: This file.


######################
# Notes:             #
######################
1. when testing a condition, if the sentence is in a section, the section header will be suggested to stay in the sentence
2. all programs are created and tested in netBean IDE under package genConText, when you use the genConText.java and other java programs, you might want to delete 
the first line of code "package genConText;"
########################
# To run the example:  #
########################
run callGenConText program first, use this script:  java callGenConText rsAnnotations-1-120-random.txt ContextFeatureCheckResults.txt trigger-neg.txt history_triggers.txt hypothetical_triggers.txt experiencer_triggers.txt

then run evaluate program, use script: java evaluation ContextFeatureCheckResults.txt 

# Using the test kit, printout should look like:
Evaluation for Negation
All  Negated  TP: 480.0
All  Negated  TN: 1877.0
All  Negated  FP: 8.0
All  Negated  FN: 11.0
 
All  Negated  Recall: 0.9775967413441955
All  Negated  Precision: 0.9836065573770492
All  Negated  F-measure: 0.9805924412665985


