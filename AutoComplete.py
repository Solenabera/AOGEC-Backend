from collections import defaultdict

class AutoComplete:
    def __init__(self, wordSet, wordFreq=None):
        self.prefixMap = defaultdict(set)
        self.wordSet = set(word.lower() for word in wordSet)  # Store wordSet for exact match checking
        self.wordFreq = wordFreq  # Store word frequency for ranking
        for word in wordSet:
            word = word.lower()
            for i in range(1, min(len(word), 15)):
                self.prefixMap[word[:i]].add(word)

    def suggest(self, prefix, limit=10):
        print(prefix)
        prefix = prefix.lower()
        suggestions = list(self.prefixMap.get(prefix, []))
        
        # Check if prefix is an exact match in the dictionary
        exact_match = None
        if prefix in self.wordSet:
            exact_match = prefix
        
        # Get other completions (words that start with prefix but are different)
        other_completions = [word for word in suggestions if word != prefix]
        
        # Sort other completions by:
        # 1. Length similarity (shorter words first - closer completions)
        # 2. Frequency (if available - more common words first)
        def sort_key(word):
            length_score = len(word)  # Shorter words first
            freq_score = 0
            if self.wordFreq:
                # Higher frequency = lower score (so more frequent comes first)
                freq_score = -self.wordFreq.get(word, 0)
            return (length_score, freq_score)
        
        other_completions.sort(key=sort_key)
        
        # If exact match exists, put it at the top, then add other completions
        if exact_match:
            result = [exact_match] + other_completions
        else:
            result = other_completions
        
        return result[:limit]
