# Algorithm #

## Terms used by regular expressions ##

### I. Negation terms ###

Three types of terms are used to indicate negation:

(1) Pseudo negation terms - phrases that look like negation terms but do not negate the clinical condition. If a pseudo-negation term is found, NegEx skips to the next negation term.

(2) Pre-condition negation term - terms that occur before the term they are negating. Pre-condition terms are used in Regular Expression 1.

(3) Post-condition negation term - terms that occur after the term they are negating. Post-condition terms are used in Regular Expression 2.

### II. Termination terms ###

Termination terms indicate that the scope of the negation term should end. For example, the term "but" terminates the scope of the negation in the sentence "Patient denies chest pain but continues to experience SOB."

## Regular Expressions ##

The regular expressions determine the scope of the negation within the sentence.

NegEx uses two regular expressions that are triggered by the negation terms described above:
Regular Expression 1:        <negation term> <$> <termination term|end of sentence>
Regular Expression 2:        <indexed term> <$> <negation phrase>

$ can represents a specified or unspecified number of words. Historically, NegEx set $ to five words (a word can be a single word or a phrase like "shortness of breath"). With the addition of termination terms, we set $ to any number of words.

Our current version is as follows:
RE 1 --> $1 = any number of words or punctuation
RE 2 --> $2 = five words or medical phrases

## Algorithm ##

For each sentence, find all negation terms:
Go to the first negation term in the sentence (Neg1).

If Neg1 is a pseudo-negation term, skip to the next negation term in the sentence.

If Neg1 is a pre-condition negation term:

> Define the scope of Neg1 forward based on the value of $1, terminating the scope when you encounter any of the following:
    * a termination term
    * another negation or pseudo-negation term
    * the end of the sentence

If Neg1 is a post-condition negation term, define the scope of Neg1 backwards based on the value of $2.

Repeat for all negation terms in the sentence.

## Examples ##
Text in square brackets is within the scope of the bolded negation term.

"The patient **denies** [and has](chest_pain.md) **no** [shortness\_of\_breath](shortness_of_breath.md)."
"The patient **denies** [chest\_pain](chest_pain.md) but has experienced some shortness\_of\_breath"
"[is tumor](She.md) **free**."
"No increase in tumor size."