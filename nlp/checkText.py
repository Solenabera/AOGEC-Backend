import torch
import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration
from torch.utils.data import Dataset, DataLoader
import numpy as np

from SpellingChecker import SpellingChecker
from Tokenizer import Tokenizer
from SentenceSplitter import SentenceSplitter

tokenizer = T5Tokenizer.from_pretrained('t5-base')
# model = T5ForConditionalGeneration.from_pretrained('AOGEC_Model_Output_1')
model = T5ForConditionalGeneration.from_pretrained('AOGEC_Model_Output_2')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.eval()
model.to(device)

def checkText(userText):
    print("Check User Text: ", userText)
    if not userText:
        return "Input Text is Empty!"
    textSplitter = SentenceSplitter()
    sentences = textSplitter.split(userText)
    for sentence in sentences:
        print(sentence)

def generate_text(eachSentence):
    if not eachSentence:
        return "Input text is empty."

    input_sentence = eachSentence
    max_length = 128

    input_ids = tokenizer.encode(input_sentence, max_length=128, truncation=True, padding='max_length', return_tensors="pt").to(device)

    outputs = model.generate(input_ids=input_ids, 
                             decoder_start_token_id=model.config.pad_token_id,
                             max_length=max_length, 
                             num_beams=5)
    
    predicted_sentence = tokenizer.decode(outputs[0], skip_special_tokens=True)

#     spell = SpellingChecker()
#     print(spell.spellCheck(["BAAAY'EE","obbbo","mana"]))
#     tk = Tokenizer()
#     print (tk.tokenizer('Inni kaleessa  dhufe.'))
    # sample = ["I love U.S.A. very much.",'"Do split me." Will you?',
	# 		"This is e.g. Mr. Smith, who talks slowly... But this is another sentence."]
    sample = ['I love U.S.A. very much. "Do split me." Will you? This is e.g. Mr. Smith, who talks slowly... But this is another sentence.']
    
#     sample2 = ["US unveils world's most powerful supercomputer, beats China. The US \
# has unveiled the world's most powerful supercomputer called 'Summit', \
# beating the previous record-holder China's Sunway TaihuLight. With a \
# peak performance of 200,000 trillion calculations per second, it is over \
# twice as fast as Sunway TaihuLight, which is capable of 93,000 trillion \
# calculations per second. Summit has 4,608 servers, which reportedly take up \
# the size of two tennis courts."]
    
    sp = SentenceSplitter()
    
    for i in sample:
        sent = sp.split(i)
        for s in sent:
                print("\nSentence :" , s)

    return predicted_sentence

def process_user_text(input_text):
    return f"You provided the text: {input_text}"


