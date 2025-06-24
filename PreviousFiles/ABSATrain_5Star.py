import os
import sys
import time
import torch
import pandas as pd
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint, LearningRateMonitor

from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup

# Custom Dataset for ABSA training
class ABSADataset(Dataset):
    def __init__(self, df, model_name, max_length=128):
        """
        Args:
            df (pandas.DataFrame): DataFrame with columns 'sentence', 'aspect', 'label'
            model_name (str): Hugging Face model repository name for the tokenizer.
            max_length (int): Maximum token length for each sequence
        """
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
        # Remove the extra batch dimension
        inputs = {key: val.squeeze(0) for key, val in inputs.items()}
        inputs['labels'] = torch.tensor(label, dtype=torch.long)
        return inputs

# PyTorch Lightning Module for fine-tuning
class ABSAClassifier(pl.LightningModule):
    def __init__(self, model_name, num_labels, learning_rate=2e-5, total_steps=1000, ignore_mismatched_sizes=False):
        """
        Args:
            model_name (str): Hugging Face model repository name.
            num_labels (int): Number of target labels.
            learning_rate (float): Learning rate.
            total_steps (int): Total training steps (for the learning rate scheduler).
            ignore_mismatched_sizes (bool): Whether to ignore layer size mismatches on load.
        """
        super().__init__()
        self.save_hyperparameters()
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name, 
            num_labels=num_labels, 
            ignore_mismatched_sizes=ignore_mismatched_sizes
        )
        self.learning_rate = learning_rate
        self.total_steps = total_steps
        self.validation_step_outputs = []

    def forward(self, input_ids, attention_mask, token_type_ids=None, labels=None):
        return self.model(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, labels=labels)

    def training_step(self, batch, batch_idx):
        outputs = self(**batch)
        loss = outputs.loss
        self.log("train_loss", loss, on_step=True, on_epoch=True)
        return loss

    def validation_step(self, batch, batch_idx):
        outputs = self(**batch)
        loss = outputs.loss
        logits = outputs.logits
        preds = torch.argmax(logits, dim=1)
        labels = batch['labels']
        self.log("val_loss", loss, prog_bar=True)
        self.validation_step_outputs.append({"loss": loss, "preds": preds, "labels": labels})
        return loss

    def on_validation_epoch_end(self):
        if not self.validation_step_outputs:
            return
        all_preds = torch.cat([x["preds"] for x in self.validation_step_outputs])
        all_labels = torch.cat([x["labels"] for x in self.validation_step_outputs])
        f1 = f1_score(all_labels.cpu(), all_preds.cpu(), average='weighted')
        self.log("val_f1", f1, prog_bar=True)
        self.validation_step_outputs.clear()  # free memory

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.learning_rate)
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=0, num_training_steps=self.total_steps
        )
        return [optimizer], [{'scheduler': scheduler, 'interval': 'step'}]

def main():
    base_model_name = os.path.join(os.path.dirname(__file__), '5star-absa-v2')
    output_model_name = "5star-absa-v3" 
    csv_file = os.path.join(os.path.dirname(__file__), 'ASPAGeneratedReviews_5Star_Complex.csv')
    max_length = 128
    batch_size = 15
    num_labels = 5 
    learning_rate = 2e-5
    max_epochs = 3

    # Load the dataset
    df = pd.read_csv(csv_file, usecols=[0, 1, 2])
    df.columns = ["sentence", "aspect", "label"]
    df['label'] = pd.to_numeric(df['label'], errors='coerce')
    df.dropna(subset=['sentence', 'aspect', 'label'], inplace=True)
    df['label'] = df['label'].astype(int) - 1
    df['sentence'] = df['sentence'].astype(str)
    df['aspect'] = df['aspect'].astype(str)

    # Split the dataset into training and validation sets
    train_df, val_df = train_test_split(df, test_size=0.1, random_state=42)

    # Create datasets and corresponding dataloaders
    train_dataset = ABSADataset(train_df, base_model_name, max_length)
    val_dataset = ABSADataset(val_df, base_model_name, max_length)
    
    num_workers = 4 if os.name == 'posix' else 0
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, persistent_workers=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, num_workers=num_workers, persistent_workers=True)

    total_steps = len(train_loader) * max_epochs
    
    # Initialize the classifier
    # Pass ignore_mismatched_sizes=True because the base model has 3 labels but we want 5.
    # This will discard the old head and add a new, randomly initialized one.
    model = ABSAClassifier(
        base_model_name, 
        num_labels, 
        learning_rate, 
        total_steps,
        ignore_mismatched_sizes=True
    )

    checkpoint_callback = ModelCheckpoint(monitor="val_f1", mode="max")
    early_stop_callback = EarlyStopping(monitor="val_f1", patience=3, mode="max")
    lr_monitor = LearningRateMonitor(logging_interval='step')

    trainer = pl.Trainer(
        max_epochs=max_epochs,
        callbacks=[checkpoint_callback, early_stop_callback, lr_monitor],
        accelerator='auto',
        devices=1,
        log_every_n_steps=10
    )

    trainer.fit(model, train_loader, val_loader)

    # Save the final model to the new directory
    save_dir = os.path.join(os.path.dirname(__file__), output_model_name)
    os.makedirs(save_dir, exist_ok=True)
    model.model.save_pretrained(save_dir)

    # Save the tokenizer from the base model
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    tokenizer.save_pretrained(save_dir)

if __name__ == "__main__":
    main()
