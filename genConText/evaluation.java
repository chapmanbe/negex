/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */


/**
 *
 * @author xshen2
 */
import java.io.*;
import java.util.*;
import java.lang.*;
import java.util.regex.Pattern;

/************************************************************
 * Utility class to calculate the accuracy of negation, experiencer and Temporality
 * detection on the testkit. this program is created basing on Imre Solti's accuracy.java
 *************************************************************/
public class evaluation {

    public static void main(String[] args) {
		
            
            if (args.length !=1) {
				System.out.println("Usage: java evaluation  path.to.callGenContext.result.file");
				System.exit(-1);
            }
			

        //String resultFile	= args[0];
      //  String resultFile = "/Users/xshen2/NetBeansProjects/ConTextFeatureTagger/src/genConText/ContextFeatureCheckResults.txt";

         String resultFile = args[0];





        System.out.println("Evaluation for Negation");
        processEval(resultFile, "Negated", "Affirmed");
        System.out.println("\n\n");

        System.out.println("Evaluation for Historical");
        processEval(resultFile, "Historical", "Recent");
        System.out.println("\n\n");

        System.out.println("Evaluation for Hypothetical");
        processEval(resultFile, "Not particular", "Recent");
        System.out.println("\n\n");

        System.out.println("Evaluation for Experiencer");
        processEval(resultFile, "Other", "Patient");
        System.out.println("\n\n");





    }

    public static void processEval(String resultFile, String val1, String val2) {
        try {
            Scanner scResult = new Scanner(new File(resultFile));

            double tp = 0;
            double fp = 0;
            double tn = 0;
            double fn = 0;


            while (scResult.hasNextLine()) {
                String line = scResult.nextLine().trim();
                Pattern pSplit = Pattern.compile("[\\t]+");
                String[] content = pSplit.split(line);
                String gold = "";
                String sys = "";
                String temporality = "";
                if (val1.equals("Negated")) {
                    gold = content[4];
                    sys = content[7];
                }
                if (val1.equals("Historical")) {
                    gold = content[5];
                    sys = content[8];
                    temporality = "Not particular";
                }
                if (val1.equals("Not particular")) {
                    gold = content[5];
                    sys = content[8];
                    temporality = "Historical";
                }
                boolean temp = gold.trim().equals(val1);
                if (val1.equals("Other")) {
                    gold = content[6];
                    sys = content[9];
                    temp = !gold.trim().equals(val2);
                }

                if (temp) {

                    if (sys.trim().equals(val1.toLowerCase())) {

                        tp++;
                    }

                    if (sys.trim().equals(val2.toLowerCase()) || sys.trim().equals(temporality.toLowerCase())) {

                        fn++;

                    }
                    if (sys.trim().equals("possible")) {

                        tp++;
                    }
                } else if (gold.trim().equals(val2)) {

                    if (sys.trim().equals(val1.toLowerCase())) {

                        fp++;
                    }
                    if (sys.trim().equals(val2.toLowerCase()) || sys.trim().equals(temporality.toLowerCase())) {

                        tn++;
                    }
                    if (sys.trim().equals("possible")) {

                        fp++;
                    }
                } else if (gold.trim().equals(temporality)) {

                    if (sys.trim().equals(val1.toLowerCase())) {

                        fp++;
                    }
                    if (sys.trim().equals("recent")) {

                        tn++;
                    }
                    if (sys.trim().equals(temporality.toLowerCase())) {

                        tn++;
                    }
                } else if (gold.trim().equals("Possible")) {

                    if (sys.trim().equals(val1.toLowerCase())) {

                        tp++;
                    }
                    if (sys.trim().equals(val2.toLowerCase())) {

                        fn++;
                    }
                    if (sys.trim().equals("possible")) {

                        tp++;
                    }
                } else {
                    System.out.println(line);
                }


            }



            System.out.println("All  " + val1 + "  TP: " + tp);

            System.out.println("All  " + val1 + "  TN: " + tn);
            System.out.println("All  " + val1 + "  FP: " + fp);
            System.out.println("All  " + val1 + "  FN: " + fn);

            System.out.println(" ");

            System.out.println("All  " + val1 + "  Recall: " + (tp / (tp + fn)));
            System.out.println("All  " + val1 + "  Precision: " + (tp / (tp + fp)));
            System.out.println("All  " + val1 + "  F-measure: " + (2 * (tp / (tp + fn)) * (tp / (tp + fp))) / ((tp / (tp + fn)) + (tp / (tp + fp))));


        } catch (Exception e) {
            System.out.println(e);
        }


    }
}

