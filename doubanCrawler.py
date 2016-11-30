import time
import urllib.request
import urllib.parse
import urllib.error
import numpy as np
from bs4 import BeautifulSoup
from openpyxl import Workbook

def read_page(tags, max_page):
    books = []
    page_nums = 0
    #遍历各个tag
    for tag in tags:
        page_num=0
        pages_in_all=1
        book_count=0
        while page_num < pages_in_all:
            quote = urllib.parse.quote(tag) #url中不能出现汉字，用quote方法转码为utf-8
            url = 'https://book.douban.com/tag/' + quote + '?start=' + str(page_num *20) + '&type=S'
            #3种不同浏览器信息，防止block
            uas = [{'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'},{'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'},{'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'}]
            try:
                req = urllib.request.Request(url, None, headers=uas[page_num %len(uas)])
                with urllib.request.urlopen(req) as response:
                    page = response.read()
            except urllib.error.URLError as e:
                print('error:' , e)
            
            soup = BeautifulSoup(page,'html.parser')
            #根据div paginator获取最大页数，防止超域
            if page_num == 0:
                try:
                    if soup.find('div','paginator')==None:
                        pages_in_all =1
                    else:
                        pg_soup = soup.find('div','paginator').find_all('a')
                        pages_in_all = int(pg_soup[-2].string.strip())
                    #print('tag',tag,' pages in all:',pages_in_all)
                    if pages_in_all > max_page:
                        pages_in_all = max_page
                except:
                    print('oooops, page_in_all occurs error')
            
            #查找li标签，解析每本书的信息
            li_soup = soup.find_all('li', 'subject-item')
            for li in li_soup:
                try:                
                    #仅当有评价且评价人数>10时收集该书信息
                    if li.find('span', 'rating_nums')!= None and li.find('span','pl').string.strip()[1:2]!='少' and li.find('span','pl').string.strip()[1:2]!='目':                
                        title = li.find(title=True)['title'] #找到存在attribute为title的标签，获取该标签title的值
                        pub = li.find('div', 'pub').string.strip() #找到div中class名为pub的标签，获取该标签的文本
                        rating = float(li.find('span', 'rating_nums').string.strip())
                        rating_by_people = int(li.find('span','pl').string.strip()[1:-4])
                        try:
                            abstract = li.find('p').string.strip()
                        except:
                            abstract ='暂无'
                        book = {'tag':tag,'title':title,'pub':pub,'rating':rating,'rating_by_people':rating_by_people,'abstract':abstract}
                        print([i for i in book.items()])
                        books.append(book)
                        book_count+=1
                except AttributeError as e:
                    print('error:',e,'@title:',title)
            page_num+=1        
            time.sleep(np.random.rand()*5)    
        page_nums+=page_num
        #print(page_num,'pages of tag',tag,' crawled,',book_count,'books found.')
    print(page_nums,'pages crawled,',len(books),'books found in all.')
    return books

def save_books(books,tags):
    wb=Workbook()
    str_tag=''
    for tag in tags:
        str_tag=str_tag+'#'+tag
    wb_name = 'booklist'+str_tag+'.xlsx'
    ws=wb.active
    ws.title = str_tag
    ws.append(['编号','标签','书名','评分','评价人数','出版信息','摘要'])
    count=1
    for book in books:
        ws.append([count,book['tag'],book['title'],book['rating'],book['rating_by_people'],book['pub'],book['abstract']])
        count+=1
    wb.save(wb_name)
    print('books of tag' +str_tag + 'have been saved.')

def run_crawler(tags, max_page=20):
    save_books(read_page(tags, max_page),tags)

if __name__=='__main__':
    tags = ['心理学','学习','决策','认知','人工智能']
    max_page=20
    run_crawler(tags,max_page)
