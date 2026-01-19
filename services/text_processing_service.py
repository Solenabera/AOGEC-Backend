from nlp import SentenceSplitter, Tokenizer, SpellingChecker, AutoComplete
from dl.inference import check_and_correct, batch_correction

# NLP Utilities (instantiate once)
sentence_splitter = SentenceSplitter.SentenceSplitter()
word_tokenizer = Tokenizer.Tokenizer()
spell_checker = SpellingChecker.SpellingChecker()
autocomplete_engine = AutoComplete.AutoComplete(
    spell_checker.wordSet,
    spell_checker.wordFreq
)

def process_text(text: str):
    sentences = sentence_splitter.split(text)
    final_result = []
    grammar_candidates = []
    grammar_indexes = []

    for i, sentence in enumerate(sentences):
        if not sentence.strip():
            continue

        tokens, _ = word_tokenizer.tokenizer(sentence)
        correction_dict = spell_checker.spellCheck(tokens)

        result = {
            "sentenceIndex": i,
            "originalSentence": sentence,
            "spellingCorrections": correction_dict or {},
            "correctedSentence": ""
        }

        if not correction_dict:
            grammar_candidates.append(sentence)
            grammar_indexes.append(len(final_result))

        final_result.append(result)

    # Grammar correction
    corrected_sentences = batch_correction(grammar_candidates)

    for idx, corrected in zip(grammar_indexes, corrected_sentences):
        final_result[idx]["correctedSentence"] = corrected

    return final_result


def autocomplete_suggestions(query: str):
    return autocomplete_engine.suggest(query)
