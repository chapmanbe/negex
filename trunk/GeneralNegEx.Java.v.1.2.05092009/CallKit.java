import java.io.*;
import java.util.Scanner;
import java.util.ArrayList;
import java.util.*;
import java.util.regex.Pattern;

// Author: Imre Solti
// solti@u.washington.edu
// 10/20/2008
// Modified: 03/29/2009
// Changed to new specifications of test kit.
//
// Purpose: To call GenNegEx and its negation check function for testing
// it also shows how to use GenNegEx in a program and the combination of tags
// that can be returned.
//
// The example below show all tags (for trigger terms, negated, possible) and scope of negation.
//
// NOTES: 
// Negation trigger terms are in the file: negex_triggers.txt.
// 
// Java version 5.0 is required as 5.0 specific features are used.
//
// To call GenNegEx's function you need to supply parameters as defined:
// g.negCheck(sentence, phrase, rules, negatePossible)
// 1) sentence: String sentence you want to check for negations.
// 2) phrase: String term we want to check for negation in the sentence. 
//    (for example, "diabetes", "sudden death syndrome", etc...). There is no
//    limitation what can be a term. It can be CUI from the UMLS or an English word.
// 3) rules: ArrayList of rules. 
//    IMPORTANT not to have extra
//    white spaces in rule lines because rules are sorted (in GenNegEx) by length
//    in descending order so longest rules will be matched first.
// 4) negatePossible: boolean and if set to "true" then POSSIBLE as defined by Chapman will be detected
//    and tagged as [POSSIBLE]. If negatePossible is set to "false" then possible is not
//    tagged.
//
// Tags are:	[PREN] - Prenegation rule tag
//		[POST] - Postnegation rule tag
//		[PREP] - Pre possible negation tag
//		[POSP] - Post possible negation tag
// 		[PSEU] - Pseudo negation tag
//		[CONJ] - Conjunction tag
//		[PHRASE] - Term is rcognized from the term list, we search negation for but was NOT negated
//		[NEGATED] - Term was recognized from term list, and it was found being negated
//		[POSSIBLE] - Term was recognized from term list, and was found as possible negation
//
//
/*
Copyright 2008 Imre Solti

Licensed under the Apache License, Version 2.0 (the "License"); 

you may not use this file except in compliance with the License. You may obtain a copy of the License at 

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, 
WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and
limitations under the License. 
*/


 
public class CallKit{
	public static void main(String[] args) {

	  try {
		if (args.length != 2) {
			System.out.println("Usage: java CallKit path.to.negex.trigger.terms path.to.file.with.sentences.to.test");
			System.exit(-1);
		}

		GenNegEx g 			= new GenNegEx();
		String fillerString		= "_";
		boolean negatePossible		= true;

		String triggersFile		= args[0];
		String sentencesFile		= args[1];		

                File ruleFile                   = new File(triggersFile);
		File testKitFile		= new File(sentencesFile);

                Scanner sc                      = new Scanner(ruleFile);
		Scanner scKit			= new Scanner(testKitFile);

		ArrayList rules			= new ArrayList();
		String afterNegCheck		= "";


		while (sc.hasNextLine()) {
			rules.add(sc.nextLine());
		}

		try {

			while (scKit.hasNextLine()) {
				//sentences.add(scKit.nextLine().trim().toLowerCase());
				Pattern pSplit		= Pattern.compile("[\\t]+");

				String line 		= scKit.nextLine().trim();

				String[] content	= pSplit.split(line);

				String phrase = content[1].trim();
				String sentence = content[2].trim();

				// Show NEGATED and POSSIBLE tags for the testkit and print scope.			
				afterNegCheck = g.negCheck(sentence, phrase, rules, negatePossible);
				System.out.println(content[0] + "\t" + content[1] + "\t" + content[2] + 
							"\t" + content[3] + "\t" +
							afterNegCheck );
			}
		}
		catch (Exception e) {
			System.out.println(e);
		}
		sc.close();
		scKit.close();
	  }
	  catch (Exception e) {
		System.out.println(e.getMessage());
		e.printStackTrace();
	  }
	}
}
