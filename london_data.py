from matplotlib import pyplot as plt
import pandas as pd

data = pd.read_csv("data.csv")
data = data.loc[(data['Link_length_km']==4.6) & (data['Year']==2014)]

# group by hour
data = data.groupby('hour').mean()

figure, ax = plt.subplots()
ax.scatter(data.index,data['Cars_and_taxis'] / 2000)
ax.set_xlabel('Hora del día')
ax.set_ylabel('Promedio de Autos / 2000')

plt.show()
