# Python Kerio Webmail Backup

## Purpose of Software

Emails stored/accessed/and operated by the software Kerio MailServer don't provide the user with a web feature enabling a local backup download. Cutting off your ability to create local data backup on external harddrives for archiving purposes

---

## Use of Software

The primary purpose of this software is to provide users with access to their kerio webmail adccounts to index, catalogue, and archive their emails stored on the kerio webmail servers

## Software Structure

Directory structure:

```
python-kerio-webmail-backup
│   README.md
│   config.ini
└───src
│   │dmain.py
│   │   ArchiveManager.py
│   │   ArrayList.py
│   
└───mail_archive
    └───user1
    |    │    1.eml
    |    |    2.eml
    |    |    3.eml
    |    |    ...

    └───user2
    |    |    55.eml
    |    |    56.ml
    |    |    ...
```

* You execute **src/main.py**
* Script indexes mailbox and saves files in **/user1/** folder (```user1 = username```)
* Saved files are in .eml format

---

## Software Requirements

The software executes a python **main.py** file which is the program archiving, and collecting your mail. This means you need to be running this software on a operating system with ***Python3.9*** installed

should work with Python 3.4

---

--

## Installation of Software

You can clone this repo and install the dependencies in **requirements_.txt**.That is all that is required for installation.

Step-by-step:

1. Clone this repo:

    ```bash
    git clone https://github.com/First-Derivative/python-kerio-webmail-backup.git
    ```

2. Activate environment **\[Optional\]**
    * Using Conda/MiniConda:

      ```bash
      conda activate env
      ```

    * Using Python venv

      ```bash
      python3 -m venv env
      ```

3. Install requirements

    ```bash
    pip install -r requirements.txt
    ```

4. Initialize ```config.ini``` file **\[Optional\]**
    1. First we create the config file

    ```bash
    touch config.ini
    ```

    2. Then we populate (edit) the appropriate headers and fields for the file

        ```bash
        > [MailserverData]
        > mailserver = https://yourmailserver.com
        >
        > [UserData]
        > usernames = username1, username2, username3, ...
        > passwords = password1, password2, password3, ...
        ```

    for more explanation of config syntax please refer to [config heading](https://github.com/First-Derivative/python-kerio-webmail-backup#config-file-setup)

5. Execute Python script

    ```bash
    python3 src/main.py
    ```

---

## Config File Setup

This software includes a provision for interacting with the script via a config file which means you only have to configure the usernames, passwords, and mailservers once and never again. This is down via a ```config.ini``` file.

This ```config.ini``` should be located in the project directory (not in src). It should follow this structure, populating the variables as appropriate:

>```config.ini```
>```bash
>Line 1: [Mailserver Data]
>Line 2: mailserver = data
>Line 3: 
>Line 4: [UserData]
>Line 5: usernames = data
>Line 6: passwords = data
>```