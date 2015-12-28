from copy import *;
from libxml2mod import prev
import sys
a={};
EMPTY='<EMPTY>'
gaz = {}

Wi='Wi='
Oi='Oi='
Pi='Pi='
Si='Si='
Wiprev='Wi-1='
Oiprev='Oi-1='
Piprev='Pi-1='
Siprev='Si-1='
Winext='Wi+1='
Oinext='Oi+1='
Pinext='Pi+1='
Sinext='Si+1='
Ti='Ti='
Ti1='Ti-1='
StateSpace= ['<START>','<STOP>','I-PER','B-PER','I-LOC','B-LOC','I-MISC','B-MISC','O','B-ORG','I-ORG'];
neg_inf = -1* float('inf');
ignore_state = set(['<START>','<STOP>', '<JUNK>']);

def load_gazetter(path):
    f = open(path, 'r');
    for line in iter(f):
        splits = line.split();
        for i in range(1, len(splits)):
            gaz.setdefault(splits[0],set()).add(splits[i]);
    f.close()

def load_features_from_weights_file(path):
    f= open(path, 'r');
    count =0;
    for line in iter(f):
        line = line.rstrip();
        splits=  line.split();
        value = float(splits[1]);
        key = splits[0];
        a[key]=value;

def generate_base_features(curr, postag):
    l=[]
    l.append(curr);
    if(curr in ignore_state):
        l.append(curr);
        l.append(postag);
        l.append(curr);
        return l;
    else:
        l.append(curr.lower());
    l.append(postag);
    shape='';
    for c in curr:
        if c.isdigit(): 
            shape=shape+'d';
        elif c.islower():
            shape=shape+'a';
        elif c.isupper():
            shape=shape+'A';
        else :
            shape=shape+c;
    l.append(shape);
    return l;
def generate_features(Wcurr, position, Wprev, Wnext, Tcurr, Tprev):
    completeWeights=0.0;
    tmp=False;
    f14=[];
    f14.append(Wi+Wcurr[0]);
    f14.append(Oi+Wcurr[1]);
    f14.append(Pi+Wcurr[2]);
    f14.append(Si+Wcurr[3]);
#     feature 1 - 4 
    current = Ti+Tcurr
    past = Ti1 +Tprev
    for f in f14:
        feature = f+':'+current
        weight=a.get(feature,0);
        completeWeights+=weight;
        if tmp and weight >0:
            print feature+' ' + str(weight);
#     feature 5
    f5=[];
    
    f5.append(Wiprev+Wprev[0]);
    f5.append(Oiprev+Wprev[1]);
    f5.append(Piprev+Wprev[2]);
    f5.append(Siprev+Wprev[3]);
    f5.append(Winext+Wnext[0]);
    f5.append(Oinext+Wnext[1]);
    f5.append(Pinext+Wnext[2]);
    f5.append(Sinext+Wnext[3]);
    for f in f5:
        feature = f+':'+current;
        weight = a.get(feature,0);
        completeWeights+=weight;
        if tmp and weight>0:
            print feature+' ' + str(weight);
#     feature 6
    for f1 in f14:
        for f2 in f5:
            feature= f1+':'+f2 +':'+current;
            weight = a.get(feature,0)
            completeWeights+=weight;
            if tmp and weight>0 :
                print feature+' ' + str(weight);
     
#     feature 7
    feature = past +':'+current
    weight = a.get(feature,0);
    completeWeights+=weight;
    if tmp :
            print feature+' ' + str(weight);
    for f in f14:
        feature = f+':'+past +':'+current;
        weight = a.get(feature,0);
        completeWeights+=weight;
        if tmp and weight>0:
                print feature+' ' + str(weight);
    for f in f5:
        feature = f+':'+past +':'+current;
        weight = a.get(feature,0);
        completeWeights+=weight;
        if tmp and weight>0:
                print feature+' ' + str(weight);
