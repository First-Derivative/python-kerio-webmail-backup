from ArrayList import ArrayList
import os, re

# Auxiliary path joining function
def _join(a, b):
  return os.path.join(a,b)

class ArchiveManager():

  def __init__(self, username, index_total, page_window_size, base_dir="archives"):
    self.username = username
    self.base_dir = self.__resolve_base_dir(base_dir)
    self.user_dir = _join(self.base_dir, self.username.split("@")[0])
    self.page_window_size = page_window_size
    self.batch_buffer_size = 0
    self.index_user_dir = 0
    self.index_total = index_total
    self.mailQ = ArrayList([i for i in range(1, index_total+ 1)], index_total)
    self.full_check()

  # def getQ(self):
  #   self.mailQ.sort()
  #   q = self.mailQ.get()
  #   return q

  def __resolve_base_dir(self, dir):
    src_path = __file__
    filename = "/src/" + os.path.basename(__file__)
    full_path = os.path.join( os.getcwd(), src_path )
    _len = len(full_path) - len(filename)
    full_path = full_path[:_len]
    if(not dir[0] == "/"):
      dir = "/" + dir
    full_path = full_path + dir
    return full_path

  def getBatch(self):
    '''
      Creates a batch of real ID's which are sequential and ordered (descending).
      Evaluation: 
        b1 = converted no. found in mailbox, 
        b0 = origin no. found in dirs
        t = total

      Formula: b1 = t - (b0 - 1)
    '''
    self.mailQ.sort()
    top_range = self.page_window_size if self.mailQ.size >= self.page_window_size else self.mailQ.size
    
    top_range = top_range + ( top_range * self.batch_buffer_size )
    bottom_range = self.page_window_size * self.batch_buffer_size 

    if(top_range > self.mailQ.size):
      top_range = self.mailQ.size
      bottom_range = 0
      self.batch_buffer_size = 0

    temp_batch = self.mailQ.get()[bottom_range:top_range]

    for i in range(len(temp_batch)):
      temp_batch[i] = self.index_total - (temp_batch[i] - 1) 

    #Error checking
    if(temp_batch == None):
      raise Exception("Batch Error")

    batch = ArrayList(temp_batch, len(temp_batch))

    return batch

  def getBatchNo(self, data):
    '''
      Reverses the conversion for batch no. found in getBatch().
      Follows the formula:

      b0 = (t - b1) + 1
    '''
    return (self.index_total - data) + 1

  def readBatchNo(self, data):
    '''
      'Reads' the batch no. to convert back into .
      Follows the formula:

      b1 = t - (b1 -1)
    '''
    return self.index_total - (data - 1)

  def init_check(self):
    '''
      cd's into base_dir and check whether a dir with the name 'self.username' is found.
      if yes, then init_check is finished. if no, then create directory. 
    '''

    # check if base_dir dir exists; if not: create it.
    if(not os.path.isdir( self.base_dir ) ):
      os.mkdir( self.base_dir )

    # check if user-based folder in base_dir exisits; if not: create it.
    if(not os.path.isdir( self.user_dir ) ):
      os.mkdir( self.user_dir )
    
    return True

  def check_index(self):
    '''
      Gets a list of archived files in user_dir in order to sort out what has been indexed (files in user_dir) VS
      what needs to be indexed. If a file with ID x is present in the archive the check_index removes this ID from mailQ.
    '''
    mail_dir = os.listdir( self.user_dir )
    exp = r"([0-9]+.eml)" # Regular expression to make sure the iteration only considers digits.eml files
    
    for entry in mail_dir:
      if re.match(exp, entry):
        id = int(entry.split(".")[0])
        if( id in self.mailQ ):
          pos = self.mailQ.search(id)
          self.mailQ.pop(pos)
          self.index_user_dir += 1
        
  def full_check(self):
    self.init_check()
    self.check_index()
    return self.mailQ.size

  def __str__(self):
    output = ""
    output += "==========  Archive Manager ==========\n"
    output += "Username: {} \n".format(self.username)
    output += "Base Directory: {} \n".format(self.base_dir)
    output += "Index Total (Total no. of Emails): {} \n".format(self.index_total)
    output += "Index User Total (Total no. of Emails in user_dir): {} \n".format(self.index_user_dir)
    output += "==========  END  ==========\n"
    return output