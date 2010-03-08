/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */


/**
 *
 * @author xshen2
 */
import java.io.*;
import java.util.Scanner;
import java.util.ArrayList;
import java.util.*;
import java.util.regex.Pattern;

//comment: this program is created basing on Imre Solti's CallKit program.
// Author: xiuyun  xis22@pitt.edu
// created: 07/27/09
// Modified: 
//
// Purpose: this program is to show users how to call GenContext and its Context Feature check function for testing.
// note: you can modify the program to get all the parameters from standard input.
//
//
// The example below show all tags (for trigger terms) and scope of trigger.
//
// NOTES: 
// Negation trigger terms are in the file: trigger-neg.txt.
// historical trigger terms are in the file: history_trigger.txt.
// experiencer trigger terms are in the file: experiencer_trigger.txt.
// hypothetical trigger terms are in the file: hypothetical_trigger.txt.
// 
// Java version 5.0 is required as 5.0 specific features are used.
//
// To call GenContext's function you need to supply parameters as defined:
// g.ContextFeatureCheck(sentence, phrase, rules, negatePossible, ctype)
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
//    tagged. others do not have possible triggers currently, so we still keep this parameter named as negatePossible
// 5) ctype: "negation" for testng negation feature, "history" for testing historical feature,
//           "hypothetical" for testing hypothetical feature, "experiencer" for testing experience feature, finally we will combine historical and 
//           hypothetical into Temporality.
//
// Tags are:	[PREN] - Pretrigger rule tag
//		[POST] - Posttrigger rule tag
//		[PREP] - Pre possible  tag
//		[POSP] - Post possible  tag
// 		[PSEU] - Pseudo  tag
//		[CONJ] - Conjunction tag
//              [FSTT] - "for some time" trigger rule tag
//              [ONEW] - one word trigger rule tag
//		[PHRASE] - Term is rcognized from the term list, we search Context Features for but was NOT tagged yet
//		[active...] - active trigger
//              [NEGATION or HISTORICAL or NOT PARTICULAR or OTHER] - feature tagged
//
public class callGenConText {

    public static void main(String[] args) {

        try {
            
            if (args.length !=6) {
            System.out.println("Usage: java callGenContext  path.to.file.with.sentences.to.test path.to.file.contains.results path.to.negex.trigger.terms path.to.historical.trigger.terms path.to.hypothetical.trigger.terms path.to.experiencer.trigger.terms ");
            System.exit(-1);
            }
             

            


           
           // String sentencesFile = "/Users/xshen2/NetBeansProjects/ConTextFeatureTagger/src/genConText/rsAnnotations-1-120-random.txt";
			String sentencesFile=args[0];
            String contextType = "";




           

            File testKitFile = new File(sentencesFile);

            

            Scanner scKit = new Scanner(testKitFile);

           


          



           // File file = new File("/Users/xshen2/NetBeansProjects/ConTextFeatureTagger/src/genConText/ContextFeatureCheckResults.txt");
			 File file = new File(args[1]);
            Writer output = null;
            output = new BufferedWriter(new FileWriter(file));

           
            try {

                while (scKit.hasNextLine()) {
                    
                    Pattern pSplit = Pattern.compile("[\\t]+");

                    String line = scKit.nextLine().trim();

                    String[] content = pSplit.split(line);

                    String phrase = content[2].trim();
                    String sentence = content[3].trim();

                   // String negaftercheck=featureTagger("trigger-neg.txt", sentence, phrase, false, "negation");
                   //  String hisaftercheck=featureTagger("history_triggers.txt", sentence, phrase, false, "history");
                   //   String hypaftercheck=featureTagger("hypothetical_triggers.txt", sentence, phrase, false, "hypothetical");
                    //  String expaftercheck=featureTagger("experiencer_triggers.txt", sentence, phrase, false, "experiencer");
                     
                  
					String negaftercheck=featureTagger(args[2], sentence, phrase, false, "negation");
					String hisaftercheck=featureTagger(args[3], sentence, phrase, false, "history");
					String hypaftercheck=featureTagger(args[4], sentence, phrase, false, "hypothetical");
					String expaftercheck=featureTagger(args[5], sentence, phrase, false, "experiencer");
					
                    
                    
                    if (negaftercheck.split("\t").length>=2&&hisaftercheck.split("\t").length>=2&&hypaftercheck.split("\t").length>=2&&expaftercheck.split("\t").length>=2){
                      
                     if(hypaftercheck.split("\t")[1].equals("not particular")){
                       output.write(line+ "\t"+negaftercheck.split("\t")[1]+"\t"+hypaftercheck.split("\t")[1]+"\t"+expaftercheck.split("\t")[1]);   
                     } 
                     else{
                         output.write(line+ "\t"+negaftercheck.split("\t")[1]+"\t"+hisaftercheck.split("\t")[1]+"\t"+expaftercheck.split("\t")[1]);
                     }
                        
                  }
                    else{
                          System.out.println("something wrong with the string returning from calling featureTagger");
                    }
                      
                   
                
                    output.write("\n");

                }
            } catch (Exception e) {
                System.out.println(e);
            }
           
            scKit.close();
            output.close();
        } catch (Exception e) {
            System.out.println(e.getMessage());
            e.printStackTrace();
        }
    }
    
    public static String featureTagger(String triggerFile, String sentence, String phrase, boolean negatePossible, String contextType){
         String afterContextFeatureCheck="";
          genConText g = new genConText();
                 
         try {
       
      
        


         //   String triggersFile = "/Users/xshen2/NetBeansProjects/ConTextFeatureTagger/src/genConText/"+triggerFile;
           
String triggersFile = triggerFile;



            File ruleFile = new File(triggersFile);
            


           

            Scanner sc = new Scanner(ruleFile);
            

            

            ArrayList rules = new ArrayList();
           
           

            while (sc.hasNextLine()) {
                rules.add(sc.nextLine());
            }
            
            
           
                  
             afterContextFeatureCheck = g.ContextFeatureCheck(sentence, phrase, rules, negatePossible, contextType);
        
        } catch (Exception e) {
                System.out.println(e);
            }
        return afterContextFeatureCheck;
        
        
    }
}
