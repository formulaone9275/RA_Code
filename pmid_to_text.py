#!/usr/bin/env python

"""
Input: PMIDs
Output: Abstract text, sentence indices, pubtator annotations (JSON format)
"""
from __future__ import print_function
import sys
import json
from pymongo import MongoClient
from html_p import getHTML

def run():

    ## Read and load all the input PMIDs ##
    pmid_list=[]

    with open(pmid_file, "r") as f:
        for line_str in f:
            if line_str.strip()!='' and not line_str.startswith('#'):
                pmid_list.append(line_str.strip())
    #print len(pmid_list)
    #

    # Load text and pubtator annotations from MongoDB
    # prospective studies in mesh
    pmid_set_ps_in_mesh=[]
    #prospective studies in mesh and in text
    pmid_set_ps_in_text=[]
    #prospective studies in mesh but not in text
    pmid_set1_ps_not_in_text=[]
    doc={}
    for pmid in pmid_list:
        raw_doc = mdb.find_one({'docId': pmid})
        if raw_doc is None:
            continue

        #doc['docId'], doc['text'] = pmid, raw_doc['text']
        #doc['sentence'] = raw_doc['sentence']
        if 'mesh' in raw_doc:
            #doc['mesh'] = raw_doc['mesh']
            if "Prospective Studies" in raw_doc['mesh'] or "prospective studies" in raw_doc['mesh'] or "Prospective studies" in raw_doc['mesh']:
                #print("Found!")
                pmid_set_ps_in_mesh.append(pmid)
                #check if prospective in text
                text_string=raw_doc['text']
                #print(pmid)
                #print(raw_doc['text'])
                string_index=text_string.find("prospective")+text_string.find("Prospective")+text_string.find("Prospectively")+text_string.find("prospectively")
                if string_index>-4:
                    #print("In text")
                    pmid_set_ps_in_text.append(pmid)
                else:
                    #print("Not in text")
                    pmid_set1_ps_not_in_text.append(pmid)
                #build a sentence list
                sentence_list=[]
                for dic_i in raw_doc['sentence']:
                    sentence_list.append(text_string[dic_i['charStart']:dic_i['charEnd']+1])
                #create a dictionary, the key is the pmid and the element is the sentence list
                doc[pmid]=getHTML(raw_doc)#sentence_list
    #print(doc)
    print("In mesh",pmid_set_ps_in_mesh)
    print("In mesh and in text",pmid_set_ps_in_text)
    print("In mesh but not in text",pmid_set1_ps_not_in_text)
    #create a html file
    pmid_list=[]
    #print(type(output_model))
    if output_model=='1':
        pmid_list=pmid_set_ps_in_mesh
    elif output_model=='2':
        pmid_list=pmid_set_ps_in_text
    elif output_model=='3':
        pmid_list=pmid_set1_ps_not_in_text

    with open(output_file, 'w') as f:
        for pmid_i in pmid_list:
            #print(pmid_i)
            line = json.dumps(doc[pmid_i])
            f.write(line+'\n')


if __name__ == '__main__':

    client = MongoClient('localhost')
    #pdb = client.pubtator2018.medline.aligned
    mdb = client.medline2018.text
    #input file contain the pmid
    pmid_file = sys.argv[1]
    #html output file
    output_file = sys.argv[2]
    #which list to output
    #1 for list of pmid have a mesh 'prospective studies'
    #2 for list of pmid that have prospective or prospectively in the text
    #3 for list of pmid that do not have prospective or prospectively in the text
    output_model=sys.argv[3]


    run()