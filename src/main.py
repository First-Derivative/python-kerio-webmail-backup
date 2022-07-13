from ArchiveManager import ArchiveManager, _join
import time, re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# Login Error for erroneous credentials
class LoginAuthError(Exception):
  pass

# Mail Server Error for erroneous webmail path
class MailServerError(Exception):
  pass

# Auxiliary Functions
def get_mailbox_indexes(driver):
  '''
    Gets index value from the mailbox page. Written on website as '6101 - 6150 of 6207'
    This functions returns a dict (object) with keyvalue pairs { "min" : 6101, "max" : 6150,  "total" : 6207}.
    Or min, max, total
  '''
  index_src = driver.find_element(By.ID, "linkbutton-1111-btnInnerEl").get_attribute("innerText") 
  indexes = index_src.split(" ")
  _pass = False
  while(not _pass):
    try:
      int(indexes[0])
      int(indexes[2])
      int(indexes[4])
      _pass = True
    except ValueError:
      time.sleep(2)
      index_src = driver.find_element(By.ID, "linkbutton-1111-btnInnerEl").get_attribute("innerText") 
      indexes = index_src.split(" ")

  obj = { "min" : int(indexes[0]), "max" : int(indexes[2]),  "total" : int(indexes[4]) }
  return obj

# Stage Functions
def login(username, password, driver):
  driver.implicitly_wait(5)

  # Get selenium login elem
  email_input = driver.find_element(by=By.NAME, value="kerio_username")
  password_input = driver.find_element(by=By.NAME, value="kerio_password")
  login_button = driver.find_element(by=By.ID, value="login-button")
  
  #send login data to elem and login
  email_input.send_keys(username)
  password_input.send_keys(password)
  login_button.click()
  
  try:
    time.sleep(3)
    error_div = driver.find_element(by=By.XPATH, value='//*[@id="error-message-text"]/h2')
    if(not error_div == None):
      return LoginAuthError(username)
  except: 
    print("======================================")
    print("Authentication successful: ")
    print("======================================")
    return 

def preAllocate(username, base_dir, driver):
  indexes = get_mailbox_indexes(driver)

  # Configuring ArchiveManager 
  manager = ArchiveManager(username, indexes["total"], indexes["max"], base_dir)
  manager.full_check()
  return manager

