#!pip install datasketch

import numpy as np
import pandas as pd
import re
import time
from datasketch import MinHash, MinHashLSHForest
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('punkt')

#Preproccessing the input dataset
def preprocess(text): 
  stop_words = set(stopwords.words('english'))
  text = re.sub(r'[^\w\s]','',text)
  txt = text.lower()

  word_tokens = word_tokenize(txt)
  text = [w for w in word_tokens if not w.lower() in stop_words]
  text = []
  
  for w in word_tokens:
      if w not in stop_words:
          text.append(w)
  return text
#Creating the forest and training the forest based on dataset
def get_forest(data, perms):
    start_time = time.time()
    
    minhash = []
    
    for text in data['text']:
        tokens = preprocess(text)
        m = MinHash(num_perm=perms)
        for s in tokens:
            m.update(s.encode('utf8'))
        minhash.append(m)
        
    forest = MinHashLSHForest(num_perm=perms)
    
    for i,m in enumerate(minhash):
        forest.add(i,m)
        
    forest.index()

    print('It took %s seconds to build forest.' %(time.time()-start_time))
    return forest
#Predicting based the query and trained LSH forest
def predict(text, database, perms, num_results, forest):
    start_time = time.time()
    
    tokens = preprocess(text)
    m = MinHash(num_perm=perms)
    for s in tokens:
        m.update(s.encode('utf8'))
        
    idx_array = np.array(forest.query(m, num_results))
    if len(idx_array) == 0:
        return None 
    
    result = database.iloc[idx_array]['name']
    
    print('It took %s seconds to query forest.' %(time.time()-start_time))
    return result

#define number of permutations and dataset
permutations = 128 #increasing permutations may result in higher accuracy but it also increases proccessing power and thus proccessing time (default is usually 128)
db = pd.read_csv('dataset.csv') #add your dataset here
db = db.drop_duplicates(subset="name")
db['text'] = db['name'] + ' ' + db['description'] #choose which colomns of your dataset you want the algorithm to consider based on the query
forest = get_forest(db, permutations)

#Enter the query, result would be the closest recommendations
num_recommendations = 5
title = input()
result = predict(title, db, permutations, num_recommendations, forest)
print('\n Top Recommendations are \n', result)
