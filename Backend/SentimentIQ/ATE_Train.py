import os
import torch
import pandas as pd
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping, LearningRateMonitor
from transformers import AutoTokenizer, AutoModelForTokenClassification, get_linear_schedule_with_warmup
from seqeval.metrics import f1_score as seqeval_f1_score
from seqeval.scheme import IOB2 # For BIO tagging scheme

# --- Dataset for Token Classification ---
class ATEDataset(Dataset):
    def __init__(self, file_path, tokenizer, label_map, max_length=128):
        self.tokenizer = tokenizer
        self.label_map = label_map
        self.max_length = max_length
        self.sentences, self.labels = self._read_data(file_path)

    def _read_data(self, file_path):
        sentences, labels = [], []
        words, tags = [], []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() == "":
                    if words:
                        sentences.append(words)
                        labels.append(tags)
                        words, tags = [], []
                else:
                    try:
                        word, tag = line.strip().split('\t')
                        words.append(word)
                        tags.append(tag)
                    except ValueError:
                        print(f"Skipping malformed line: {line.strip()}")
        # Add the last sentence if the file doesn't end with a newline
        if words:
            sentences.append(words)
            labels.append(tags)
        return sentences, labels

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, index):
        words = self.sentences[index]
        labels = self.labels[index]

        # Tokenize and align labels
        tokenized_inputs = self.tokenizer(words, truncation=True, is_split_into_words=True, padding='max_length', max_length=self.max_length)
        word_ids = tokenized_inputs.word_ids()
        
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100) # Special token
            elif word_idx != previous_word_idx:
                label_ids.append(self.label_map[labels[word_idx]]) # Label for the first token of a word
            else:
                label_ids.append(-100) # Only label the first token of a multi-token word
            previous_word_idx = word_idx
            
        tokenized_inputs["labels"] = torch.tensor(label_ids, dtype=torch.long)
        # Squeeze tensors to remove batch dimension
        return {key: val for key, val in tokenized_inputs.items()}

# --- PyTorch Lightning Module for ATE ---
class ATEClassifier(pl.LightningModule):
    def __init__(self, model_name, num_labels, label_map, learning_rate=3e-5, total_steps=1000):
        super().__init__()
        self.save_hyperparameters()
        self.model = AutoModelForTokenClassification.from_pretrained(model_name, num_labels=num_labels)
        self.learning_rate = learning_rate
        self.total_steps = total_steps
        self.validation_step_outputs = []
        # Create inverse mapping from index to label string
        self.id_to_label = {v: k for k, v in label_map.items()}

    def forward(self, input_ids, attention_mask, labels=None):
        return self.model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)

    def training_step(self, batch, batch_idx):
        outputs = self(**batch)
        loss = outputs.loss
        self.log("train_loss", loss)
        return loss

    def validation_step(self, batch, batch_idx):
        outputs = self(**batch)
        logits = outputs.logits
        preds = torch.argmax(logits, dim=2)
        self.validation_step_outputs.append({'preds': preds, 'labels': batch['labels']})
        self.log("val_loss", outputs.loss)
        return outputs.loss

    def on_validation_epoch_end(self):
        # Convert all predictions and labels to lists of strings
        true_labels = []
        pred_labels = []
        for output in self.validation_step_outputs:
            for i in range(output['labels'].shape[0]): # Iterate through batch
                true_seq = [self.id_to_label.get(l.item(), 'O') for l in output['labels'][i] if l != -100]
                pred_seq = [self.id_to_label.get(p.item(), 'O') for p, l in zip(output['preds'][i], output['labels'][i]) if l != -100]
                true_labels.append(true_seq)
                pred_labels.append(pred_seq)

        f1 = seqeval_f1_score(true_labels, pred_labels, mode='strict', scheme=IOB2)
        self.log("val_f1", f1, prog_bar=True)
        self.validation_step_outputs.clear()

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.learning_rate)
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=int(0.1 * self.total_steps), num_training_steps=self.total_steps
        )
        return [optimizer], [{'scheduler': scheduler, 'interval': 'step'}]

def main():
    # --- Parameters ---
    model_name = "distilbert-base-uncased"
    data_file = os.path.join(os.path.dirname(__file__), 'ATE_Training_Data.tsv')
    max_length = 128
    batch_size = 16
    learning_rate = 3e-5
    max_epochs = 5 # NER tasks can benefit from a few more epochs

    # --- Data Loading and Preparation ---
    if not os.path.exists(data_file) or os.path.getsize(data_file) == 0:
        print(f"Training data not found or is empty at {data_file}.")
        print("Please run ATE_Generator.py first to create the training data.")
        return

    label_map = {"O": 0, "B-ASPECT": 1, "I-ASPECT": 2}
    num_labels = len(label_map)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # We need to split our sentences into train/val sets before creating datasets
    temp_dataset = ATEDataset(data_file, tokenizer, label_map, max_length)
    train_indices, val_indices = train_test_split(range(len(temp_dataset)), test_size=0.2, random_state=42)
    
    train_dataset = torch.utils.data.Subset(temp_dataset, train_indices)
    val_dataset = torch.utils.data.Subset(temp_dataset, val_indices)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, num_workers=0)

    # --- Model Training ---
    total_steps = len(train_loader) * max_epochs
    model = ATEClassifier(model_name, num_labels, label_map, learning_rate, total_steps)

    checkpoint_callback = ModelCheckpoint(monitor="val_f1", mode="max", filename='best-ate-checkpoint')
    early_stop_callback = EarlyStopping(monitor="val_f1", patience=3, mode="max")
    
    trainer = pl.Trainer(
        max_epochs=max_epochs,
        callbacks=[checkpoint_callback, early_stop_callback],
        accelerator='auto',
        devices=1,
        log_every_n_steps=10
    )

    trainer.fit(model, train_loader, val_loader)

    # --- Save Final Model ---
    save_dir = os.path.join(os.path.dirname(__file__), "finetuned-ATE")
    os.makedirs(save_dir, exist_ok=True)
    model.model.save_pretrained(save_dir)
    tokenizer.save_pretrained(save_dir)
    print(f"Fine-tuned ATE model saved to {save_dir}")

if __name__ == "__main__":
    main() 