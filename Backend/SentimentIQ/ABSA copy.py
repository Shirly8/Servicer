import os
import torch
import pandas as pd
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split

import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint, LearningRateMonitor
from pytorch_lightning.loggers import TensorBoardLogger

from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
import torchmetrics

# Custom Dataset for ABSA training
class ABSADataset(Dataset):
    def __init__(self, df, tokenizer, max_length=128):
        """
        Args:
            df (pandas.DataFrame): DataFrame with columns 'Review', 'Aspect', 'Sentiment'
            tokenizer: Hugging Face tokenizer instance
            max_length (int): Maximum token length for each sequence
        """
        self.tokenizer = tokenizer
        self.sentences = df['Review'].tolist()
        self.aspects = df['Aspect'].tolist()
        self.labels = df['Sentiment'].tolist()  # These should be numeric (0 or 1)
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
        # Use ignore_mismatched_sizes to ignore classifier head size mismatch.
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name, 
            num_labels=num_labels, 
            ignore_mismatched_sizes=True
        )
        self.learning_rate = learning_rate
        self.total_steps = total_steps
        # Initialize torchmetrics F1 Score. Here we use task="multiclass" for a binary problem.
        self.val_f1 = torchmetrics.F1Score(task="multiclass", num_classes=num_labels, average='weighted')

    def forward(self, input_ids, attention_mask, labels=None, **kwargs):
        return self.model(input_ids=input_ids, attention_mask=attention_mask, labels=labels, **kwargs)

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
        # Update the F1 metric with current predictions and labels
        self.val_f1.update(preds, labels)
        self.log("val_loss", loss, prog_bar=True, on_epoch=True)
        return loss

    def on_validation_epoch_end(self):
        # Compute and log F1 metric at the end of the validation epoch
        f1 = self.val_f1.compute()
        self.log("val_f1", f1, prog_bar=True)
        self.val_f1.reset()

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.learning_rate)
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=0, num_training_steps=self.total_steps
        )
        return [optimizer], [{'scheduler': scheduler, 'interval': 'step'}]

def main():
    # Parameters
    model_name = "yangheng/deberta-v3-base-absa-v1.1"  # Hugging Face model
    csv_file = "./Synthetic_Data.csv"                 # Path to your CSV file
    max_length = 128
    batch_size = 16
    num_labels = 2  # Binary classification: Positive and Negative
    learning_rate = 2e-5
    max_epochs = 3

    # Load the tokenizer from Hugging Face using the model name
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Load CSV file and map sentiment strings to numeric labels
    df = pd.read_csv(csv_file)
    # Map "Positive" to 1 and "Negative" to 0
    df['Sentiment'] = df['Sentiment'].map({'Positive': 1, 'Negative': 0})

    # Split the dataset into training and validation sets (e.g., 90/10 split)
    train_df, val_df = train_test_split(df, test_size=0.1, random_state=42)

    # Create datasets and dataloaders
    train_dataset = ABSADataset(train_df, tokenizer, max_length)
    val_dataset = ABSADataset(val_df, tokenizer, max_length)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, num_workers=0)

    # Calculate total training steps for the scheduler
    total_steps = len(train_loader) * max_epochs

    # Initialize the LightningModule for fine-tuning
    model_module = ABSAClassifier(model_name, num_labels, learning_rate, total_steps)

    # Set up callbacks and logger for monitoring training
    checkpoint_callback = ModelCheckpoint(monitor="val_f1", mode="max")
    early_stop_callback = EarlyStopping(monitor="val_f1", patience=3, mode="max")
    lr_monitor = LearningRateMonitor(logging_interval='step')
    logger = TensorBoardLogger("tb_logs", name="absa")

    trainer = pl.Trainer(
        max_epochs=max_epochs,
        callbacks=[checkpoint_callback, early_stop_callback, lr_monitor],
        logger=logger,
    )

    # Start training
    trainer.fit(model_module, train_loader, val_loader)

    # Save the fine-tuned model and tokenizer
    save_dir = "finetuned_absa_model"
    os.makedirs(save_dir, exist_ok=True)
    model_module.model.save_pretrained(save_dir)
    tokenizer.save_pretrained(save_dir)
    print(f"Fine-tuned model saved to {save_dir}")

if __name__ == "__main__":
    main()
