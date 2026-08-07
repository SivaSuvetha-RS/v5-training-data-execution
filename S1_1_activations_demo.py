import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_circles

# 1. Generate Synthetic Data (Two Concentric Rings)
X_np, y_np = make_circles(n_samples=1000, factor=0.5, noise=0.08, random_state=42)

# Convert to PyTorch tensors
X = torch.tensor(X_np, dtype=torch.float32)
y = torch.tensor(y_np, dtype=torch.float32).unsqueeze(1)

# 2. Define Model A: Linear Model (No hidden layers/non-linearities)
class LinearModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(2, 1)
        
    def forward(self, x):
        return torch.sigmoid(self.linear(x))

# 3. Define Model B: Non-Linear Model (One ReLU Hidden Layer)
class ReLUModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )
        
    def forward(self, x):
        return torch.sigmoid(self.net(x))

# 4. Helper Function to Train Models
def train_model(model, X, y, epochs=1000, lr=0.05):
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    for epoch in range(epochs):
        optimizer.zero_grad()
        predictions = model(X)
        loss = criterion(predictions, y)
        loss.backward()
        optimizer.step()
        
    acc = ((predictions > 0.5).float() == y).float().mean().item() * 100
    return acc

# Instantiate and Train
linear_model = LinearModel()
relu_model = ReLUModel()

linear_acc = train_model(linear_model, X, y)
relu_acc = train_model(relu_model, X, y)

print(f"Linear Model Accuracy: {linear_acc:.2f}%")
print(f"ReLU Model Accuracy:   {relu_acc:.2f}%")

# 5. Plotting Decision Boundaries ("The Money Shot")
def plot_decision_boundary(model, title, ax):
    # Create grid mesh
    x_min, x_max = X_np[:, 0].min() - 0.2, X_np[:, 0].max() + 0.2
    y_min, y_max = X_np[:, 1].min() - 0.2, X_np[:, 1].max() + 0.2
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200), np.linspace(y_min, y_max, 200))
    
    grid = torch.tensor(np.c_[xx.ravel(), yy.ravel()], dtype=torch.float32)
    
    with torch.no_grad():
        preds = model(grid).reshape(xx.shape).numpy()
        
    # Plot contours and data points
    ax.contourf(xx, yy, preds, levels=[0, 0.5, 1], alpha=0.3, colors=['#440154', '#fde725'])
    ax.contour(xx, yy, preds, levels=[0.5], colors='k', linewidths=2)
    ax.scatter(X_np[:, 0], X_np[:, 1], c=y_np, cmap='viridis', edgecolors='k', s=20)
    ax.set_title(title)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
plot_decision_boundary(linear_model, f"Linear Model\nAccuracy: {linear_acc:.2f}%", axes[0])
plot_decision_boundary(relu_model, f"1-ReLU Hidden Layer Model\nAccuracy: {relu_acc:.2f}%", axes[1])

plt.tight_layout()
plt.show()
