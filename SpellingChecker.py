import re
import string
from collections import Counter
from functools import lru_cache

class SpellingChecker():
	"""SpellingChecker"""
	def __init__(self):
		# self.wordDictionary = Counter(self.words(open('AODic.dic').read()))
		# self.wordDictionary = Counter(self.words(open('NewAODictionary.dic.txt').read()))
		
		words = self.words(open('NewAODictionary.dic.txt').read())
		self.wordSet = set(words)          # FAST lookup
		self.wordFreq = Counter(words)     # For ranking

		self.alphabets = string.ascii_lowercase
		self.ALPHABETS = string.ascii_uppercase
		self.digits = string.digits


	def spellCheck(self, tokenList):
		"""Main method"""
		correctDict = {}

		for i, word in enumerate(tokenList):
			if len(word) <= 2:
					continue			
			else:
				# if 
				corr, cand = self.correction(word.lower())
				
				if word.lower() != corr:
					if word[0].isupper():
						correctDict[word] = [i.capitalize() for i in cand]
					else:
						correctDict[word] = cand

		return correctDict

	def words(self, text):
		return re.findall(r"[\w']+", text.lower())
	
	def P(self, word, N=None):
		"""Probability of `word`."""
		if N is None:
			N = sum(self.wordFreq.values())
		return self.wordFreq[word] / N

	@lru_cache(maxsize=50000)
	def correction(self, word):
		"""Most probable spelling correction for word."""
		cand = self.candidates(word)
		if len(cand) > 4:
			cand = cand[:4]
		return max(cand, key=self.P), cand

	def candidates(self, word):
		"""Generate possible spelling corrections for word."""
		if word in self.wordSet:
			return [word]   # no edits needed
		return (
			self.known(self.edits1(word)) or
			self.known(self.edits2(word)) or
			[word]
		)

	def known(self, words):
		"""The subset of `words` that appear in the dictionary of WORDS."""
		return [w for w in words if w in self.wordSet]

	def edits1(self, word):
		"""All edits that are one edit away from `word`."""
		letters    = "abcdefghijklmnopqrstuvwxyz'"
		splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
		deletes    = [L + R[1:]               for L, R in splits if R]
		transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
		replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
		inserts    = [L + c + R               for L, R in splits for c in letters]
		return set(deletes + transposes + replaces + inserts)

	def edits2(self, word):
		"""All edits that are two edits away from `word`."""
		return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

	def suggested_word(self, wordlist):
		for i in wordlist:
			return self.candidates(i)

if __name__ == '__main__':
	spell = SpellingChecker()
	# print(spell.spellCheck(['Innin','booda','dhufte']))
	print(spell.spellCheck(["BAAAY'EE","obbbo","mana"]))
	# print(spell.suggested_word(["Obbbo"]))