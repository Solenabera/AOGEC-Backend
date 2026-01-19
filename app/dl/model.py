import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Load tokenizer and model ONCE
tokenizer = T5Tokenizer.from_pretrained("t5-base")
# model = T5ForConditionalGeneration.from_pretrained("AOGEC_Model_Output_2")
model = T5ForConditionalGeneration.from_pretrained("solenabera55/AOGEC")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

print("Torch device:", device)
print("Model loaded on device:", next(model.parameters()).device)
