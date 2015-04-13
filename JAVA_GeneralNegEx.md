# Introduction #

How to call the GenNegEx class from another JAVA program.

# Details #

To call GenNegEx's function you need to supply parameters as defined:
> g.negCheck(sentences, rules, phrases, fillerString, negatePossible, showOnlyPOSSandNEG, negScope)

**sentences**: ArrayList of sentences you want to check for negations.

**rules**: ArrayList of rules (best to supply in the format of HITEx rules as the file "hitex\_negexrules.negex" shows. IMPORTANT not to have extra white spaces in rule lines because rules are sorted (in GenNegEx) by length in descending order so longest rules will be matched first.

**phrases**: ArrayList of terms we want to check for negation in the sentences (for example, "diabetes", "sudden death syndrome", etc...). There is no limitation what can be a term. It can be CUI from the UMLS or an English word.

**fillerString**: String to use as white space replacement in multi-word terms. So, if you chose underscore as fillerString then the term "sudden death syndrome" will be processed as "sudden\_death\_syndrome".

**negatePossible**: boolean and if set to "true" then POSSIBLE as defined by Chapman will be detected and tagged as [POSSIBLE](POSSIBLE.md). If negatePossible is set to "false" then possible is not tagged.

**showOnlyPOSSandNEG**: boolean and if set to "true" then only [NEGATED](NEGATED.md) and [POSSIBLE](POSSIBLE.md) if
negatePossible was set to "true" in a separate parameter) will be returned as tag.
Other work tags will be removed and the fillerString from rules and terms will be removed, too. See examples for details.

**negScope**: boolean and if set to "true" then the portion of the sentence that is the   scope of the negation (or multiple portions if the sentence includes multiple negations) is returned. Could be combined with negatePossible. When negScope is set to "true" then no tags are shown only the negated (or both the negated and possibly negated) portions of the sentences are returned as ArrayList members. When negScope is set to "true" then the list of phrases (as described in #3 "phrases") is not consulted and the output includes the entire portion of the sentence that is in the scope of the negation (and possible negation). Setting negScope to "true" makes it possible to use GenNegEx in the preprocesing steps before running concept extraction as the GenNegEx output will not depend on the list of phrases. The user still needs to provide a dummy list of phrases (at least one term).