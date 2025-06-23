import os
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
    def __init__(self, model_name, num_labels, learning_rate=2e-5, total_steps=1000):
        """
        Args:
            model_name (str): Hugging Face model repository name.
            num_labels (int): Number of target labels.
            learning_rate (float): Learning rate.
            total_steps (int): Total training steps (for the learning rate scheduler).
        """

        
        super().__init__()
        self.save_hyperparameters()
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
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
    # Parameters
    model_name = "yangheng/deberta-v3-base-absa-v1.1"
    csv_file = os.path.join(os.path.dirname(__file__), 'ASPAGeneratedReviews.csv')
    max_length = 128
    batch_size = 16
    # The base model is trained on 3 labels (negative, neutral, positive). 
    # We keep num_labels=3 to match its architecture.
    num_labels = 3
    learning_rate = 2e-5
    max_epochs = 3

    # Load your CSV file
    df = pd.read_csv(csv_file)
    df = df.rename(columns={"Review": "sentence", "Aspect": "aspect", "Sentiment": "label"})
    
    # Map string labels to integers consistent with the base model's config.
    # "Negative" -> 0, "Neutral" -> 1, "Positive" -> 2.
    label_map = {"Negative": 0, "Neutral": 1, "Positive": 2}
    df['label'] = df['label'].map(label_map)
    df.dropna(subset=['label'], inplace=True)
    df['label'] = df['label'].astype(int)

    # Split the dataset into training and validation sets
    train_df, val_df = train_test_split(df, test_size=0.1, random_state=42)

    # Create datasets and corresponding dataloaders
    train_dataset = ABSADataset(train_df, model_name, max_length)
    val_dataset = ABSADataset(val_df, model_name, max_length)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4, persistent_workers=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, num_workers=4, persistent_workers=True)

    total_steps = len(train_loader) * max_epochs
    model = ABSAClassifier(model_name, num_labels, learning_rate, total_steps)

    checkpoint_callback = ModelCheckpoint(monitor="val_f1", mode="max")
    early_stop_callback = EarlyStopping(monitor="val_f1", patience=3, mode="max")
    lr_monitor = LearningRateMonitor(logging_interval='step')

    trainer = pl.Trainer(
        max_epochs=max_epochs,
        callbacks=[checkpoint_callback, early_stop_callback, lr_monitor],
        accelerator='auto',
        devices=1,
        log_every_n_steps=1
    )

    trainer.fit(model, train_loader, val_loader)

    save_dir = os.path.join(os.path.dirname(__file__), "finetuned-ABSA")
    os.makedirs(save_dir, exist_ok=True)
    model.model.save_pretrained(save_dir)
    # Save the tokenizer from the main process, as they are all the same
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.save_pretrained(save_dir)
    print(f"Fine-tuned model saved to {save_dir}")

if __name__ == "__main__":
    main()
