class Mole:
    def __init__(self, mole_args):
        import json
        self.config = mole_args[0]
        with open(self.config, 'r') as config_data:
            self.data = json.load(config_data)       

    def cycle_through_history(self, mole_obj):
        import requests
        from datetime import datetime

        with open(f"./{mole_obj["FOLDER"]}/enumeration.log","a") as a:
            a.write(f"Began enumerating chat IDs between {mole_obj["MIN"]} - {mole_obj["MAX"]} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        if mole_obj["BLUE_CHANNEL"] != "":
            using = {
            "forwardMessage": f"forwardMessage?chat_id={mole_obj["BLUE_CHANNEL"]}&from_chat_id={mole_obj["RED_CHANNEL"]}&disable_notification=True&message_id="
        }
        else:
            using = {
            "forwardMessage": f"forwardMessage?chat_id={mole_obj["RED_CHANNEL"]}&from_chat_id={mole_obj["RED_CHANNEL"]}&disable_notification=True&message_id=",
        }
        cntr = 0
        for x in range(int(mole_obj["MIN"]),int(mole_obj["MAX"])):
            m_id = 0
            for key in using.keys():
                endpoint = key
                response = requests.get(mole_obj["URL"]+using[endpoint]+str(x))
                formatted = response.json()
                print(formatted)
                try:
                    m_id = formatted["result"]["message_id"]
                except:
                    continue
                if '{"ok":true' in response.text:
                    cntr += 1  
                    with open(f"./{mole_obj["FOLDER"]}/{endpoint}.json","a") as a:
                        a.write(f"{response.text}\n")

            if m_id != 0 and mole_obj["BLUE_CHANNEL"] == "":
                print("Removing duplicate forwarded message.")
                response = requests.get(mole_obj["URL"]+f"deleteMessage?chat_id={mole_obj["RED_CHANNEL"]}&message_id={m_id}")
                if '{"ok":true,' in response.text:
                    with open(f"./{mole_obj["FOLDER"]}/deletedMessage.json","a") as a:
                        a.write(f"{response.text}\n")
                    print("Removed duplicate forwarded message.") 

        if mole_obj["BLUE_CHANNEL"] != "":
            exit_channel = {
                "leaveChat":f"leaveChat?chat_id={mole_obj["BLUE_CHANNEL"]}",
                "close":f"close",
                "logOut":f"logOut"
            }
            self.query_endpoint(exit_channel, mole_obj["URL"], mole_obj["FOLDER"])
        print(f"COMPLETED DATA ENUMERATION. RETRIEVED {cntr} MESSAGES.")
    

    def cycle_through_endpoints(self, mole_obj):
        folder, exists = self.create_folder(mole_obj["URL"], mole_obj["RED_CHANNEL"])

        if not exists:
            self.query_endpoint(mole_obj["GEN_ENDPOINTS"], mole_obj["URL"], folder)
            self.query_endpoint(mole_obj["CHANNEL_ENDPOINTS"], mole_obj["URL"], folder) 
        
        mole_obj["FOLDER"] = folder
        userchatid = input(f"ENTER YOUR GROUP ID FOR BOT [{folder}]: ")
        mole_obj["BLUE_CHANNEL"] = userchatid
        return mole_obj


    def query_endpoint(self, endpoint, URL, folder):
        import requests
        for key in endpoint.keys():
            response = requests.get(URL+endpoint[key])
            with open(f"./{folder}/{key}.json","a") as a:
                a.write(f"{response.text}\n")
    
    
    def create_folder(self, URL, RED_CHANNEL_ID):
        import requests
        from datetime import datetime
        import os
        response = requests.get(f"{URL}getMe")
        formatted = response.json()
        bot_username = formatted["result"]["username"]
        response = requests.get(f"{URL}getChat?chat_id={RED_CHANNEL_ID}")
        formatted = response.json()
        try:
            chat_username = formatted["result"]["username"]
        except:
            try:
                chat_username = formatted["result"]["title"]
            except:
                try:
                    chat_username = f"{formatted["result"]["first_name"]}_{formatted["result"]["last_name"]}"
                except:
                    try:
                        chat_username = f"{formatted["result"]["first_name"]}"
                    except:
                        print("DOES NOT EXIST")
        folder = f"{bot_username}.{chat_username}.{datetime.today().strftime('%m-%d-%y')}"
        exists = False
        try:
            os.mkdir(f"{folder}")
        except:
            print("Folder already exists")
            exists = True
        return [folder,exists]

    def enumerate(self):
        import threading

        MIN = input("ENTER MINIMUM CHAT ID TO SCAN FOR WITH ALL BOTS: ")
        MAX = input("ENTER MAXIMUM CHAT ID TO SCAN FOR WITH ALL BOTS: ")
        to_cycle = []

        for key in self.data.keys():
            mole_obj = {}

            TOKEN = self.data[key]['token']
            RED_CHANNEL_ID = self.data[key]['chat_id']

            URL = f"https://api.telegram.org/{TOKEN}/"

            CHANNEL_ENDPOINTS = {
                "getChatAdministrators":f"getChatAdministrators?chat_id={RED_CHANNEL_ID}",
                "getChat":f"getChat?chat_id={RED_CHANNEL_ID}",
                "getChatMembersCount":f"getChatMembersCount?chat_id={RED_CHANNEL_ID}",
                "createChatInviteLink":f"createChatInviteLink?chat_id={RED_CHANNEL_ID}",
            }

            GEN_ENDPOINTS = {
                "getUpdates":"getUpdates",
                "getWebhookInfo":"getWebhookInfo",
                "getMe":"getMe",
                "getMyCommands":"getMyCommands",
                "getMyName":"getMyName",
                "getMyDescription":"getMyDescription",
                "getAvailableGifts":"getAvailableGifts",
                "getWebhookInfo":"getWebhookInfo",
            }
            
            mole_obj["RED_CHANNEL"] = RED_CHANNEL_ID
            mole_obj["URL"] = URL
            mole_obj["GEN_ENDPOINTS"] = GEN_ENDPOINTS
            mole_obj["CHANNEL_ENDPOINTS"] = CHANNEL_ENDPOINTS
            mole_obj["MIN"] = MIN
            mole_obj["MAX"] = MAX
            mole_obj["TOKEN"] = TOKEN
            to_cycle.append(mole_obj)
        
        newcycle = []
        for el in to_cycle:
            new_mole_obj = self.cycle_through_endpoints(el)
            newcycle.append(new_mole_obj)
 
        thread_list = []
        inc = 0
        for el in newcycle:
            t = threading.Thread(target=self.cycle_through_history, args=(el, ))
            thread_list.append(t)
            inc+=1
        
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()