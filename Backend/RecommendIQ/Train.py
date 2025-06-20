import torch
import numpy as np
from DataLoader import loadData, convertCategories, convertDescriptions
from LSTM_Model import LSTMModel, train_LSTM
from NCF_Model import train_NCF
from LSTM_Feature import extract_lstm_features

def main():
    menuData, userData = loadData()

    description_tensor = convertDescriptions(menuData)

    inputDim = description_tensor.shape[1]
    
    # Train LSTM Model
    lstm_model, description_features = train_LSTM(description_tensor, inputDim=inputDim)  # Unpack both returned values
    torch.save(lstm_model.state_dict(), '/Users/shirleyhuang/Documents/Apps/RecommendIQ/LSTM_Model.pth')

    # Extract LSTM features for the menu data
    lstm_model.eval()  # Set the model to evaluation mode
    description_features = extract_lstm_features(description_tensor, inputDim)  # Extract features

    # Map ItemIDs to LSTM features
    itemIdToFeature = dict(zip(menuData['Item_ID'], description_features.detach().numpy()))
    userData['LSTM_Features'] = userData['Item_ID'].map(itemIdToFeature)
    LSTM_features = torch.tensor(np.array(userData['LSTM_Features'].tolist()), dtype=torch.float32)

    # Map Item_IDs to Category features for each user interaction
    categoriesID = convertCategories(menuData)
    userData['Category_Features'] = userData['Item_ID'].map(categoriesID)
    category_tensor = torch.tensor(np.array(userData['Category_Features'].tolist()), dtype=torch.float32)

    # Train NCF Model
    train_NCF(userData, category_tensor)

if __name__ == '__main__':
    main()
