# Package Restructuring #

> Version 0.4.x includes a significant restructuring of the package structure.
  * The original code that was included in the pyConText main package has been moved to the subpackage "deprecated". This code is not longer being developed but is included since it is the code used in the JBI paper.
  * The code in the pyConTextGraph subpackage has been moved into the main package.
  * Applications corresponding to the different library versions have been put into a negex subpackage "pyConTextNLPTestApps"
    * tags
      * JBI: peFinder.py, peFinderRedux.py. Publication application (and simplified version) based on original (not NetworkX based) code.
      * 0.3.x: peFinderRedux2.py. Version based on the pyConTextGraph subpackage of pyConTextNLP version 0.3.x
    * trunk
      * Current test applications:
        * markFindgs.py: a very simple application that reads in text and marks up sentences. No document level inferences are made
        * testPEItems.py: a code for testing validity of itemData definitions. **This should be moved into main package testing.**



# Code Changes #
  * unicode support: all processing is now done with unicode strings. Regular expression compilation is now done explicitly with the re.UNICODE flag.
  * Some function name changes
    * setTxt() -> setText()
    * getCleanTxt() -> cleanText()
  * Some new functions:
    * unicode()
    * getRawText()

# Testing #
  * Started creating unit tests in test1.py file of pyConTextNLP package