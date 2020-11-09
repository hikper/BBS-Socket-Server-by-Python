#!/usr/bin/env python3
from datetime import date
import re
import threading

board_list = dict()
post_list = dict()
board_index_cnt = 1
post_sn_cnt = 1


#implement mutually exclusive shared memory global variable
board_list_lock = threading.Lock()
post_list_lock = threading.Lock()
board_index_cnt_lock = threading.Lock()
post_sn_cnt_lock = threading.Lock()


class Board:
    def __init__(self,index,name,moderator):
        self.index = index
        self.name = name
        self.moderator = moderator
        self.post_list = list()
    
    def list_post(self):
        print("Undo")

class Post:
    def __init__(self,sn,board,title,author,date,content):
        self.sn = sn
        self.board = board
        self.title = title
        self.author = author
        self.date = date
        self.content = content
        self.comment_list = list()

def get_date():
    today = date.today()
    res = today.strftime("%m/%d")
    return res

def post_cmd_parse(text):
    res = re.findall("create-post (.*) --title (.*) --content (.*)",text)
    board_name,title,content = res[0]
    content = content.replace("<br>","\n")
    return board_name,title,content



def create_board(name,moderator):

    global board_index_cnt
    if moderator == "":
        return "Please login first."
    if board_list.get(name) != None:
        return "Board already exists."
    board_index_cnt_lock.acquire()
    board_list_lock.acquire()
    board_list[name] = Board(board_index_cnt,name,moderator)
    board_index_cnt += 1
    board_list_lock.release()
    board_index_cnt_lock.release()
    return "Create board successfully."

def list_board():
    response = "Index\tName\tModerator"
    for board in board_list.values():
        response += f"\n{board.index}\t{board.name}\t{board.moderator}"
    return response

def create_post(raw,author):
    global post_sn_cnt
    board_name,title,content = post_cmd_parse(raw)
    if author == "":
        return "Please login first."
    if board_list.get(board_name) == None:
        return "Board does not exist."
    post_sn_cnt_lock.acquire()
    post_list_lock.acquire()
    post_list[post_sn_cnt] = Post(post_sn_cnt,board_name,title,author,get_date(),content)
    board_list[board_name].post_list.append(post_sn_cnt)
    post_sn_cnt += 1
    
    post_sn_cnt_lock.release()
    post_list_lock.release()
    return "Create post successfully."

def list_post(board_name):
    if board_list.get(board_name) == None:
        return "Board does not exist."
    response = "S/N\tTitle\tAuthor\tDate"
    for sn in board_list[board_name].post_list:
        post = post_list[sn]
        response += f"\n{post.sn}\t{post.title}\t{post.author}\t{post.date}"
    return response

def read_post(sn):
    if post_list.get(sn) == None:
        return "Post does not exist."
    post = post_list[sn]
    response = f"Author: {post.author}"
    response += f"\nTitle: {post.title}"
    response += f"\nDate: {post.date}"
    response += "\n--"
    response += f"\n{post.content}"
    response += "\n--"
    for comment in post.comment_list:
        response += f"\n{comment}"
    return response

def delete_post(sn,operator):
    if operator == "":
        return "Please login first."
    if post_list.get(sn) == None:
        return "Post does not exist."
    post = post_list[sn]
    if operator != post.author:
        return "Not the post owner."
    board_list[post.board].post_list.remove(sn)
    del post_list[sn]
    return "Delete successfully."

def update_post(sn,operator,raw):
    if operator == "":
        return "Please login first."
    if post_list.get(sn) == None:
        return "Post does not exist."
    fake,title_or_content,new = re.findall("update-post ([0-9]*) --([tilecon]*) (.*)",raw)[0]
    post = post_list[sn]
    if operator != post.author:
        return "Not the post owner"
    if title_or_content == "title":
        post_list[sn].title = new
    elif title_or_content == "content":
        post_list[sn].content = new
    return "Update successfully."

def make_comment(sn,operator,raw):
    if operator == "":
        return "Please login first"
    if post_list.get(sn) == None:
        return "Post does not exist."
    comment = re.findall("comment [0-9]* (.*)",raw)[0]
    post_list[sn].comment_list.append(f"{operator}: {comment}")
    return "Comment successfully"   


def main():
    # print("Start testing")
    # for i in range(3):
    #     create_board(f"test{i}",f"coder{i}")
    # print(list_board())
    # for i in range(5):
    #     create_post("test1",f"title{i}","i am coding",f"coder")
    # print(list_post("test1"))
    # print(read_post(4))
    # print(delete_post(4,""))
    # print(delete_post(8,"ghost"))
    # print(delete_post(4,"coder"))
    # print(update_post(3,"coder","title","what is new"))
    # print(list_post("test1"))
    board_name,title,content = post_cmd_parse("create-post NP_HW --title About NP HW_2 --content Help!<br>I have some problem!")
    print(board_name)
    print(title)
    print(content)
if __name__=="__main__":
    main()