import re
import string
from collections import Counter

class SpellingChecker():
	"""SpellingChecker"""
	def __init__(self):
		self.wordDictionary = Counter(self.words(open('AODic.dic').read()))

	def spellCheck(self, tokenList):
		"""Main method"""
		correctDict = {}
		flag = 0
		correctionList = []

		for i, word in enumerate(tokenList):
			corr, cand = self.correction(word.lower())
			# print(corr,cand)
			if word[0].isupper():
				correctionList.append(corr.capitalize())
			else:
				correctionList.append(corr)
			
			if word.lower() != corr:
				flag = 1
				if word[0].isupper():
					correctDict[word] = [i.capitalize() for i in cand]
				else:
					correctDict[word] = cand

		return correctDict

	def words(self, text):
		return re.findall(r"[\w']+", text.lower())

	def P(self, word, N = -1):
		"""Probability of `word`."""
		if N == -1: N = sum(self.wordDictionary.values())
		return (self.wordDictionary[word]/N)

	def correction(self, word):
		"""Most probable spelling correction for word."""
		cand = self.candidates(word)
		if len(cand)>=5:
			cand = cand[:4]
		return max(cand, key = self.P), cand

	def candidates(self, word):
		"""Generate possible spelling corrections for word."""
		return (self.known([word]) or self.known(self.edits1(word)) or self.known(self.edits2(word)) or [word])

	def known(self, words):
		"""The subset of `words` that appear in the dictionary of WORDS."""
		return list(set(w for w in words if w in self.wordDictionary))

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