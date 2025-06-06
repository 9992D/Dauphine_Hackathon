import matplotlib.pyplot as plt

labels = ['Exposés à Retargeting', 'Non exposés', 'Simulé sans Retargeting']
values = [0.2604, 0.1618, 0.2445]

plt.figure(figsize=(8, 5))
bars = plt.bar(labels, values, color=['#6EC4FF', '#FF9999', '#FFD966'])
plt.ylabel("Taux de conversion")
plt.title("Impact de Prog_Retargeting sur la conversion")

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.005, f"{height:.2%}", ha='center')

plt.ylim(0, 0.3)
plt.tight_layout()
plt.show()