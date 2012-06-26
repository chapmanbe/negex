import pyConText.pyConTextGraph.itemData as itemData
'''
SUBOPTIMAL STUDY  
SUBOPTIMAL EXAM
SUBOPTIMAL BOLUSTIMING
SUBOPTIMAL STUDY FOR EVALUATION FOR
SUBOPTIMAL STUDY FOR DETECTION OF
SUBOPTIMAL STUDY
SUBOPTIMAL EXAM
STUDY IS SUBOPTIMAL
suboptimal opacification
BOLUS,HOWEVER IS SUBOPTIMAL
TIMING OF THE BOLUS IS SUBOPTIMAL
SUBOPTIMAL SCAN
SUBOPTIMAL EVALUATION
SUBOPTIMAL PULMONARY EMBOLUS STUDY
STUDY WAS SLIGHTLY SUBOPTIMAL
SUBOPTIMAL STUDY
STUDY IS SUBOPTIMAL
SUBOPTIMAL OPACIFICATION
SUBOPTIMAL STUDY
SUBOPTIMAL BOLUS
CONTRAST BOLUS IS SUBOPTIMAL
SUBOPTIMAL CONTRAST BOLUS
Limited study
LIMITED STUDY DUE TO
Limited examination
LIMITED, BUT NEGATIVE EXAMINATION FOR
LIMITED EXAMINATION
STUDY LIMITED
EVALUATION FOR PULMONARY EMBOLISM IS MARKEDLY LIMITED
MARKEDLY LIMITED SECONDARY TO MOTION ????
LIMITED EXAMINATION FOR
Limited exam
STUDY MODERATELY LIMITED BY MOTION ARTIFACT
LIMITED STUDY
 EVALUATION FOR PULMONARY EMBOLISM IS LIMITED
LIMITED IN EVALUATION 
STUDY IS LIMITED
LIMITED EXAMINATION FOR
NONDIAGNOSTIC EVALUATION FOR
EVALUATION OF THE LOWER LOBE SEGMENTAL ARTERIES IS ESSENTIALLY NONDIAGNOSTICSECONDARY TO
NONDIAGNOSTIC EXAM FOR
'''

peItems = itemData.itemData(
['pulmonary embolism','FINDING',r'''(pulmonary )(artery )?(embol[a-z]+)''',''], 
['pe','FINDING',r'''\bpe\b''',''],
['embolism','FINDING',r'''embol[a-z]+''',''],
['pulmonary embolus','FINDING',r'''pulmonary\sembol[a-z]+''',''],
['pe examination','EXCLUSION',r'''(pulmonary )(artery )?(embol[a-z]+)(exam[a-z]*|study|protocol)''',''],
)

qualities = itemData.itemData(
["suboptimal","QUALITY_FEATURE","","bidirectional"],
["degraded","QUALITY_FEATURE","","bidirectional"],
["limited","QUALITY_FEATURE","","bidirectional"],
["nondiagnostic","QUALITY_FEATURE","","bidirectional"], #fix for pedoc #231
)

examFeatures = itemData.itemData(
["bolus","EXAM_FEATURE",r"""\bbolus""","bidirectional"],
["exam","EXAM_FEATURE",r"exam[a-z]*",""],
["study","EXAM_FEATURE","",""],
["scan","EXAM_FEATURE","",""],
["evaluation for","EXAM_FEATURE","",""],
["evaluation","EXAM_FEATURE","",""],
["contrast bolus","EXAM_FEATURE","","bidirectional"],
#["opacification","EXAM_FEATURE","","bidirectional"],
["bolus timing","EXAM_FEATURE",r"\bbolus[ -]{0,1}timing","bidirectional"], # fixes pedoc #129 dq
)

artifacts = itemData.itemData(
["respiratory motion","ARTIFACT","",""],
["patient motion","ARTIFACT","",""],
["motion","ARTIFACT","",""],
["bulk motion","ARTIFACT","",""],
["artifact","ARTIFACT",r"""artifact(ual)?""",""])


temporal = itemData.itemData()

