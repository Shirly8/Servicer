import pytorch_lightning as pl
from transformers import AutoModelForSequenceClassification, get_linear_schedule_with_warmup
import torch
from sklearn.metrics import f1_score

class ABSAClassifier(pl.LightningModule):


    def __init__(self, model_name, num_labels, learning_rate=2e-5, total_steps=1000, ignore_mismatched_sizes=False):
        super().__init__()


        # Load the model
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


# define training step at each Epoch
    def training_step(self, batch, batch_idx):
        outputs = self(**batch)
        loss = outputs.loss
        self.log("train_loss", loss, on_step=True, on_epoch=True)
        return loss


#Log validation step, accuracy, prediction, and prediction labels
    def validation_step(self, batch, batch_idx):
        outputs = self(**batch)
        loss = outputs.loss
        logits = outputs.logits
        preds = torch.argmax(logits, dim=1)
        labels = batch['labels']
        self.log("val_loss", loss, prog_bar=True)
        self.validation_step_outputs.append({"loss": loss, "preds": preds, "labels": labels})
        return loss


#Log F1 score at each epoch
    def on_validation_epoch_end(self):
        if not self.validation_step_outputs:
            return
        all_preds = torch.cat([x["preds"] for x in self.validation_step_outputs])
        all_labels = torch.cat([x["labels"] for x in self.validation_step_outputs])
        f1 = f1_score(all_labels.cpu(), all_preds.cpu(), average='weighted')
        self.log("val_f1", f1, prog_bar=True)


        self.validation_step_outputs.clear()   #Empty out array


#For configuration/finetuning
    def configure_optimizers(self):

        optimizer = torch.optim.AdamW(self.parameters(), lr=self.learning_rate)
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=0, num_training_steps=self.total_steps
        )

        return [optimizer], [{'scheduler': scheduler, 'interval': 'step'}] 