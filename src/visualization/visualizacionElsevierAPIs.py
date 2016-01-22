"""
Simple demo of a scatter plot.
"""
import numpy as np
import matplotlib.pyplot as plt


def mapperArea(radio):
	return np.pi * radio**2

# Affiliations of the universities with those we collaborate
y = ['60024830','60019424','100422342','60007801','60070231','60032442','114997202','60007966','60002306','60017774','101648832','60015150','113482957']
# Amount of publications in the period 2010-2014
x=[3107,1678,12,3770,559,5000,1,2414,5000,179,7,5000,1]
# Amount of publications written toghether
z= [1,1,1,27,1,2,1,19,1,2,1,1,1]

yUniques, y = np.unique(y, return_inverse=True)

colors = np.random.rand(len(x))

fig = plt.figure()

ax = fig.add_subplot(1, 1, 1)

ax.scatter(x, y, s=map(mapperArea,z), c=colors, alpha=0.5)

ax.set(yticks=range(len(yUniques)), yticklabels=yUniques)

plt.show()


# import pylab

# names = ['anne','barbara','cathy']
# counts = [3230,2002,5456]

# pylab.figure(1)
# x = range(3)
# pylab.xticks(x, names)
# pylab.plot(x,counts,"g")

# pylab.show()
#################################################################

# affiliationID|affilName|affilCity|affilCountry|pubCount|totalPubPeriod|totalPub
# |Benemerita Universidad Autonoma de Puebla|Puebla|Mexico|||6483
# |Texas Christian University|Fort Worth|United States|||5494
# |Laboratoire dEtude des Transferts en Hydrologie et Environnement|Grenoble|France|||29
# |University of Texas at El Paso|El Paso|United States|||9668
# |European Commission Joint Research Centre, Institute for Energy and Transport|Petten|Netherlands|||1386
# |Universidad Nacional Autonoma de Mexico|Mexico City|Mexico|||55978
# |CBRE Group, Inc.|No_Affil_City|United States|||1
# |Tecnologico de Monterrey|Monterrey|Mexico|||4838
# |University of Calgary|Calgary|Canada|||70377
# |Instituto Mexicano de Tecnologia del Agua|Jiutepec|Mexico|||590
# |CPS Energy|San Antonio|United States|||10
# |Imperial College London|London|United Kingdom|||128616
# |Southern Methodist University|Monterrey|Mexico|||1