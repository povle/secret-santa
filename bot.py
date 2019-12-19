import vk_api
import requests
import re
import time
import random
import json
import glob
import io
import os
import logging
from vk_api.bot_longpoll import VkBotMessageEvent

logger = logging.getLogger('ssanta.'+__name__)

class Bot:
    def __init__(self, token):
        self.token = token
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.pending_folder = './data/pending/'
        self.done_folder = './data/done/'
        
        self.pending = os.listdir(self.pending_folder)
        self.done = os.listdir(self.done_folder)

    def handle(self, data):
        event = VkBotMessageEvent(data)
        msg = event.object
        if msg.text:
            id = str(msg.from_id)
            if id in self.pending:
                to = random.choice([x for x in self.pending if x!=id])
                with open(self.done_folder + id, 'w') as f:
                    f.write(to)
                self.done.append(id)
                self.pending = [x for x in self.pending if x!=id]
                self.send(f'vk.com/id{to}', msg.from_id)
                logger.info(f'NEW: {id} to {to}')
            elif id in self.done:
                with open(self.done_folder + id, 'r') as f:
                    to = f.read()
                self.send(f'vk.com/id{to}', msg.from_id)
                logger.info(f'repeat: {id} to {to}')
            else:
                self.send('Вы не в списке', msg.from_id)

    def send(self, text, to, attachments=[], photos=[]):
        _attachments = []
        for doc in attachments:
            d = doc[doc['type']]
            s = f"{doc['type']}{d['owner_id']}_{d['id']}"
            if 'access_key' in d:
                s += '_' + d['access_key']
            _attachments.append(s)
        if photos:
            upload = vk_api.VkUpload(self.vk_session)
            for photo in upload.photo_messages(photos=photos):
                _attachments.append(f"photo{photo['owner_id']}_{photo['id']}")

        if not text and not _attachments:
            text = 'empty'
        text = str(text)

        rd_id = vk_api.utils.get_random_id()
        self.vk.messages.send(peer_id=to, random_id=rd_id, message=text[:4000],
                              attachment=','.join(_attachments))
        if len(text) > 4000:
            time.sleep(0.4)
            self.send(text[4000:], to)
