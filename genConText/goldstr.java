/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */



import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.Writer;
import java.util.Scanner;
import java.util.regex.Pattern;

/**
 *
 * @author xshen2
 */
public class goldstr {
    public static void main(String[] args){
      try{  
        String sentencesFile		= "/Users/xshen2/NetBeansProjects/ConTextFeatureTagger/src/genConText/Annotations.txt";
               
                
                
                
                
               File testKitFile		= new File(sentencesFile);

               Scanner scKit			= new Scanner(testKitFile);
        
        
        
         File file=new File("/Users/xshen2/NetBeansProjects/ConTextFeatureTagger/src/genConText/annotations-1-120-negation.txt");
Writer output=null;
output=new BufferedWriter(new FileWriter(file));

int count=1;

while (scKit.hasNextLine()) {
				//sentences.add(scKit.nextLine().trim().toLowerCase());
				Pattern pSplit		= Pattern.compile("[\\t]+");

				String line 		= scKit.nextLine().trim();

				String[] content	= pSplit.split(line);
                                
                               
                                
                             
                                
                                
                                output.write(count+"\t"+content[0]+"\t"+content[1]+"\t"+content[2]);
                                output.write("\n");   
                                count++;
                              //  System.out.println(content[0]);
}
		scKit.close();
                output.close();
      }
	  catch (Exception e) {
		System.out.println(e.getMessage());
		e.printStackTrace();
	  }     
        
        
    }

}
