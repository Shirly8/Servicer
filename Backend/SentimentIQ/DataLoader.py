import pandas as pd
from torch.utils.data import Dataset
from transformers import AutoTokenizer
import torch

class ABSADataset(Dataset):
    """
    Tokenized sentence/aspect pair and label.
        {
            'input_ids': tensor([101, 102, 103, 104, 105, 106, 107, 108, 109, 110]),
            'attention_mask': tensor([...]),
            'labels': tensor([1, 2, 3, 4, 5])
        }
    """
    def __init__(self, df, model_name, max_length=128):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.sentences = df['sentence'].tolist()
        self.aspects = df['aspect'].tolist()
        self.labels = df['label'].tolist()
        self.max_length = max_length

    def __len__(self):
        return len(self.sentences)
    


    def __getitem__(self, index):
        sentence = self.sentences[index]
        aspect = self.aspects[index]
        label = self.labels[index]



        # Tokenize the sentence and aspect as a pair
        inputs = self.tokenizer(
            sentence,
            text_pair=aspect,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )


        # Remove batch dimension - dataset is single propered shape for batching
        inputs = {key: val.squeeze(0) for key, val in inputs.items()}
        inputs['labels'] = torch.tensor(label, dtype=torch.long)
        return inputs