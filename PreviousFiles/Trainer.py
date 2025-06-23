import time
import torch
from torch.utils.data import DataLoader
from transformers import XLNetTokenizer
import pytorch_lightning as pl
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint, LearningRateMonitor
from pytorch_lightning.loggers import TensorBoardLogger
from DataLoader import create_datasets
from Model import TextClassificationModel




def main(data_file):

    # Check if MPS (Apple Silicon) is available
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Using device: {device}")

    # Initialize tokenizer
    tokenizer_path = 'xlnet-base-cased'
    tokenizer = XLNetTokenizer.from_pretrained(tokenizer_path)

    # Load data - See DataLoader.py
    train_dataset, val_dataset = create_datasets(data_file, tokenizer)
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16)

    # Initialize model - See Model.py
    model = TextClassificationModel()

    # Callbacks - OPTIMIZATION
    early_stopping = EarlyStopping(monitor='val_loss', patience=2, mode='min')
    checkpoint_callback = ModelCheckpoint(
        dirpath='./checkpoints', filename='best-checkpoint', save_top_k=1, verbose=True, monitor='val_loss', mode='min'
    )
    lr_monitor = LearningRateMonitor(logging_interval='epoch')


    # Trainer
    trainer = pl.Trainer(
        max_epochs=3,
        accelerator="mps",
        devices=1,
        callbacks=[early_stopping, checkpoint_callback, lr_monitor],
        precision=16,

        #tensorboard --logdir=lightning_logs/
        logger=TensorBoardLogger("lightning_logs/")

    )

    # Measure training time
    start_time = time.time()
    trainer.fit(model, train_loader, val_loader)
    end_time = time.time()
    print(f"Training time: {end_time - start_time} seconds")

    # Save the model and tokenizer
    model.model.save_pretrained('./SentimentFilter')
    tokenizer.save_pretrained('./SentimentFilter')


if __name__ == "__main__":
    main('./Data/test(full).csv')
