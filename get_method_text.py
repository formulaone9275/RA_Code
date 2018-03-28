#!/usr/bin/env python
from __future__ import print_function
from pymongo import MongoClient
import sys,codecs

def run(pid,pid_list,output_model):

    if pid_list.find('.txt')>0:

        ## Read and load all the input PIDs
        id_list=[]

        with open(pid_list, "r") as f:
            for line_str in f:
                if line_str.strip()!='' and not line_str.startswith('#'):
                    id_list.append(line_str.strip())
    else:
        id_list=[pid_list]

    for id_i in id_list:
        print('Document '+pid+': '+id_i)
        doc=mdb.find({pid: id_i})

        #keywords for the section names
        key_word_list=['methods','materials and methods']
        section_id=[]
        section_name=[]
        #find the section names and ids base on the given keywords
        for k_word in key_word_list:
            for raw_doc in doc:

                if raw_doc['sec_type'] ==k_word and len(raw_doc['parent'])==0:

                    section_name.append(raw_doc['sec_type'])
                    section_id.append(raw_doc['id'])

        #have to query again since the last cursor is invalid
        doc_copy=mdb.find({pid: id_i})

        #get the text in sequence based on the section name and id
        for index_i in range(len(section_name)):
            section_child_id=[]
            section_parent_list=[]
            section_text=[]
            for raw_doc in doc_copy:
                #find the child and parent list for an entity
                if raw_doc['sec_type'] ==section_name[index_i]:
                    section_child_id.append(raw_doc['id'])
                    section_parent_list.append(raw_doc['parent'])
                    section_text.append(raw_doc['text'])


            #build a tuple for later usage
            section_child_id_tuple=tuple(section_child_id)

            #find the maximum height of the parent-children tree
            max_height=0
            for ii in section_parent_list:
                max_height= len(ii) if len(ii)>max_height else max_height

            #build a tree dictionary for depth-first search
            tree_dic={}
            for jj in range(max_height+1):
                tree_dic[jj]=[]

            for ii in range(len(section_parent_list)):
                tree_dic[len(section_parent_list[ii])].append(section_child_id[ii])

            #put all the text in order based on the parent-children relations

            text_in_order=[]
            parent_now=[]
            len_list=len(section_child_id)

            #add the root since the section 27356755name has the minimum id
            min_id=min(section_child_id)
            parent_now.append(min_id)
            min_index=section_child_id.index(min_id)
            text_in_order.append(section_child_id[min_index])

            parent_list=section_parent_list[min_index]
            if len(parent_list)==0:
                del section_child_id[min_index]
                del section_parent_list[min_index]

                len_list-=1

            #add the children using depth-first search
            level_i=1
            while len_list>0:
                #get the minimum id of this level
                if len(tree_dic[level_i])>0 and level_i<=max_height:
                    min_id=min(tree_dic[level_i])
                    min_index_tree=tree_dic[level_i].index(min_id)
                    min_index=section_child_id.index(min_id)
                    parent_list=section_parent_list[min_index]

                    if parent_list==parent_now and level_i<max_height:
                        #print('Add one:',section_child_id[min_index])
                        text_in_order.append(section_child_id[min_index])

                        parent_now.append(section_child_id[min_index])
                        #go to the next level
                        del section_child_id[min_index]
                        del section_parent_list[min_index]
                        del tree_dic[level_i][min_index_tree]
                        len_list-=1
                        level_i+=1
                        continue
                    elif parent_list==parent_now and level_i==max_height:
                        #this is leaf level, just add all the leaves
                        #print('Add one:',section_child_id[min_index])
                        text_in_order.append(section_child_id[min_index])

                        del section_child_id[min_index]
                        del section_parent_list[min_index]
                        del tree_dic[level_i][min_index_tree]
                        len_list-=1
                        continue
                    else:
                        #go the upper level
                        parent_now.pop()
                        level_i-=1
                        continue

                else:
                    #go the upper level
                    level_i-=1
                    continue
            if output_model=='0':
                print('text_in_order:',text_in_order)
                #print the text in order
                for text_id in text_in_order:
                    text_index=section_child_id_tuple.index(text_id)
                    print(section_text[text_index])
            else:
                with codecs.open('output_'+id_i+'.txt','w+',encoding='utf8') as f:

                    for text_id in text_in_order:
                        text_index=section_child_id_tuple.index(text_id)
                        f.write(section_text[text_index])
                        f.write('\n')
                    f.write('\n')





if __name__ == '__main__':

    client = MongoClient('localhost')
    mdb = client.pmc.text

    #using pmid or pmcid
    pid = sys.argv[1]
    #input file contain the pid
    pid_list = sys.argv[2]
    #print out the results or save them in a file
    #0 is just printing out, 1 is saving them in a file named output.txt
    output_model=sys.argv[3]


    run(pid,pid_list,output_model)