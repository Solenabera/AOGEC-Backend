import os
import sys
import SentenceSplitter
import Tokenizer
import SpellingChecker
from collections import Counter

class TextChecker:
	"""main class"""
	def __init__(self):
		self.spellCheck = SpellingChecker.SpellingChecker()
		self.tokenizer = Tokenizer.Tokenizer()
		return
	
	def check(self, text):
		"""Check a text string and return the results as an XML formatted list 
		of possible errors."""
		splitter = SentenceSplitter.SentenceSplitter()
		sentences = splitter.split(text)

		wholeSpellCheck = {}
		finalResult = {}
		for i, sentence in enumerate(sentences):
			if not sentence: 
				continue
			tokenList, tokenList_for_whitespace = self.tokenizer.tokenizer(sentence)
			correctionDict = self.spellCheck.spellCheck(tokenList)
			print(correctionDict)
			if correctionDict:
				wholeSpellCheck.update(correctionDict)
		
		finalResult["spell"] = wholeSpellCheck
		return finalResult