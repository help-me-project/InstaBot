#!/usr/bin/python3
# -*- coding: utf-8 -*-
from InstagramAPI import InstagramAPI
import sys

# Инициализируем массив логин/пароль
instagramm_accounts=[['helpme24comnsk','xxxXXXxxx'],['probendutor','yyyYYYyyy']]
# Инициализируем массив тегов
instagramm_tags=['sinuniformes','rap','jaz']
# Сообщение которое будем отправлять
instagramm_message='Привет! У меня нет друзей и хотел предложить подружиться.'
# Максимум сообщений которые можно отправить от имени одного пользователя
# Согласно доке можно отравить 15-и пользователям
max_messages=15
# Минимум подписчиков для отправки сообщения
min_followers=500

def debug_message(msg):
    global enable_debug
    if enable_debug:
        print (msg+'\n')

# Функция отправки сообщений (анализируется количество уже отправленных сообщений и ограничения по количеству фоловеров)
# инициализируем глобальные переменные
_user_id=0
_instapi=None
_message_sended=0
# Собственно функция
def send_message_for_user(user_name_id):
    global _instapi
    global _user_id
    global _message_sended
    # Проверяем статус подключения к инстаграмм
    try:
        u_agent=_instapi.USER_AGENT
        connected=True
    except:
        connected = False
    if connected:
        debug_message('Bot connected to Instagramm [Skip connection phase] \n')
    else:
        debug_message('Bot not connected to Instagramm [Try to connect] \n')
        while True:
            login_info = instagramm_accounts[_user_id]
            _instapi = InstagramAPI(login_info[0], login_info[1], debug=False)
            if _instapi.login():
                debug_message('Login sucess for: ' + login_info[0] + '\n')
                break
            else:
                debug_message('Login failed for: ' + login_info[0] + '\n')
                debug_message('Switch user ID\n')
                _user_id =_user_id+1
                # Если идентификатор превышает количество существующих пользователей, то сбрасываем счетчик
                if _user_id>len(instagramm_accounts)-1:
                    _user_id=0
    # Запрашиваем информацию о пользователе
    # и определяем будем ли отправлять ему сообщение
    if _instapi.getUsernameInfo(user_name_id):
        json_data=_instapi.LastJson
        if json_data['status']=='ok':
            user_info = json_data['user']
            debug_message('Get info for user: ' + user_info['username'] + '\n')
            debug_message('Follower count: ' + str(user_info['follower_count']) + '\n')
            if user_info['follower_count'] > min_followers:
                debug_message('Send message for: '+str(user_name_id)+'\n')
                # После отправки добавляем строку в файл со списком исключений
                _f=open('exclude_list.txt', 'a')
                _f.write(str(user_name_id)+'\n')
                _f.close()
                # Выводим сообщение в консоль кому отправлено и от кого
                print ('> Sended message from: '+instagramm_accounts[_user_id][0]+' to '+user_info['username'])
                # Выход после первой отправки на период отладки
                sys.exit()
            else:
                debug_message('Skip user ' + user_info['username'] + ' too few folowers\n')
    _message_sended=_message_sended+1
    # Если привышен лимит отправки с одного акакаунта, то переключаем аккаунт и сбрасываем счетчик
    if _message_sended>max_messages:
        debug_message('Messages limit from a single account exceeded. Reset counter\n')
        _user_id = _user_id + 1
        _message_sended = 0
        _instapi = None
        # Если идентификатор превышает количество существующих пользователей, то сбрасываем счетчик
        if _user_id > len(instagramm_accounts) - 1:
            _user_id = 0

# Включить режим откладки на период сбора аккаунтов
enable_debug=False

debug_message('Application started')
# Первым этапом производится сборка всех пользователей связанных с метками,
# удаление дубликатов и чистка уже обработанных согласно файла исключений
#
# Выборка пользователей по меткам проводится от имени одного пользователя
# если подключиться не удалось, то запрашиваем от имени следующего пользователя
#
debug_message('Collect users by tags')
user_list = []
for account in instagramm_accounts:
    login=account[0]
    password=account[1]
    debug_message('Working with account: '+login)
    InstAPI = InstagramAPI(login, password,debug=False)
    if InstAPI.login():
        debug_message('Login '+login+' Sucess!')
        for tag in instagramm_tags:
            InstAPI.tagFeed(tag)
            results=InstAPI.LastJson
            if results['status']=='ok':
                debug_message('Tag ' + tag + ' scaned Sucess!')
                for item_pack in results['items']:
                    user_info=item_pack['user']
                    debug_message('Located user: '+user_info['username']+' ('+user_info['full_name']+')\n')
                    user_list.append(user_info['pk'])
            else:
                debug_message('Tag ' + tag + ' scan Fail!')
        InstAPI.logout()
        debug_message('Collecting users related to the tag is completed')
        break
    else:
        debug_message('Login ' + login + ' Fail!')

# Удаляем дубликаты
_user_list=list(set(user_list))

# Загружаем файл со списком исключений и удаляем из списка пользователей
# тех кому уже отправляли сообщение
_f = open('exclude_list.txt', 'r')
exclude_list =[]
for item in _f.read().split('\n'):
    try:
        exclude_list.append(int(item))
    except:
        pass
_f.close()

user_list = []
for user in _user_list:
    if user not in exclude_list:
        user_list.append(user)

# Включаем режим отладки на период отправки сообщений
enable_debug=False
# Запрашиваем количество подписчиков у пользователя и если нас устраивает, то отправляем сообщение
# Весь функционал зашит в функцию send_message_for_user
debug_message('Located '+str(len(user_list))+' users')
for user_id in range (0,len(user_list)):
    send_message_for_user(user_list[user_id])