import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, random_split
import matplotlib.pyplot as plt


class NCFModel(nn.Module):

    def __init__(self, numUsers, numItems, dimensions, categoryDimensions):
        super(NCFModel, self).__init__()

        # embeddings
        self.user_embedding = nn.Embedding(numUsers, dimensions)
        self.item_embedding = nn.Embedding(numItems, dimensions)

        # embedding (assuming categorical features are integers)
        self.category_embedding = nn.Linear(categoryDimensions, dimensions)

        # initialize fc1 with correct input size
        input_dim = dimensions * 3  # including category dimensions
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 1)  # output score
        


        #OVERFITTING - APPLY DROPOUT LAYER
        self.dropout = nn.Dropout(0.5)


    def forward(self, userID, itemID, features, categories):
        userEmbedding = self.user_embedding(userID)
        itemEmbedding = self.item_embedding(itemID)
        
        # category embedding
        categoryEmbedding = torch.relu(self.category_embedding(categories))

        # embeddings and features
        x = torch.cat([userEmbedding, itemEmbedding, features, categoryEmbedding], dim=1)

        # fully connected layers
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


def train_NCF(userData, categories, batch_size=32, validation_split=0.2):
    numUsers = userData['User_ID'].nunique()
    numItems = userData['Item_ID'].nunique()
    dimensions = 50
    categoryDimensions = categories.shape[1]  # category dimension 


    # NCF model with category dimensions
    model = NCFModel(numUsers, numItems, dimensions, categoryDimensions)
    optimizer = optim.Adam(model.parameters(), lr=1e-5)
    losses = nn.MSELoss()

    # data->tensors
    userID = torch.tensor(userData['User_ID'].values - 1, dtype=torch.long)
    itemID = torch.tensor(userData['Item_ID'].values - 1, dtype=torch.long)
    ratings = torch.tensor(userData['Rating'].values - 1, dtype=torch.float32)
    categories = categories.clone().detach()  # categories -> as tensor


    dataset = TensorDataset(userID, itemID, categories, ratings)
    
    train_size = int((1 - validation_split) * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    model.train()

    #loss visualization: 
    train_losses = []
    val_losses = []

    totalepoch = 35
    for epoch in range(totalepoch):
        # Training loop
        for batch_userID, batch_itemID, batch_categories, batch_ratings in train_loader:
            optimizer.zero_grad()  # Clears previous gradients
            
            # Create a zero tensor for features if you have removed LSTM features
            batch_features = torch.zeros(batch_userID.size(0), 0)  # Assuming no features
            
            prediction = model(batch_userID, batch_itemID, batch_features, batch_categories)
            loss = losses(prediction.squeeze(), batch_ratings)
            loss.backward()  # gradients
            optimizer.step()



        # validation loop
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch_userID, batch_itemID, batch_categories, batch_ratings in val_loader:
                prediction = model(batch_userID, batch_itemID, batch_features, batch_categories)
                val_loss += losses(prediction.squeeze(), batch_ratings).item()
        val_loss /= len(val_loader)

 
        print(f'NCF TRAINING: Epoch [{epoch + 1}/{totalepoch}], Training Loss: {loss.item()}, Validation Loss: {val_loss}')
        train_losses.append(loss.item())
        val_losses.append(val_loss)

        model.train()

    torch.save(model.state_dict(), 'NCFModel.pth')
    
    plotTraining(train_losses, val_losses)




def plotTraining(train_losses, val_losses):
    epochs = range(1,len(train_losses)+1)
    plt.plot(epochs, train_losses, 'b-', label='Training loss')
    plt.plot(epochs, val_losses, 'r-', label='Validation loss')
    plt.title('Training and validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()
