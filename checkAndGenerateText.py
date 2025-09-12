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

def checkAndGenerateUserText(eachSentence):
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

    return predicted_sentence
