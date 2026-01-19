import re

class Tokenizer():
	"""docstring for Tokenizer"""
	def __init__(self):
		self.word_end = re.compile("([\s,:;.!?]+)$")
		self.whitespace = re.compile("\s+$")
		self.nonword = re.compile("([\s,:;]+)")

	def tokenizer(self,sentence):
		word_matches=sentence.split()
		whitespace_word_matches = self.nonword.split(sentence)
		
		j = len(word_matches)-1
		while j >= 0:
			w = word_matches[j]
			w_end_match = self.word_end.search(w)
			if w_end_match:
				stem = w[:len(w)-len(w_end_match.group(1))]
				if stem != '': 
					word_matches[j] = stem
				else: 
					word_matches.pop(j)
			j = j - 1
		
		return word_matches, whitespace_word_matches

if __name__ == '__main__':
	tk = Tokenizer()
	print (tk.tokenizer('Inni kaleessa  dhufe.'))
