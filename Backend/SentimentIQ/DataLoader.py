import pandas as pd
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
import torch

# Dataset class for handling text data
# Tensor([[‘CLS’ 101,  877,  674,  785,   23, 2319,  503,  876,  674, 2310]])
class TextDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)



# Function to create datasets from CSV file
def create_datasets(data_file, tokenizer):

    # Splitting data into training and validation sets (20% used for validation)
    data = pd.read_csv(data_file)
    train_texts, val_texts, train_labels, val_labels = train_test_split(data['text'].tolist(), data['label'].tolist(), test_size=0.2)
    

    # Tokenize the text
    # Tokens: ['▁Food', '▁is', '▁great', '▁but', '▁service', '▁was', '▁terrible', '<pad>', '<pad>', '<pad>']
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=128, return_tensors="pt")
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=128, return_tensors="pt")

    #Create a PytTorch Data Type
    train_dataset = TextDataset(train_encodings, train_labels)
    val_dataset = TextDataset(val_encodings, val_labels)
    
    
    return train_dataset, val_dataset

