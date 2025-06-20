from transformers import XLNetForSequenceClassification
import pytorch_lightning as pl
import torch
from sklearn.metrics import f1_score
from torch.optim.lr_scheduler import StepLR
import os


class TextClassificationModel(pl.LightningModule):

    def __init__(self, load_model_path=None):
        super().__init__()

        # Load the model 
        if load_model_path and os.path.exists(load_model_path):
            self.model = XLNetForSequenceClassification.from_pretrained(load_model_path)
            print("OLD MODEL:")

        else:
            self.model = XLNetForSequenceClassification.from_pretrained('xlnet-base-cased', num_labels=2)
            print("NEW MODEL:")

        #Array to store predictions and labels (For F1 score calculation)
        self.validation_predictions = []
        self.validation_labels = []



    def forward(self, input_ids, attention_mask, labels=None):
        return self.model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)


    #Define training step at each EPOTCH
    def training_step(self, batch, batch_idx):
        outputs = self(batch['input_ids'], batch['attention_mask'], batch['labels'])
        loss = outputs.loss

        #Logs training loss and accuracy at every epochs
        accuracy = (torch.argmax(outputs.logits, dim=1) == batch['labels']).float().mean()
        self.log('train_loss', loss, on_epoch=True, prog_bar=True, logger=True)
        self.log('train_accuracy', accuracy, on_epoch=True, prog_bar=True, logger=True)
        return loss

    #Log validation loss, accuracy, prediction at each STEP
    def validation_step(self, batch, batch_idx):
        outputs = self(batch['input_ids'], batch['attention_mask'], batch['labels'])
        val_loss = outputs.loss
        predictions = torch.argmax(outputs.logits, dim=1)
        accuracy = (predictions == batch['labels']).float().mean()
        
        
        #Sends to list for calculating F1
        self.validation_predictions.append(predictions.detach())
        self.validation_labels.append(batch['labels'].detach())
        self.log('val_loss', val_loss, on_epoch=True, prog_bar=True, logger=True)
        self.log('val_accuracy', accuracy, on_epoch=True, prog_bar=True, logger=True)
        return val_loss



    #Logs validation F1 calculation at every EPOCH
    def on_validation_epoch_end(self):
        all_predictions = torch.cat(self.validation_predictions).cpu().numpy() #Stores all tensors in a single tensor/cpu/numPy array
        all_labels = torch.cat(self.validation_labels).cpu().numpy()
        avg_f1 = f1_score(all_labels, all_predictions, average='weighted')
        self.log('val_f1', avg_f1, prog_bar=True, logger=True)

        #Empty out array after every epochs
        self.validation_predictions = []
        self.validation_labels = []


    #For configuration and finetuning
    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=3e-5)
        scheduler = {
            'scheduler': StepLR(optimizer, step_size=10, gamma=0.1),
            'interval': 'epoch',
            'frequency': 1
        }
        return [optimizer], [scheduler]
    
load_path = './SentimentFilter'
model = TextClassificationModel(load_model_path=load_path)

