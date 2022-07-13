class ArrayListException():
  pass

class ArrayList():
  
  def __init__(self, init_arr=None, init_size=50):
    self.arr = None
    self.size = 0
    self.memory = init_size

    # Evaluate self.arr
    if(init_arr == None):
      self.arr = [ 0 for i in range(init_size) ] 
    else:
      init_arr_len = len(init_arr)
      self.arr = self.copy(init_arr, [ 0 for i in range(self.memory) ])
      self.size = init_arr_len

    # Edge Case: erroneous init_size
    if( init_size < self.size ):
      self.memory = self.size

  def copy(self, ref, target, skip=-1):
    '''
    Copies reference array values into target array.
    Does not return a copy array of reference. 
    '''
    
    ref_len = len(ref)
    target_len = len(target)

    try:
      if(ref_len > target_len):
        raise ArrayListException("Reference array len is larger than target array len. Lens must be identical or target must be larger")
      
      # i = ref index, j = target index
      i = 0; j = 0;
      while( i < ref_len and j < target_len ):
        if( ( skip != -1 ) and ( i >= skip ) ):
          if( i >= ref_len-1 ):
            break
          target[j] = ref[i+1]
          i += 1
          j += 1
          continue

        target[j] = ref[i]
        i += 1
        j += 1
      
      return target

    except Exception as e:
      print("Exception: {e} ".format(e))
    
  def sizeUp(self):
    # increase array memory by 3/4 
    new_memory = int(1.75 * self.size) + 50
    new = self.copy(self.arr, [ 0 for i in range( new_memory ) ])
     
    # set object properties arr and memory
    self.arr = new 
    self.memory = new_memory

  def get(self):
    return self.arr[:self.size]

  def append(self, data):
    if(self.size == self.memory):
      self.sizeUp()

    self.arr[self.size] = data
    self.size += 1
    
  def pop(self, index=-1):
    '''
      Removes and returns value at pos index if index value specified. 
      Otherwise removes and returns value at the end of self.arr
    '''
    #edge case: erroneous index value
    if(index > self.size):
      raise ArrayListException("Index out of Range: Cannot pop at pos {} higher than size {}".format(index, self.size))

    if(not index == -1):
      value = self.arr[index]
      self.arr = self.copy(self.arr, self.arr, skip=index)
      self.size -= 1
      return value

    value = self.arr[self.size]
    self.arr[self.size] = 0
    self.size -= 1
    return value

  def search(self, data):
    '''
      Binary Search algorithm that returns the index pos of data (value) in self.arr.
      -1 pos return means that the data is not in self.arr
    '''
    self.sort() #search only works on sorted list
    min = 0
    max = self.size - 1

    while(min <= max):
      mid = (min + max ) // 2
      if( data == self.arr[mid] ):
        return mid
      
      if( data < self.arr[mid] ):
        max = mid - 1
      else:
        min = mid + 1

    return -1

  def sort(self):
    '''
    Executes merge sort algorithm in place on object property arr.
    Complexity sits at O(n) not O(n log(n)); limited by ArrayList datastructure which has to search through n items
    '''
    new = self.copy(self.arr, [0 for i in range(self.memory)])
    self.mergeSort(new)

    self.arr = self.copy(new, self.arr)

  def mergeSort(self, arr):
    # splitting arrays into atomic parts
    max = len(arr)
    mid = max//2
    
    if(max <= 1):
      return arr   
    
    left = arr[0:mid]
    right = arr[mid:max]
    self.mergeSort(left)
    self.mergeSort(right)
    self.merge(left, right, arr)

  def merge(self, left, right, arr):

    # i = arr index, j = left index, k = right index
    i = 0; j = 0; k = 0;
    left_max = len(left); right_max = len(right)
    
    while j < left_max and k < right_max:
      if( left[j] < right[k] ):
        arr[i] = left[j]
        j += 1
      else:
        arr[i] = right[k]
        k += 1
      i += 1

    while j < left_max:
      arr[i] = left[j]
      j += 1; i += 1;

    while k < right_max:
      arr[i] = right[k]
      k += 1; i += 1;

  def sum(self):
    total = 0
    for i in range(self.size):
      total += self.arr[i]
    return total

  def print_to(self, pos):
    output = "["
    if(pos >= self.size):
      raise IndexError
    
    for i in range(pos):
      output += str(self.arr[i]) + ", "
    
    output += "]"
    return output
    
  def __str__(self):
    output = "["
    for i in range(self.size):
      if( i == self.size -1 ):
        output += "{d}".format(d = self.arr[i])
        continue
      output += "{d}, ".format(d = self.arr[i])
    output += "]"
    return output
  
  def __contains__(self, data):
    ''' 
      dunder method that overwrites use of 'in' keyword.
      Returns boolean based on whether data in self.arr
    '''
    search_result = self.search(data)
    if(not search_result == -1):
      return True
    return False

  def __getitem__(self, key):
    if(key >= self.size):
      raise IndexError
    return self.arr[key]
