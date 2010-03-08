/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */



/**
 *
 * @author xshen2
 */
public class testrandom {
     public static void main(String[] args){
         
       int rangestart=0;
   int rangeend=1;
   
    
   int random = (int) ( rangestart + Math.random() *(rangeend-rangestart));   
    System.out.println(random);     
         
         
     }

}
