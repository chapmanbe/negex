A physician annotated non-numeric clinical conditions in the reports (i.e., symptoms, findings, and diseases not requiring a numeric value to be a valid condition). The sentences have been de-identified automatically using the De-ID System and have been randomized.

The file contains one sentence for every clinical condition found in the reports. For each condition, the physician annotated the following contextual properties:

**Negation status** - values: affirmed, negated (sorry - no possible annotations in this set).

**Temporality status** - values: historical, recent, hypothetical.

**Experiencer** - values: patient, other.

You can use the set to evaluate your own version of NegEx by comparing your output from the sentence to the physician annotation of Negation status. Below, we list performance you should get on this set when applying the code distributed on this site. You can also use the set to evaluate ConText, which assigns not only negation status but also temporality status and experiencer. Downloadable versions of ConText will be posted soon.

This file is available as a separate download but is also contained in the downloadable code packages on the site.

Please contact Wendy Chapman with any questions or suggestions for this set: wendy.w.chapman@gmail.com


---

**Performance stats**

_GenNegEx v1.2_

GS Negated: 491.0
GS Affirmed: 1885.0
GS Possible: 0.0

System Negated: 495.0
System Affirmed: 1871.0
System Possible: 10.0

TP or Correct Negated: 471.0
TN or Correct Affirmed: 1851.0
FP or False Negated: 34.0
FN or False Affirmed: 20.0

Recall: 0.9592668024439919
Precision: 0.9326732673267327
F-measure: 0.9457831325301205
Correct Negated + Correct Affirmed/Total x100 = 97.72727272727273
Total: 2376.0