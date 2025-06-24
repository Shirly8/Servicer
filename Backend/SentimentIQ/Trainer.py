import os
import pandas as pd
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint, LearningRateMonitor
from transformers import AutoTokenizer

from DataLoader import ABSADataset
from Model import ABSAClassifier

def main():


    input_model = os.path.join(os.path.dirname(__file__), '5star-absa-v2')
    output_model = "5star-absa-v4"
    csv_file = os.path.join(os.path.dirname(__file__), 'AllSyntheticReviews.csv')



    # Hyperparameters for training
    max_length = 128
    batch_size = 15
    num_labels = 5
    learning_rate = 2e-5
    max_epochs = 3


# Clean dataframe as columns: sentence, aspect, label
    df = pd.read_csv(csv_file, usecols=[0, 1, 2])
    df.columns = ["sentence", "aspect", "label"]
    df['label'] = pd.to_numeric(df['label'], errors='coerce')  #Label -> numeric
    df.dropna(subset=['sentence', 'aspect', 'label'], inplace=True)
    df['label'] = df['label'].astype(int) - 1   #Labels (1-5) represents (0-4) on classifications
    df['sentence'] = df['sentence'].astype(str)
    df['aspect'] = df['aspect'].astype(str)


    #Load model (90% train, 10% val)
    train_df, val_df = train_test_split(df, test_size=0.1, random_state=42)
    train_dataset = ABSADataset(train_df, input_model, max_length)
    val_dataset = ABSADataset(val_df, input_model, max_length)

    #Set num workers
    num_workers = 4 if os.name == 'posix' else 0



    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, persistent_workers=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, num_workers=num_workers, persistent_workers=True)


    #for learning rate scheduler
    total_steps = len(train_loader) * max_epochs


    model = ABSAClassifier(
        input_model,
        num_labels,
        learning_rate,
        total_steps,
        ignore_mismatched_sizes=True
    )



   #LOGGING
    checkpoint_callback = ModelCheckpoint(monitor="val_f1", mode="max")
    early_stop_callback = EarlyStopping(monitor="val_f1", patience=3, mode="max")
    lr_monitor = LearningRateMonitor(logging_interval='step')


   #TRAIN MODEL
    trainer = pl.Trainer(
        max_epochs=max_epochs,
        callbacks=[checkpoint_callback, early_stop_callback, lr_monitor],
        accelerator='auto',
        devices=1,
        log_every_n_steps=10
    )

    trainer.fit(model, train_loader, val_loader)



    #Save Model
    save_dir = os.path.join(os.path.dirname(__file__), output_model)
    os.makedirs(save_dir, exist_ok=True)
    model.model.save_pretrained(save_dir)
    tokenizer = AutoTokenizer.from_pretrained(input_model)
    tokenizer.save_pretrained(save_dir)

if __name__ == "__main__":
    main() 