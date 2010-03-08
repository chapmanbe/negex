import java.io.*;
import java.util.*;
import java.lang.*;
import java.util.regex.Pattern;

/************************************************************
* Utility class to calculate the accuracy of negation
* detection on the testkit.
*************************************************************/


public class accuracy {

	public static void main(String[] args) {

		try {
			String resultFile	= args[0];
			double tp 		= 0;
			double fp		= 0;
			double tn		= 0;
			double fn		= 0;

			double gsN		= 0;
			double gsA		= 0;
			double gsP		= 0;

			double sysN		= 0;
			double sysA		= 0;
			double sysP		= 0;

			double total		= 0;
			
			double F		= 0;

			Scanner scResult	= new Scanner(new File(resultFile));
			while (scResult.hasNextLine() ) {
				String line  		= scResult.nextLine().trim();
				Pattern pSplit 		= Pattern.compile("[\\t]+");
				String[] content	= pSplit.split(line);

				total++;

				if (content[3].trim().equals("Negated")) {
					gsN++;
					if (content[5].trim().equals("negated")) {
						sysN++;
						tp++;
					}
					if (content[5].trim().equals("affirmed")) {
						sysA++;
						fn++;
					}
					if (content[5].trim().equals("possible")) {
						sysP++;
						tp++;
					}
				}
				else if (content[3].trim().equals("Affirmed")) {
					gsA++;
					if (content[5].trim().equals("negated")) {
						sysN++;
						fp++;
					}
					if (content[5].trim().equals("affirmed")) {
						sysA++;
						tn++;
					}
					if (content[5].trim().equals("possible")) {
						sysP++;
						fp++;
					}
				}
				else if (content[3].trim().equals("Possible")) {
					gsP++;
					if (content[5].trim().equals("negated")) {
						sysN++;
						tp++;
					}
					if (content[5].trim().equals("affirmed")) {
						sysA++;
						fn++;
					}
					if (content[5].trim().equals("possible")) {
						sysP++;
						tp++;
					}
				}
				else {
					System.out.println(line);
				}
			}

			System.out.println("GS Negated: " + gsN);
			System.out.println("GS Affirmed: " + gsA);
			System.out.println("GS Possible: " + gsP);

			System.out.println(" ");

			System.out.println("System Negated: " + sysN);
			System.out.println("System Affirmed: " + sysA);
			System.out.println("System Possible: " + sysP);

			System.out.println(" ");

			System.out.println("TP or Correct Negated: " + tp);
			System.out.println("TN or Correct Affirmed: " + tn);
			System.out.println("FP or False Negated: " + fp);
			System.out.println("FN or False Affirmed: " + fn);

			System.out.println(" ");

			System.out.println("Recall: " + (tp/(tp+fn)) );
			System.out.println("Precision: " + (tp/(tp+fp)) );
			System.out.println("F-measure: " + (2 * (tp/(tp+fn))  * (tp/(tp+fp)) ) / ((tp/(tp+fn))  +  (tp/(tp+fp)) ) );

			System.out.println("Correct Negated + Correct Affirmed/Total *100 = " + ((tp+tn)/total)*100);

			System.out.println("Total: " + total);
		}
		catch (Exception e) {
			System.out.println(e);
		}
	}
}
