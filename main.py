from pkg.manga_pkg import *
import time
import datetime
from random import randint
import threading
import json

with  open('./pkg/manga_state.json','r',encoding="utf-8") as manga_state_file:
    manga_state = json.load( manga_state_file )
    
path_log_book = './data/log_book/manga_output.md'
def output_to_log_book(typee='mna',text='none'):
    #typee = 'mna'/'usr'
    timing = datetime.datetime.now()  
    timing_format = timing.strftime("%Y_%m_%d@%H_%M_%S@{}@".format(typee))
    with open( path_log_book,'a+',encoding='utf-8') as output:
        output.write( timing_format)
        output.write( text + '\n' )
    pass

def threading_manga_state():
    while(1):
        global manga_state
        with  open('./pkg/manga_state.json','r',encoding="utf-8") as manga_state_file:
            manga_state = json.load( manga_state_file )
        output_to_log_book('ini','suc@start_update')
        for user_id in manga_state.keys():
            output_to_log_book('ini','beg@{}'.format(user_id))
            update_list =  []
            messages = []
            for web in manga_state[user_id]['manga'].keys():
                #
                time.sleep(randint(3, 10))
                current_value = manga_state[user_id]['manga'][web]
                try:
                    manga_class= check_manga_state(web,current_value)
                except:
                    print('error occur in opening')
                    output_to_log_book('mnm','err'+'@{}'.format(web))
                output_to_log_book('mnm',manga_class._state+'@{}'.format(web))
                if( manga_class._state =='updated'):
                    update_list.append( manga_class )
                else:
                    pass
            print(len(update_list))
            if(len(update_list) != 0):
                #如果有更新
                print('There are updates')
                print(update_list)
                flex_message = flex2( update_list )
                for i in flex_message:
                    messages.append( i )
                try:                  
                    #嘗試送訊息
                    print( md_state[user_id]['reply_token'])
                    line_bot_api.reply_message(md_state[user_id]['reply_token'],messages)
                    output_to_log_book('usr','suc@'+user_id)

                except:
                    #沒成功退出
                    print('failed '+md_state[user_id]['reply_token'])
                    output_to_log_book('usr','non@'+user_id)
                    try:
                        line_bot_api.reply_message(md_state['Ud3c29bface5061c1ef292f819dc78bdc']['reply_token'],messages)
                    except:
                        pass
                    continue
                for updates in update_list:
                    print( updates._web + '::'+updates._words[1])
                    manga_state[user_id]['manga'][updates._web] = updates._words[1]
                    print( manga_state[user_id]['manga'][updates._web] )
                save_manga_state()
            else:
                continue
        time.sleep( 60*randint(20,40))

if __name__ == "__main__":
    update_manga_threading = threading.Thread(target=threading_manga_state)
    update_manga_threading.start()