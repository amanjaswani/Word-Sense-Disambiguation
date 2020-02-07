# -*- coding: utf-8 -*-
"""Word Sense Disambiguation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18BbqVjrH9OXre4sU21r_FdhnKAchbjGn
"""

import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
from nltk.corpus import wordnet
import numpy as np

# Get Input
#sentence = input("Enter a Sentence : ")
sentence = "There is a financial institute near the river bank."
words = nltk.word_tokenize(sentence)

# Lemmatization
lemmatizer = WordNetLemmatizer()
for i in range(len(words)):
  words[i] = lemmatizer.lemmatize(words[i])

# Remove Stopwords and unknown words
words = [w for w in words if w not in stop_words]
for word in words:
  if not wordnet.synsets(word):
    words.remove(word)

words

# Word Similarity Matrix - W (Co-occurrence graph)
word_similarity_matrix = [[0 for i in range(len(words))] for j in range(len(words))]
for i in range(len(words)):
  for j in range(len(words)):
    if i == j:
      continue

    # Dice coefficient
    bigram1 = set(words[i])
    bigram2 = set(words[j])
    word_similarity_matrix[i][j] = len(bigram1 & bigram2) * 2.0 / (len(bigram1) + len(bigram2))

word_similarity_matrix

# N-Gram graph
n_gram_graph = [(words[i], words[i+1]) for i in range(0, len(words)-1)]

n_gram_graph

# Mean of Co-occurrence graph
avg = 0
for i in range(len(words)):
  for j in range(len(words)):
    avg += word_similarity_matrix[i][j]
avg = avg/(len(words)*len(words))

# Similarity n-gram graph
for i in range(0, len(words)):
  for j in range(0, len(words)):
    if i == j:
      continue
    if (words[i], words[j]) in n_gram_graph:
      word_similarity_matrix[i][j] += avg
      word_similarity_matrix[i][j] = word_similarity_matrix[i][j]
      word_similarity_matrix[j][i] += avg
      word_similarity_matrix[j][i] = word_similarity_matrix[j][i]

word_similarity_matrix

# Sense Extraction
word_count = 0
all_synsets = []  # List C in step 2
sense_count = np.zeros(len(words), dtype=int)

for word in words:
  word_synset=[]
  for synset in wordnet.synsets(word):
    word_synset.append(synset)
    
  unique_word_synsets = []
  for synset in word_synset:
    if synset not in unique_word_synsets:
      unique_word_synsets.append(synset)
      
  if not len(unique_word_synsets) <= 5:   # Number of unique senses = 5 (assumption)
      unique_word_synsets = unique_word_synsets[0:5]
  
  for synset in unique_word_synsets:
    all_synsets.append(synset)
      
  sense_count[word_count] = len(unique_word_synsets)
  word_count +=1

print (all_synsets)
print (sense_count)

sense_start_index = [0]
for i in range(len(sense_count)-1):
  sense_start_index.append(sense_start_index[i]+sense_count[i])
  
sense_start_index

#Strategy Space
strategy_space = np.zeros((len(words), len(all_synsets)), dtype=float)


# Initializing strategy space with sij = 1/|Mi|,if sense j is in Mi, else 0
start_index=0
for i in range(len(words)):
  for j in range(start_index, start_index+sense_count[i]):
    strategy_space[i][j] = 1.0/sense_count[i];

  start_index += sense_count[i]

strategy_space

# Pay-off (Z) using sense similarity matrix

sense_similarity_matrix = np.zeros((len(all_synsets), len(all_synsets)), dtype=float)
for i in range(len(all_synsets)):
  for j in range(i, len(all_synsets)):
    similarity = all_synsets[i].wup_similarity(all_synsets[j])
    
    if similarity == None:
      similarity = 0
    sense_similarity_matrix[i][j] = similarity
    sense_similarity_matrix[j][i] = similarity

sense_similarity_matrix

# Replicator dynamics
number_of_iterations = 10

for i in range(number_of_iterations):
  for player in range(len(words)):

    player_payoff = 0

    strategy_payoff = np.zeros((sense_count[player], 1), dtype=float)

    sense_preference_player = np.array(strategy_space[player:player+1, sense_start_index[player]:sense_start_index[player]+sense_count[player]])


#     print ("Player word senses")
#     print (sense_preference_player)
#     print (sense_preference_player.shape)
#     print ("\n")

    for neighbour in range(len(words)):
      if neighbour==player:
        continue

      payoff_matrix = np.array(sense_similarity_matrix[sense_start_index[player]:sense_start_index[player]+sense_count[player], sense_start_index[neighbour]:sense_start_index[neighbour]+sense_count[neighbour]], dtype=float)

#       print ("\nPayoff")
#       print (payoff_matrix)
#       print (payoff_matrix.shape)

      sense_preference_neighbour = np.array(strategy_space[neighbour:neighbour+1, sense_start_index[neighbour]:sense_start_index[neighbour]+sense_count[neighbour]])
      sense_preference_neighbour = sense_preference_neighbour.transpose()

#       print ("\nNeighbour word Senses")
#       print (sense_preference_neighbour)
#       print (sense_preference_neighbour.shape)

      temp_matrix = np.dot(payoff_matrix, sense_preference_neighbour)
      current_payoff = temp_matrix * word_similarity_matrix[player][neighbour]

      strategy_payoff = np.add(current_payoff, strategy_payoff)

#       print ("\nCurrent Payoff and Strategy")
#       print (current_payoff)
#       print (current_payoff.shape)
#       print (strategy_payoff)
#       print (strategy_payoff.shape)

      player_payoff += np.dot(sense_preference_player, current_payoff)

#       print ("\nPlayer Payoff")
#       print (player_payoff)

    updation_values = np.ones(strategy_payoff.shape)
    if not player_payoff == 0:
      updation_values = np.divide(strategy_payoff, player_payoff)

#     print ("\nUpdation Vlues")
#     print (updation_values)


    for j in range(0, sense_count[player]):
      strategy_space[player][sense_start_index[player]+j] = strategy_space[player][sense_start_index[player]+j] * updation_values[j]

#     print ("\nStrategy Space Updated")
#     print (strategy_space)

print ("\nStrategy Space Updated")
print (strategy_space)

# Display Meaning
for word in range(len(words)):
  print(words[word] + ": ", end="")
  max_value = 0
  required_synset = None
  for synset in range(len(all_synsets)):
    if strategy_space[word][synset] > max_value:
        max_value = strategy_space[word][synset]
        required_synset = all_synsets[synset]
  print(required_synset.definition())