def allocate(manager, driver):
  # Get batch of mailbox 
  batch = manager.getBatch()
  
  time.sleep(3)
  # Navigate driver to appropriate mailbox view
  nav_buttons = {
    "first" : driver.find_element(By.ID, "button-1109-btnEl"),
    "prev" : driver.find_element(By.ID, "button-1110-btnEl"),
    "next" : driver.find_element(By.ID, "button-1112-btnEl"),
    "last" :  driver.find_element(By.ID, "button-1113-btnEl"),
  }

  # Orient target via batch for navigation
  target = batch.sum()//batch.size
  cIndex = get_mailbox_indexes(driver)
  
  # Navigation Algorithm that finds the correct page
  while ( target < cIndex["min"] or target > cIndex["max"] ):
    prevIndex = cIndex
    delta = (target - cIndex["min"])//manager.page_window_size
    delta_floor = (cIndex["total"] //manager.page_window_size ) //2
    direction = "left" if delta < 0 else "right"

    # First Check: Evaluate if First/Last buttons need to be used for efficiency
    if(delta > delta_floor):
      if( direction == "left" ):
        nav_buttons["first"].click()
      else:
        nav_buttons["last"].click()

    # Second Check: Navigates pages based on direction
    else: 
      if( direction == "left" ):
        nav_buttons["prev"].click()
      else:
        nav_buttons["next"].click()
    
    while(prevIndex == cIndex):
      time.sleep(3)
      cIndex = get_mailbox_indexes(driver)

  return (batch, cIndex, manager)

def _save(obj, id, manager, driver):

  action = ActionChains(driver)
  # right click on selenium elem
  action.move_to_element(obj).perform()
  action.context_click(obj).perform()

  # Click 'View Source' and COMMAND+Click
  source_click = driver.find_element(By.ID, "menuitem-1253-itemEl")
  action = ActionChains(driver)
  action.move_to_element(source_click).perform()
  action.key_down(Keys.COMMAND).perform()
  action.click(source_click).perform()
  action.key_up(Keys.COMMAND).perform()

  # Switch Tabs driver -> Tab#2
    
  # Get current window handle
  p = driver.current_window_handle
  # Get first child window
  chwd = driver.window_handles
  for w in chwd:
    #switch focus to child window
    if(w!=p):
      driver.switch_to.window(w)
      break
  
  # Get elem, elem data data (mail), and save
  eml = driver.find_element(By.TAG_NAME, "pre")
  filename = '{}.eml'.format(id)
  path = manager.user_dir
  save_path = _join(path, filename)
  print("Saving {} in: {}".format(filename, save_path))
  with open(save_path, 'w') as f:
    f.write(eml.get_attribute("innerText"))

  # Close driver Tab#2
  driver.close() 

def save(batch, index, manager, driver):
  '''
    Explaining data structures and their contents:

    mailbox = contains the selenium elements found on display on the webpage (hence mailbox). Ordered [first] = largest mailbox id, [last] = smallest mailbox id
    mailbox_id = contains the list of ids that corresponds to the mailbox elements, generated in order of mailbox elements. So mailbox_id[0] = id of selenium element mailbox[0]
    batch = contains the batch of mails to download. Written in the batch no format (inferred from the webpage mail)
  '''
  main_driver_tab = driver.current_window_handle

  # Get mailbox selenium elemenets and ids as arrays. lens of both elements are the same
  mailbox = driver.find_elements(by=By.CLASS_NAME, value="simple-item-list-row")
  mailbox_id = [ (index["total"] - (i - 1)) for i in range( index["min"], (index["max"] + 1) ) ]
  _no_save = False

  for i in range( batch.size ):
    # convert batch_no into id form to compare with mailbox_id
    batch_no = manager.readBatchNo(batch[i])

    # if mail id from batch is found in mailbox_id then proceed to save mail element
    if(batch_no in mailbox_id):
      _no_save = False
      mailbox_pos = mailbox_id.index(batch_no)
      _save(mailbox[mailbox_pos], mailbox_id[mailbox_pos], manager, driver)

      #after saving remove item from batch, and mailQ
      mailQ_pos = manager.mailQ.search(mailbox_id[mailbox_pos])
      manager.mailQ.pop(mailQ_pos)
      driver.switch_to.window(main_driver_tab)
    else:
      _no_save = True
    
  return (manager, _no_save)

def postSave(manager, _no_save):
  # Check size of mailQ to see if there are remaining emails queued to be downloaded
  remaining = manager.full_check()
  if(remaining == 0):
    return (True, manager)
  else:
    if(_no_save):
      manager.batch_buffer_size += 1
    return (False, manager)

# Main Function
def main(username, password, mailserver, driver):
  t1 = time.time()
  try:

    # Get webmail login page via path
    path = mailserver 
    if (not 'https://' in path):
      path = 'https://' + path
    print("\n")
    print("======================================")
    print("Accessing webmail: {}".format(path))
    print("======================================")
    try:
      driver.get(path)
      WebDriverWait(driver, 10).until(EC.title_contains("Kerio Connect Client"))
    except:
      print("raising mailserver error")
      raise MailServerError(mailserver)
    
    # Main Sequence 
    print("======================================")
    print("Authneticating: {}".format(username))
    print("======================================")
    print("\n")

    exception = login(username, password, driver)
    if(type(exception) == LoginAuthError):
      raise LoginAuthError(username) 
    
    manager = preAllocate(username, "mail_archive", driver)
    _finished = False

    while(not _finished):
      (runtime_batch, runtime_index, manager) = allocate(manager, driver)
      (manager, _no_save) = save(runtime_batch, runtime_index, manager, driver)
      (_finished, post_manager) = postSave(manager, _no_save)
      manager = post_manager

    t2 = time.time()
    print("Time elapsed: {}".format(t2-t1))
    driver.quit()

  except Exception as e:
    t2 = time.time()
    print("Time elapsed: {}".format(t2-t1))
    
    #Catch raised exception from login()
    if(type(e) == LoginAuthError):
      print("Login Authentication error for user: {}".format(e))
    if(type(e) == MailServerError):
      print("The given mailserver: {} is not a valid path".format(e))
      driver.quit()
    else:
      print(e)
      driver.quit()

def __get_username():
  user_input = input("Please enter username: ")
  email_pattern = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
  if(not re.search(email_pattern,user_input)):
    print("\n***********************")
    print("Please enter a valid email")
    print("***********************\n")
    __get_username()
  return user_input

def __get_password():
  user_input = input("Please enter password: ")
  return user_input

def process_account():
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
  print("\n")
  print("======================================")
  print("...........Starting Program...........")
  print("======================================")
  print("\n")

  mailserver = input("Please input the kerio webmail url: ")
  print("\n")

  # Manage inputs from user for user credentials
  input_creds = []
  _done = False
  while ( not _done ):

    user = { 'username': '', 'password': ''}
    
    if( len(input_creds) == 0 ):
      user["username"] = __get_username()
      user["password"] = __get_password()
      input_creds.append(user)
    else:
    
      _answered = False
      while( not _answered ):
    
        answer = input("Would you like to process another kerio account?\n").lower()
        if( answer == 'yes'):
          _answered = True
          user["username"] = __get_username()
          user["password"] = __get_password()
          input_creds.append(user)
        elif( answer == 'no' ):
          _answered = True
          _done = True
        else:
          print("\n***********************")
          print("Please enter yes or no")
          print("***********************\n")

  for user in input_creds:
    try:
        main(user["username"], user["password"], mailserver, driver)
    except Exception:
      pass

if __name__ == "__main__":
  process_account()