
import random

array=random.sample(xrange(1000),50)


class Counter:
  
  def __init__(self,initialValue):
    self.value=initialValue

  def add_One(self):
    self.value+=1


def main():

  contador=Counter(0)
  
  x=random.sample(xrange(1000000),100000)

  #print x

  sortedArray=quickSort_withCounter(x,contador)

  #print sortedArray

  print contador.value


def quickSort_withCounter(array, contador):
  
  less=[]
  greater=[]
  equal=[]

  arraySize=len(array)

  if (arraySize > 1):
    pivot=array[arraySize/2]

    for x in array:

      if (x > pivot):
        greater.append(x)
      elif (x == pivot):
        equal.append(x)
      else:
        less.append(x)

      contador.add_One()

    return quickSort_withCounter(less,contador) + equal + quickSort_withCounter(greater,contador)

  else:
    return array


  def quickSort(array):
  
  less=[]
  greater=[]
  equal=[]

  arraySize=len(array)

  if (arraySize > 1):
    pivot=array[arraySize/2]

    for x in array:

      if (x > pivot):
        greater.append(x)
      elif (x == pivot):
        equal.append(x)
      else:
        less.append(x)

    return quickSort(less) + equal + quickSort(greater)

  else:
    return array