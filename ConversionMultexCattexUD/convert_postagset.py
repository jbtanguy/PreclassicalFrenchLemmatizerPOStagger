import json
import pandas as pd

def read_csv_like_corpus(file_path, sep):
	csv_file = pd.read_csv(file_path, sep=sep, low_memory=False) # read the csv-like file
	head = csv_file.columns.to_numpy() # get the columns name
	data = csv_file.to_numpy()[1:len(csv_file),:] # get the data (without taking the first row because it is the head=columns name)
	corpus = pd.DataFrame(data=data, columns=head) # convert as a dataframe
	return corpus

def convert_corpus(corpus_before, table, pos_col, lemma_col):
	# Note that a verb in multext can be i) an auxiliary or ii) a "main verb". 
	# In the table conversion cattex --> multext, there "VERcjg": "Vm or Va". So we have to verify the lemma in order to choose between aux or main.
	corpus = corpus_before
	for label_from, label_to in table.items():
		if label_to != 'Vm or Va':
			corpus.loc[corpus[pos_col] == label_from, pos_col] = label_to
		else: # we have to verify the auxiliary
			corpus.loc[(corpus[pos_col] == label_from) & ((corpus[lemma_col] == 'ÊTRE') | (corpus[lemma_col] == 'AVOIR')), pos_col] = 'Va'
			corpus.loc[(corpus[pos_col] == label_from) & (corpus[lemma_col] != 'ÊTRE') & (corpus[lemma_col] != 'AVOIR'), pos_col] = 'Vm'
	return corpus

if __name__ == '__main__':
	print('---------------- If you find mistakes in the conversion tables, please send me an email (jbtanguy56@gmail.com). ----------------')

	# 1. static variables: to modify regarding your case
	_path_corpus = 'res_cattex.csv' # path to the local corpus: it must be a csv-like file (+ first row = columns name = head)
	_path_cenverted_corpus = 'res_cattex_multext.csv'
	_sep = '\t' # seperator
	_pos_col_name = 'pos'
	_lemma_col_name = 'lemma'
	# We can make these and only these conversions:
	#    FROM  ->  TO
	#   presto   cattex
	#   multext  cattex
	#   multext    ud
	#   cattex   multext
	#   cattex     ud
	# Note that I added an ad hoc conversion table 'conversion_table__presto_to_cattex.json'. PRESTO was supposed to be labeled in Cattex but 
	# there are several labels that are not in the standard multext POS-tags set. So first I converted the PRESTO corpus into Cattex and for
	# the its specific labels I made another conversion table and I converted again the corpus. You can do the same with your proper POS-tags. 
	_from = 'cattex'
	_to = 'multext'

	# 2. convert as a dataframe
	corpus = read_csv_like_corpus(_path_corpus, sep=_sep)

	# 3. process the conversion itself
	table = {}
	if _from == 'multext' and _to == 'cattex':
		table = json.load(open('conversion_table__multex_to_cattex.json'))
	elif _from == 'presto' and _to == 'cattex':
		table = json.load(open('conversion_table__presto_to_cattex.json'))
	elif _from == 'multext' and _to == 'ud':
		table = json.load(open('conversion_table__multex_to_ud.json'))
	elif _from == 'cattex' and _to == 'multext':
		table = json.load(open('conversion_table__cattex_to_multext.json'))
	elif _from == 'cattex' and _to == 'ud':
		table = json.load(open('conversion_table__cattex_to_ud.json'))
	else:
		print('Sorry, the wanted conversion (%s -> %s) is not possible so far.' % (_from, _to))

	if table != {}: # that means we can process the conversion
		new_corpus = convert_corpus(corpus, table, _pos_col_name, _lemma_col_name) # conversion
		new_corpus.to_csv(_path_cenverted_corpus, index=True, sep=_sep)
		print('Conversion done. File saved on here: %s.' % _path_cenverted_corpus)
