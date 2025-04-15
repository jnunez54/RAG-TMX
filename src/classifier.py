import pandas as pd
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer
from sklearn.metrics import classification_report, confusion_matrix

import torch
import torch.nn as nn
import torch.optim as optim

# Modelo simple
class Autoencoder(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim, input_dim)
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))
    
def load_data():
    # Cargar el CSV
    df = pd.read_csv("solicitudes.csv") 

    # Filtrar datos
    positivos = df[df['competencia'] == 1]
    test_neg = df[df['competencia'] == 0]

    # Dividir positivos en train/test
    train_pos, test_pos = train_test_split(positivos, test_size=0.2, random_state=42)

    # Tomar cantidad igual de negativos en test_pos que en test_neg
    test_pos = test_pos.sample(n=len(test_neg), random_state=42)

    # Conjuntos finales
    train_df = train_pos  # solo positivos
    test_df = pd.concat([test_pos, test_neg]).sample(frac=1, random_state=42)  # equilibrado y mezclado
    print("Train size:", len(train_df))
    print("Test size:", len(test_df))

    return train_df, test_df

def create_model(train_df, sbert):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)
    
    X_train = sbert.encode(train_df['solicitud'].tolist(), convert_to_tensor=True)
    X_train = X_train.to(device)

    input_dim = X_train.shape[1]
    model = Autoencoder(input_dim=input_dim, hidden_dim=512).to(device)

    model.train()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    # Entrenar
    for epoch in range(200):
        model.train()
        optimizer.zero_grad()
        output = model(X_train)
        loss = criterion(output, X_train)
        loss.backward()
        optimizer.step()
        if epoch % 50 == 0:
            print(f"Epoch {epoch} - Loss: {loss.item():.4f}")
        
    return model, input_dim

def load_model(model_path, input_dim):
    """ Cargar el modelo guardado. """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Autoencoder(input_dim=input_dim, hidden_dim=512).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model

def get_confidence(errors):
    """ Calcula la confianza a partir de los errores de reconstrucción.
    """
    scaled_errors = (errors - errors.mean()) / errors.std()
    confidence = 1 - torch.sigmoid(scaled_errors)
    return confidence

def classify_by_confidence(confidence, min_conf=0.3, max_conf=0.7):
    """
    Clasifica según un rango de confianza:
    - Confianza < min_conf => Clase 0 (negativa / anomalía)
    - Confianza > max_conf => Clase 1 (positiva / normal)
    - Entre medio => zona gris (Estos ejemplos pasan al RAG)
    """
    result = torch.full_like(confidence, -1)  # -1 para zona gris
    result[confidence < min_conf] = 0
    result[confidence > max_conf] = 1
    return result

def classify(X_test, model, min_conf=0.3, max_conf=0.6):
    """ Clasifica ejemplos usando el modelo y devuelve la predicción.
    """
    model.eval()
    with torch.no_grad():
        recon = model(X_test)
        errors = torch.mean((X_test - recon) ** 2, dim=1)
        confidence = get_confidence(errors)

    # Clasificación
    y_pred = classify_by_confidence(confidence, min_conf=min_conf, max_conf=max_conf)
    return y_pred


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    sbert = SentenceTransformer('all-MiniLM-L12-v2').to(device)
    # Cargar datos
    train_df, test_df = load_data()
    
    # Crear modelo
    model, input_dim = create_model(train_df, sbert)
    
    # Guardar modelo
    torch.save(model.state_dict(), "autoencoder_model.pth")
    print("Modelo guardado como autoencoder_model.pth")
    print("Input dimension:", input_dim)
    
    # Cargar modelo
    model = load_model("autoencoder_model.pth", input_dim)
    
    # Evaluar modelo
    X_test = sbert.encode(test_df['solicitud'].tolist(), convert_to_tensor=True)
    X_test = X_test.to(device)
    y_test = test_df['competencia'].values
    
    
    predictions = classify(X_test, model) 
    # Calcular métricas
    gray_zone = (predictions == -1).sum().item()
    
    filtered_predictions = predictions[predictions != -1]
    filtered_y_test = y_test[predictions.cpu() != -1]
    
    # Classification report
    report = classification_report(filtered_y_test, filtered_predictions.cpu())
    print("Classification Report:")
    print(report)
    
    # Confusion matrix
    cm = confusion_matrix(filtered_y_test, filtered_predictions.cpu())
    print("Confusion Matrix:")
    print(cm)
    
    
    print(f"Gray zone size: {gray_zone}")
if __name__ == "__main__":
    main()