#     feature 8
    key='PREi='
    for k in xrange(1,min(5,len(Wcurr[0])+1)):
        feature = key+Wcurr[0][:k]+':'+current
        weight = a.get(feature,0);
        completeWeights+=weight;
        if tmp and weight>0:
                print feature+' ' + str(weight);
#     feature 9
    key='GAZi=True'
    key1='GAZi=False'
    if(Tcurr.find('-')>0):
        basetag = Tcurr.split('-')[1];
        if Wcurr[0] in gaz.get(basetag,set()):
            feature = key+':'+current
            weight = a.get(feature,0);
            completeWeights+=weight;
            if tmp :
                    print feature+' ' + str(weight);
        else :
            feature = key1+':'+current
            weight = a.get(feature,0);
            completeWeights+=weight;
            if tmp :
                    print feature+' ' + str(weight);
    else:
        feature = key1+':'+current
        weight = a.get(feature,0);
        completeWeights+=weight;
        if tmp :
                print feature+' ' + str(weight);
#     feature 10
    key='CAPi='
    feature = key+str(Wcurr[0][0].isupper())+':'+current
    weight = a.get(feature,0);
    completeWeights+=weight;
    if tmp and weight>0:
            print feature+' ' + str(weight);
#     feature 11
    key = 'POSi='
    feature = key+str(position)+':'+current
    weight = a.get(feature,0);
    completeWeights+=weight;
    if tmp:
            print feature+' ' + str(weight);
    return completeWeights;

def decode(observations):
    q=[];
    q.append({});
    path = {};
    n = len(observations);
#     base case
    for state in StateSpace:
        q[0][state]=neg_inf;
        path[state]=[state];
    
    q[0]['<START>']=1;
    
    for t in range(1, n):
        q.append({});
        prev = generate_base_features(observations[t-1][0], observations[t-1][1]);
        curr = generate_base_features(observations[t][0], observations[t][1]);
        if t+1==len(observations):
            next1 = generate_base_features('<JUNK>', '<JUNK>');
        else :
            next1 = generate_base_features(observations[t+1][0], observations[t+1][1]);
        newPath={}
        for Tcurr in StateSpace:
            best_prob = neg_inf;
            best_state= '';
            
            for Tprev in StateSpace:
                prob = q[t-1][Tprev] + generate_features(curr, t, prev, next1, Tcurr, Tprev);
                if prob > best_prob:
                    best_prob = prob;
                    best_state = Tprev;
            
            q[t][Tcurr] = best_prob;
            newPath[Tcurr] = deepcopy(path[best_state]);
            newPath[Tcurr].append(Tcurr);
    
        path = newPath;
    return path['<STOP>'];
            
            
            
def testModel(filePath, outPath):
    f = open(filePath);
    w = open(outPath,'w')
    sentence=[('<START>','<START>')];
    correct_tags=['<CSTART>'];
    tokensList=[];
    count =0;
    for line in iter(f):
        tokensList.append(line.rstrip());
        splits= line.split();
        if len(splits)==0 :
            print "tagging sentence: "+str(count);
            count+=1;
            sentence.append(('<STOP>','<STOP>'));
            correct_tags.append('<STOP>');
            print sentence;
            print correct_tags;
            
            taggged_sentence = decode(sentence);
            print taggged_sentence;
            for i in xrange(1, len(taggged_sentence)-1):
                w.write(tokensList[i-1]+" "+taggged_sentence[i]+'\n');
            w.write('\n');
            
            sentence=[('<START>','<START>')];
            correct_tags=['<CSTART>'];
            tokensList=[];
        else :
            sentence.append((splits[0],splits[1]));
            correct_tags.append(splits[3]);
    f.close();
    w.close();
    

if __name__ == '__main__':
    if len(sys.argv)<3:
        print "USAGE python linear_model weightsFIle GazetterFile TestingFile OutputFIle";
    else:
        load_features_from_weights_file(sys.argv[1]);
        load_gazetter(sys.argv[2]);
        testModel(sys.argv[3],sys.argv[4] );












