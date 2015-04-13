ConText is based on a negation algorithm called NegEx. ConText's input is a sentence with indexed clinical conditions; ConText's output for each indexed condition is the value for three contextual features:

Negation: affirmed or negated.
Temporality: recent, historical, or hypothetical.
Experiencer: patient or other.

**I. ConText Algorithm:**

Go to first trigger term in sentence

If term is a pseudo-trigger term,
> Skip to next trigger term

Determine scope of trigger term

If termination term within scope,
> Terminate scope before termination term

Assign appropriate contextual feature value to all indexed conditions within scope.


**II. Trigger Terms:**


ConText relies on two types of trigger terms:

(1) Trigger terms - terms that indicate the value of the clinical concept within the scope of the trigger terms. For example, "no" is a trigger term for Negation, and "history" is a trigger term for temporality.

(2) Pseudo-trigger terms - terms that look like trigger terms but do not function as trigger terms. Often, pseudo trigger terms contain trigger terms. If ConText encounters a pseudo-trigger term, the algorithm skips to the next trigger term.

Trigger terms most often occur before the clinical condition being affected, but some trigger terms occur after the clinical condition..

Pre-concept trigger terms - terms that occur before the concept they are affecting.

Post-concept trigger terms - terms that occur after the concept they are affecting.

The list of actual terms is shown is section IV below.


**III. Scope of Trigger Terms:**


The default scope of a trigger term includes all indexed concepts until the end of the sentence. The default scope is overridden in certain circumstances. First, if the trigger term is a section heading, the entire section is within the scope of the trigger term. Second, a termination term ends the scope of the trigger term immediately preceding the termination term. Third, an individual trigger term can have its own scope, such as the historical trigger term "previous," which only extends one word forward.


**IV. List of Trigger Terms Currently Used by ConText (updated 3/23/07):**


NEGATION
Details on the Negation triggers can be found on the page describing **NegEx**


EXPERIENCER





TEMPORALITY




V.  Termination Terms:

Column 1 lists the type of termination term and the contextual feature values using that type of termination term.

Column 2 lists the terms.






Publications on ConText

(1) Chapman,W, Chu D, Dowling JN.  (2007) ConText: An algorithm for identifying contextual features from clinical text. BioNLP 2007: Biological, translational, and clinical language processing, pp. 81–88.

(2) Harkema H, Thornblade T, Dowling J, Chapman WW. Portability of ConText: An Algorithm for determining Negation, Experiencer, and Temporal Status from Clinical Reports. J Biomed Inform. 2009 May 10. [ahead of print](Epub.md).
