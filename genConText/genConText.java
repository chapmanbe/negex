/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */


/**
 *
 * @author xshen2
 *
 */
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.io.*;
import java.util.ArrayList;
import java.util.Scanner;
import java.util.*;

/***************************************************************************************
 * Author: Xiuyun Shen
 * Date: 07/27/09
 * Modified: 
 * Comment: this program is created on Imre Solti's genNegEx, I just did some modifiction in order to 
 *          annotate not only negation status also annotat temporality and experiencer.
 ****************************************************************************************/
public class genConText {
    //ctype can be "negation", "history", "experiencer" and "hypothetical"

    public String ContextFeatureCheck(String sentenceString, String phraseString, ArrayList ruleStrings,
            boolean negatePossible, String ctype) throws Exception {

        Sorter s = new Sorter();
        String sToReturn = "";
        String sScope = "";
        String sentencePortion = "";
        ArrayList sortedRules = new ArrayList();

        String filler = "_";
        boolean negPoss = negatePossible;
        boolean negationScope = true;



//Negation: affirmed or negated. Temporality: recent, historical, or not particular. Experiencer: patient or other.

        String ctag = "";
        String cdefault = "";
        if (ctype.equals("history")) {
            ctag = "historical";
            cdefault = "recent";
        }
        if (ctype.equals("negation")) {
            ctag = "negated";
            cdefault = "affirmed";
        }
        if (ctype.equals("experiencer")) {
            ctag = "other";
            cdefault = "patient";
        }
        if (ctype.equals("hypothetical")) {
            ctag = "not particular";
            cdefault = "recent";
        }



        //need to add more history ruls: "FSTT"(for some time) triggers and "For several days" terminators
        if (ctype.equals("history")) {


            //"for several days" is history terminators, add this rule to rule list
            String expr1 = "(?m)(?i)(within the last|in the last|for the past|for the last|over the past|over the last|for)(\\s+\\d*(\\.\\d*)*|\\s+(\\w+)(\\s+\\w*)?(\\s+\\w*)?(\\s+\\w*)?(\\s+\\w*)?(\\s+\\w*)?)?(\\s+days|\\s+day)";
            Pattern p1 = Pattern.compile(expr1.trim());
            Matcher m1 = p1.matcher(sentenceString);

            while (m1.find() == true) {
                ruleStrings.add(m1.group().trim() + "\t" + "\t" + "[CONJ]");

            }

            //"put "FSTT" triggers to rule list
            String expr2 = "(?m)(?i)(for the past|for the last|over the past|over the last|for)(\\s+\\d*(\\.\\d*)*|\\s+(\\w+)(\\s+\\w*)?(\\s+\\w*)?(\\s+\\w*)?(\\s+\\w*)?(\\s+\\w*)?)?(\\s+weeks|\\s+week|\\s+months|\\s+month|\\s+years|\\s+year)";
            Pattern p22 = Pattern.compile(expr2.trim());
            Matcher m2 = p22.matcher(sentenceString);

            while (m2.find() == true) {
                String temp = m2.group().trim();
                ruleStrings.add(temp + "\t" + "\t" + "[FSTT]");
                  
            }

        //finish adding additional history rules

        }



        
        sortedRules = s.sortRules(ruleStrings);


        String sentence = "." + sentenceString + ".";

        
        String phrase = phraseString;
        Pattern pph = Pattern.compile(phrase.trim(), Pattern.CASE_INSENSITIVE);
        Matcher mph = pph.matcher(sentence);

        while (mph.find() == true) {
            sentence = mph.replaceAll(" [PHRASE]" + mph.group().trim().replaceAll(" ", filler) + "[PHRASE]");
        }
        
        //tag negation "Punct" terminators: },),:
        if (ctype.equals("negation")) {
            String prule = "[\\}\\:\\)]";

            Pattern pp = Pattern.compile(prule.trim());
            Matcher pm = pp.matcher(sentence);

            while (pm.find() == true) {
                sentence = pm.replaceAll(" " + "[CONJ]" + pm.group().trim().replaceAll(" ", filler) + "[" + "/CONJ" + "]" + " ");
            }
        }



        Iterator iRule = sortedRules.iterator();
        while (iRule.hasNext()) {
            String rule = (String) iRule.next();
            Pattern p = Pattern.compile("[\\t]+"); 	

            String[] ruleTokens = p.split(rule.trim());
           
            String[] ruleMembers = ruleTokens[0].trim().split(" ");
            String rule2 = "";
            for (int i = 0; i <= ruleMembers.length - 1; i++) {
                if (!ruleMembers[i].equals("")) {
                    if (ruleMembers.length == 1) {
                        rule2 = ruleMembers[i];
                    } else {
                        rule2 = rule2 + ruleMembers[i].trim() + "\\s+";
                    }
                }
            }
           
            if (rule2.endsWith("\\s+")) {
                rule2 = rule2.substring(0, rule2.lastIndexOf("\\s+"));
            }
// modify the rule2 expression in order to prevent some situations like this: [PSEU]poor history[/PSEU] in stead of [PSEU]poor [PREN]history[/PREN][/PSEU]
            rule2 = "(?m)(?i)[[\\p{Punct}&&[^\\]\\[]]|\\s+](" + rule2 + ")[[\\p{Punct}&&[^_\\[]]|\\s+]";

            Pattern p2 = Pattern.compile(rule2.trim());
            Matcher m = p2.matcher(sentence);

            while (m.find() == true) {
               
                String[] t = ruleTokens[1].trim().split("\\[");
                sentence = m.replaceAll(" " + ruleTokens[1].trim() + m.group().trim().replaceAll(" ", filler) + "[" + "/" + t[1] + " ");
            }
        }






        Pattern pSpace = Pattern.compile("[\\s+]");
        String[] sentenceTokens = pSpace.split(sentence);
        StringBuilder sb = new StringBuilder();
        int count1 = 0;

        
        for (int i = 0; i < sentenceTokens.length; i++) {

            if (sentenceTokens[i].trim().startsWith("[PREN]") || sentenceTokens[i].trim().startsWith("[FSTT]") || sentenceTokens[i].trim().startsWith("[ONEW]")) {

                for (int j = i + 1; j < sentenceTokens.length; j++) {
                    //add more conditions mainly for applying "closest trigger" policy
                    if (sentenceTokens[j].trim().startsWith("[CONJ]") ||
                            sentenceTokens[j].trim().startsWith("[PSEU]") ||
                            sentenceTokens[j].trim().startsWith("[POST]") ||
                            sentenceTokens[j].trim().startsWith("[PREN]") ||
                            sentenceTokens[j].trim().startsWith("[PREP]") ||
                            sentenceTokens[j].trim().startsWith("[POSP]") ||
                            sentenceTokens[j].trim().startsWith("[FSTT]") ||
                            sentenceTokens[j].trim().startsWith("[ONEW]")) {
                        break;
                    }
                    //we use this flag to control domain of "one word" trigger because one word trigger only affect phrase which is at most two tokens far from trigger
                    
                    boolean onewFlag = true;
                    if (sentenceTokens[i].trim().startsWith("[ONEW]")) {
                        if (sentenceTokens[j].trim().startsWith("[PHRASE]")) {
                            if (j - i > 4) {
                                onewFlag = false;
                            }
                        }
                    }
                    //we tag the first fired trigger differently
                    if (sentenceTokens[j].trim().startsWith("[PHRASE]") && onewFlag) {
                       
                        if (count1 == 0) {
                            if (sentenceTokens[i].trim().startsWith("[FSTT")) {
                                sentenceTokens[i] = sentenceTokens[i].trim().replaceAll("\\[", "[activePRE");
                            } else {
                                sentenceTokens[i] = sentenceTokens[i].trim().replaceAll("\\[", "[active");
                            }
                            count1 = count1 + 1;
                        }
                       
                        sentenceTokens[j] = sentenceTokens[j].trim().replaceAll("\\[PHRASE\\]", "[" + ctag.toUpperCase() + "]");

                    }
                }
            }
            sb.append(" " + sentenceTokens[i].trim());
        }

        sentence = sb.toString();
        pSpace = Pattern.compile("[\\s+]");
        sentenceTokens = pSpace.split(sentence);
        StringBuilder sb2 = new StringBuilder();
        int count2 = 0;

        // Check for [POST]
        for (int i = sentenceTokens.length - 1; i > 0; i--) {
//add more conditions for "closest trigger " policy
            if (sentenceTokens[i].trim().startsWith("[POST]") || sentenceTokens[i].trim().startsWith("[FSTT]")) {
                for (int j = i - 1; j > 0; j--) {
                    if (sentenceTokens[j].trim().startsWith("[CONJ]") ||
                            sentenceTokens[j].trim().startsWith("[PSEU]") ||
                            sentenceTokens[j].trim().startsWith("[PREN]") ||
                            sentenceTokens[j].trim().startsWith("[PREP]") ||
                            sentenceTokens[j].trim().startsWith("[POST]") ||
                            sentenceTokens[j].trim().startsWith("[POSP]") ||
                            sentenceTokens[j].trim().startsWith("[FSTT]")) {
                        //for closest negation post trigger, we don't check terminators betwwn phrase and trigger
                        if (ctype.equals("negation") && sentenceTokens[j].trim().startsWith("[CONJ]")) {
                        } else {
                            break;
                        }
                    }

                    if (sentenceTokens[j].trim().startsWith("[PHRASE]")) {
                        if (count2 == 0) {
                            if (sentenceTokens[i].trim().startsWith("[FSTT")) {
                                sentenceTokens[i] = sentenceTokens[i].trim().replaceAll("\\[", "[activePOST");
                            } else {
                                sentenceTokens[i] = sentenceTokens[i].trim().replaceAll("\\[", "[active");
                            }
                            count2 = count2 + 1;
                        }
                       
                        sentenceTokens[j] = sentenceTokens[j].trim().replaceAll("\\[PHRASE\\]", "[" + ctag.toUpperCase() + "]");
                    }
                }
            }
            sb2.insert(0, sentenceTokens[i] + " ");
        }

        sentence = sb2.toString();

       
        if (negPoss == true) {
            pSpace = Pattern.compile("[\\s+]");
            sentenceTokens = pSpace.split(sentence);

            StringBuilder sb3 = new StringBuilder();
            int count3 = 0;
            // Check for [PREP]
            for (int i = 0; i < sentenceTokens.length; i++) {

                if (sentenceTokens[i].trim().startsWith("[PREP]")) {

                    for (int j = i + 1; j < sentenceTokens.length; j++) {
                        if (sentenceTokens[j].trim().startsWith("[CONJ]") ||
                                sentenceTokens[j].trim().startsWith("[PSEU]") ||
                                sentenceTokens[j].trim().startsWith("[POST]") ||
                                sentenceTokens[j].trim().startsWith("[PREN]") ||
                                sentenceTokens[j].trim().startsWith("[PREP]") ||
                                sentenceTokens[j].trim().startsWith("[POSP]")) {
                            break;
                        }

                        if (sentenceTokens[j].trim().startsWith("[PHRASE]")) {
                            if (count3 == 0) {
                                sentenceTokens[i] = sentenceTokens[i].trim().replaceAll("\\[", "[active");
                                count3 = count3 + 1;
                            }
                            sentenceTokens[j] = sentenceTokens[j].trim().replaceAll("\\[PHRASE\\]", "[POSSIBLE]");
                        }
                    }
                }
                sb3.append(" " + sentenceTokens[i].trim());
            }

            sentence = sb3.toString();
            pSpace = Pattern.compile("[\\s+]");
            sentenceTokens = pSpace.split(sentence);
            StringBuilder sb4 = new StringBuilder();
            int count4 = 0;
            // Check for [POSP]
            for (int i = sentenceTokens.length - 1; i > 0; i--) {

                if (sentenceTokens[i].trim().startsWith("[POSP]")) {
                    for (int j = i - 1; j > 0; j--) {
                        if (sentenceTokens[j].trim().startsWith("[CONJ]") ||
                                sentenceTokens[j].trim().startsWith("[PSEU]") ||
                                sentenceTokens[j].trim().startsWith("[PREN]") ||
                                sentenceTokens[j].trim().startsWith("[PREP]") ||
                                sentenceTokens[j].trim().startsWith("[POSP]") ||
                                sentenceTokens[j].trim().startsWith("[POST]")) {
                            break;
                        }

                        if (sentenceTokens[j].trim().startsWith("[PHRASE]")) {
                            if (count4 == 0) {
                                sentenceTokens[i] = sentenceTokens[i].trim().replaceAll("\\[", "[active");
                                count4 = count4 + 1;
                            }
                            sentenceTokens[j] = sentenceTokens[j].trim().replaceAll("\\[PHRASE\\]", "[POSSIBLE]");
                        }
                    }
                }
                sb4.insert(0, sentenceTokens[i] + " ");
            }

            sentence = sb4.toString();
        }

   
        sentence = sentence.replaceAll(filler, " ");

       
        sentence = sentence.substring(0, sentence.trim().lastIndexOf('.'));
        sentence = sentence.replaceFirst(".", "");

        // Get the scope of the pre active trigger

        if (sentence.contains("[activePRE")) {
            int startOffset = sentence.indexOf("[activePRE");
            String sentence1 = sentence.substring(startOffset + 1, sentence.length() - 1);
            
            int endOffset = sentence1.indexOf("[CONJ]");
            if (endOffset == -1) {
                endOffset = sentence1.indexOf("[PSEU]");
            }
            if (endOffset == -1) {
                endOffset = sentence1.indexOf("[PREN]");
            }
            if (endOffset == -1) {
                endOffset = sentence1.indexOf("[PREP]");
            }
            if (endOffset == -1) {
                endOffset = sentence1.indexOf("[activePRE");
            }
            if (endOffset == -1) {
                endOffset = sentence1.indexOf("[FSTT]");
            }
            
            endOffset = endOffset + startOffset;
            if (endOffset == -1 || endOffset < startOffset) {
                endOffset = sentence.length() - 1;
            }
            
            sScope = sentence.substring(startOffset, endOffset);
        }

        // Get the scope of the post active trigger 
        if (sentence.contains("[activePOST/") || sentence.contains("[active/POS")) {

            int endOffset = sentence.lastIndexOf("[activePOST/");
            int es = sentence.lastIndexOf("[activePOSTFSTT");
            if (endOffset == -1) {
                endOffset = sentence.lastIndexOf("[active/POS");
                es = sentence.lastIndexOf("[activePOS");
            }


            String sentence2 = sentence.substring(0, es);
            int startOffset = sentence2.lastIndexOf("[CONJ]");
            if (startOffset == -1) {
                startOffset = sentence2.lastIndexOf("[PSEU]");
            }
            if (startOffset == -1) {
                startOffset = sentence2.lastIndexOf("[POST]");
            }
            if (startOffset == -1) {
                startOffset = sentence2.lastIndexOf("[POSP]");
            }
            if (startOffset == -1) {
                startOffset = sentence2.lastIndexOf("[active");
            }
            if (startOffset == -1) {
                startOffset = sentence2.lastIndexOf("[FSTT]");
            }
            if (startOffset == -1) {
                startOffset = 0;
            }
           
            sScope = sentence.substring(startOffset, endOffset + 14);
        }

       
        if (sentence.contains("[" + ctag.toUpperCase() + "]")) {
            sentence = sentence + "\t" + ctag + "\t" + sScope;
        } else if (sentence.contains("[POSSIBLE]")) {
            sentence = sentence + "\t" + "possible" + "\t" + sScope;
        } else {
            sentence = sentence + "\t" + cdefault + "\t" + sScope;
        }

        sToReturn = sentence;

        return sToReturn;
    }
}
