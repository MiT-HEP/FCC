# FCC

Example of usage:
~~~
text2workspace.py  -P  python.FCCModels:fccHiggs test/simple-fcc.txt
combine -M MultiDimFit -P kappaZ -P width --floatOtherPOIs=0  test/simple-fcc.root
~~~

if model is moved in scram structures:
~~~
text2workspace.py  -P  HiggsAnalysis.CombinedLimit.FCCModels:fccHiggs test/simple-fcc.txt
~~~

