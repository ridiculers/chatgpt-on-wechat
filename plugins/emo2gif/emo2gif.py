# encoding:utf-8

import json
import os

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *
from channel.wechat.wechat_message import WechatMessage
import pdb
import io

@plugins.register(
        name='emo2gif',
        desire_priority=0,
        desc='将微信的表情转为gif，然后回复给用户。',
        version='1.0',
        author='ridiculers',
        )
class Emo2gif(Plugin):
    def __init__(self):
        super().__init__()
        self.curdir = os.path.dirname(__file__)
        self.e2g_dic = {"on":True, "off":False}
        #self.e2g_switch = False
        self.e2g_switch = False
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context


    def on_handle_context(self, e_context: EventContext):
        self.download_fn = e_context.econtext['context'].kwargs['msg'].Text
        # 1.只要是文字，不管是false还是true都要处理
        # 2.如果是true，需要是图像才要处理
        # 3. 如果是false,非文字，则不需要处理
        context_type = e_context.econtext["context"].type
        if self.e2g_switch == False and context_type != ContextType.TEXT:
            e_context.action = EventAction.BREAK_PASS
            return

        content = e_context["context"].content.split(' ')
        logger.info(content)
        logger.debug("[Emo2gif] on_handle_context. content: %s" % content)
        if context_type == ContextType.TEXT:
            #进入流程
            if content[0] == "e2g":
                reply = Reply()
                if len(content) != 2:
                    reply.type = ReplyType.INFO
                    reply.content = f"指令为空，请输入\'e2g on\'或\'e2g off\'来打开或关闭emo2gif。\n"
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS 
                    return
                if content[1] not in ["on", "off"]:
                    reply.type = ReplyType.INFO
                    reply.content = f"指令错误，请输入\'e2g on\'或\'e2g off\'来打开或关闭emo2gif。\n"
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS 
                    return
                self.e2g_switch = self.e2g_dic[content[1]]
                logger.info(self.e2g_switch)
                reply.type = ReplyType.INFO
                reply.content = "已成功 {} emo2gif。".format(content[1])
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS 
            return
        #图片处理流程
        if context_type == ContextType.IMAGE:
            self.download_fn = e_context.econtext['context'].kwargs['msg'].Text
            logger.info(self.curdir)
            file_path = self.curdir+'/'+e_context.econtext['context'].kwargs['msg'].content[4:]
            self.download_fn(file_path)
            reply = Reply()
            reply.type = ReplyType.IMAGE
            b_img = io.BytesIO()
            with open(file_path, 'rb') as f:
                img_data = f.read()
                b_img.write(img_data)
            reply.content = b_img
            logger.debug(b_img)
            e_context["reply"] = reply
            os.remove(file_path)
            e_context.action = EventAction.BREAK_PASS 
        return

    def bad_reply(self,e_context):
        reply = Reply()
        reply.type = ReplyType.ERROR
        reply.content = f"空指令，输入#help查看指令列表\n"
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS
        return
