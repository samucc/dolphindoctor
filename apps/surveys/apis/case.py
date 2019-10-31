# -*- coding: utf-8 -*-
#

from rest_framework import generics
from rest_framework_bulk import BulkModelViewSet
from rest_framework.generics import ListAPIView, get_object_or_404, RetrieveUpdateAPIView,RetrieveAPIView,CreateAPIView,ListCreateAPIView
from rest_framework.pagination import LimitOffsetPagination

from ..serializers import CaseSerializer
from ..models import Case
from common.permissions import IsOrgAdmin
from common.mixins import IDInCacheFilterMixin
from django.http import JsonResponse
from rest_framework.decorators import api_view
from dolphindoctor.settings import PROJECT_DIR
from django.core.cache import cache

import os
import json
import numpy as np
import pandas as pd
import math
from pandas import Series,DataFrame
from sklearn.externals import joblib
from datetime import datetime
from collections import OrderedDict, defaultdict


__all__ = ['CaseViewSet']


class CaseViewSet(IDInCacheFilterMixin, BulkModelViewSet):
    filter_fields = ('name','disease_code','case_number')
    search_fields = filter_fields
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = (IsOrgAdmin,)
    pagination_class = LimitOffsetPagination


@api_view(['GET', 'POST'])
def answer(request):
    # print(type(request.data))
    # print(request.data)
    DATA_DIR = os.path.join(PROJECT_DIR, 'data')
    #print(DATA_DIR)
    #print('read case number data')
    patient_number_data = pd.read_csv(os.path.join(DATA_DIR,"case_number_1025.csv"))[0:77]

    patient_number = pd.Series(patient_number_data['case_number'].values, index=patient_number_data['disease_code'])
    patient_number.name = 'number'

    #print('read case number ratio data')
    patient_ratio_data = pd.read_csv(os.path.join(DATA_DIR,"case_number_ratio_1025.csv"))[0:77]
    patient_ratio = pd.Series(patient_ratio_data['case_ratio'].values, index=patient_ratio_data['disease_code'])
    patient_ratio.name = 'ratio'
    
    #print('read disease data')
    disease_sym_matrix = pd.read_csv(os.path.join(DATA_DIR,'77_disease_data_1025.csv'))
    SD_symcode=pd.DataFrame(disease_sym_matrix['symptom_cause'])
    SD_symcode.columns=['symptom_code']
    symptom_code=disease_sym_matrix['symptom_cause']
    symptom_code.name='0'
    disease_code=patient_number_data['disease_code']
    disease_code.name='0'
    disease_number = patient_number_data.shape[0]
    symptom_number = len(symptom_code)
    disease_sym_matrix.set_index(["symptom_cause"], inplace=True)

    # input data information
    jsondata = request.data
    # jsondata = {
    #     "pathtype": "getanswer",
    #     "answer_record_seqno": "201908051619300001938_007",
    #     "content":
    #         {
    #             "answer_mainseqno": "201908051619300001938",
    #             "question_seq": "1",
    #             "actual_symptom_code": ["C0015230"],
    #             "answer_detail": ["是"]
    #         }
    # }
    #print(jsondata["pathtype"])
    content = jsondata['content']
    #print(content)

    python_output = {}
    global_dict = cache.get(('global_dict'+content["answer_mainseqno"]),None)


    # programming
    # interface 1--getanswer
    if jsondata["pathtype"] == "getanswer":
        #print('-'*10 + 'getanswer')
        if content["question_seq"] == "1":
            # establish unit matrix 
            global_dict={}
            global_dict['A' + content["answer_mainseqno"]] = pd.DataFrame(data=0,
                                                                        columns=["symptom_code", "answer_detail"],
                                                                        index=range(1, 21))
            global_dict['A' + content["answer_mainseqno"]]['symptom_code'] = '0'
            global_dict['B' + content["answer_mainseqno"]] = pd.DataFrame(data=1, columns=range(1, 21),
                                                                        index=patient_number.index, dtype=float)        
        # check the json string whether has wrong information or whether to end(20 question so far).
        if not global_dict:
            result_code = 'FAIL'
            answer_mainseqno = ''
            ifend = ''
            next_symptom_code = []
            next_answer_detail = []
            confirm_disease_code = ''
            confirm_disease_percent = ''
            disease_array = []
            disease_case_number = ''
            errmessage = '整体会话主键不存在'
        elif content["actual_symptom_code"][0] not in list(symptom_code):
            result_code = 'FAIL'
            answer_mainseqno = ''
            ifend = ''
            next_symptom_code = ['']
            next_answer_detail = ['']
            confirm_disease_code = ''
            confirm_disease_percent = ''
            disease_array = []
            disease_case_number = ''
            errmessage = '症状代码不存在'
        else:
            # confirm the correct json string
            # update A_ and B_
            global_dict['A' + content["answer_mainseqno"]].iloc[(int(content["question_seq"]) - 1), 0] = \
            content["actual_symptom_code"][0]
            if content["answer_detail"][0] == "是":
                global_dict['A' + content["answer_mainseqno"]].iloc[(int(content["question_seq"]) - 1), 1] = 1
                global_dict['B' + content["answer_mainseqno"]][int(content["question_seq"])] = disease_sym_matrix.loc[
                    content["actual_symptom_code"][0]]
            elif content["answer_detail"][0] == "否":
                global_dict['A' + content["answer_mainseqno"]].iloc[(int(content["question_seq"]) - 1), 1] = 0
                global_dict['B' + content["answer_mainseqno"]][int(content["question_seq"])] = 1 - \
                                                                                             disease_sym_matrix.loc[
                                                                                                 content[
                                                                                                     "actual_symptom_code"][
                                                                                                     0]]
            else:
                global_dict['A' + content["answer_mainseqno"]].iloc[(int(content["question_seq"]) - 1), 1] = np.nan
                global_dict['B' + content["answer_mainseqno"]][int(content["question_seq"])] = 1
            cache.set(('global_dict'+content["answer_mainseqno"]),global_dict,timeout=86400)
            # establish temporary dataframe,store A and B,perform single-threaded operations
            A = global_dict['A' + content["answer_mainseqno"]].copy()
            A.loc[np.isnan(A['answer_detail']), 'symptom_code'] = '0'
            A.loc[np.isnan(A['answer_detail']), 'answer_detail'] = 0
            B = global_dict['B' + content["answer_mainseqno"]]
            # calculate similar disease case number(disease_case_number) and probability(disease_array)
            # has been removed
            # calculate entropy to get the next question
            H20 = Series([0] * symptom_number)
            H20 = H20.astype(float)
            H21 = Series([0] * symptom_number)
            H21 = H21.astype(float)
            pb20 = Series([0] * symptom_number)
            pb20 = H20.astype(float)
            pb21 = Series([0] * symptom_number)
            pb21 = H20.astype(float)
            B_mul = B[1] * B[2] * B[3] * B[4] * B[5] * B[6] * B[7] * B[8] * B[9] * B[10] * B[11] * B[12] * B[13] * \
                    B[14] * B[15] * B[16] * B[17] * B[18] * B[19]
            for i in range(symptom_number):
                if symptom_code[i] in list(global_dict['A' + content["answer_mainseqno"]]["symptom_code"]):
                    H20[i] = 100
                    H21[i] = 100
                    pb20[i] = 1
                    pb21[i] = 1
                else:
                    pb20[i] = (B_mul * (1 - disease_sym_matrix.loc[symptom_code[i]]) * patient_number).sum() / (
                                B_mul * patient_number).sum()
                    pb21[i] = 1 - pb20[i]
                    if pb21[i] == 0:
                        H20[i] = 10
                        H21[i] = 10
                    else:
                        data_pba20 = B_mul * (1 - disease_sym_matrix.loc[symptom_code[i]])
                        data_mul20 = data_pba20.mul(patient_ratio, axis=0)
                        data_pab20 = data_mul20 / data_mul20.sum()
                        data_pab_d020 = data_pab20[data_pab20 != 0]
                        for j in range(0, len(data_pab_d020)):
                            H20[i] = H20[i] - data_pab_d020[j] * math.log(data_pab_d020[j], disease_number)
                        data_pba21 = B_mul * disease_sym_matrix.loc[symptom_code[i]]
                        data_mul21 = data_pba21.mul(patient_ratio, axis=0)
                        data_pab21 = data_mul21 / data_mul21.sum()
                        data_pab_d021 = data_pab21[data_pab21 != 0]
                        for j in range(0, len(data_pab_d021)):
                            H21[i] = H21[i] - data_pab_d021[j] * math.log(data_pab_d021[j], disease_number)
            H20 = H20.fillna(0)
            H21 = H21.fillna(0)
            H2 = H20 * pb20 + H21 * pb21
            # determine whether end or not.
            if H2.min() < 1 and int(content["question_seq"]) < 20:
                # get the next question(corresponding symptom code) and other output information
                H2_sym = pd.DataFrame({'H2': H2, 'sym': symptom_code})
                next_symptom_code_str = H2_sym['sym'][H2_sym['H2'] == H2_sym['H2'].min()].values[0]
                next_symptom_code = []
                next_symptom_code.append(next_symptom_code_str)
                result_code = 'SUCCESS'
                answer_mainseqno = content["answer_mainseqno"]
                ifend = '0'
                next_answer_detail = ["是", "否", "不确定"]
                confirm_disease_code = ''
                confirm_disease_percent = ''
                disease_array = ['']
                errmessage = ''
            else:
                #get the model file using joblib
                forest_clf_file = "forest_clf_1025.pkl"
                forest_clf = joblib.load(os.path.join(DATA_DIR,forest_clf_file))
                gnb_clf_file = "gnb_clf_1025.pkl"
                gnb_clf = joblib.load(os.path.join(DATA_DIR,gnb_clf_file))
                mnb_clf_file = "mnb_clf_1025.pkl"
                mnb_clf = joblib.load(os.path.join(DATA_DIR,mnb_clf_file))
                bnb_clf_file = "bnb_clf_1025.pkl"
                bnb_clf = joblib.load(os.path.join(DATA_DIR,bnb_clf_file))
                #ensemble learning to predict disease
                Sd=pd.merge(A,SD_symcode,how='right')
                Sd['answer_detail']=Sd['answer_detail'].fillna(0)
                Sd=Sd.sort_values(by="symptom_code" , ascending=True)
                some_digit=np.array(Sd["answer_detail"])
                #first classifier:Bayes method,based on probability               
                A_sym=list(A[A["answer_detail"]==1]["symptom_code"])
                sym_num=len(A_sym)
                Bys_dsm=(disease_sym_matrix.copy()).T
                Bys_dsm['1']=1
                Bys_pba=Bys_dsm['1']
                for i in range(sym_num):
                    Bys_pba=Bys_pba*Bys_dsm[A_sym[i]]
                Bys_baa=Bys_pba*patient_ratio
                Bys_pab=Bys_baa/sum(Bys_baa)
                bys_clf_predict=disease_code.copy()
                bys_clf_predict=pd.DataFrame(bys_clf_predict)
                bys_clf_predict.columns=['bys_clf.classes']
                bys_clf_predict['predict_proba']=list(Bys_pab)
                #second classifier:Random Forest
                forest_clf_predict_proba1=pd.DataFrame(forest_clf.predict_proba([some_digit])[0],columns=['predict_proba'])
                forest_clf_classes1=pd.DataFrame(forest_clf.classes_,columns=['sgd_clf.classes'])
                forest_clf_predict=pd.merge(forest_clf_classes1,forest_clf_predict_proba1,left_index=True,right_index=True)          
                #third classifier:GaussianNB
                gnb_clf_predict_proba1=pd.DataFrame(gnb_clf.predict_proba([some_digit])[0],columns=['predict_proba'])
                gnb_clf_classes1=pd.DataFrame(gnb_clf.classes_,columns=['gnd_clf.classes'])
                gnb_clf_predict=pd.merge(gnb_clf_classes1,gnb_clf_predict_proba1,left_index=True,right_index=True)
                #fourth:MultinomialNB
                mnb_clf_predict_proba1=pd.DataFrame(mnb_clf.predict_proba([some_digit])[0],columns=['predict_proba'])
                mnb_clf_classes1=pd.DataFrame(mnb_clf.classes_,columns=['mnd_clf.classes'])
                mnb_clf_predict=pd.merge(mnb_clf_classes1,mnb_clf_predict_proba1,left_index=True,right_index=True)
                #fifth:BernoulliNB
                bnb_clf_predict_proba1=pd.DataFrame(bnb_clf.predict_proba([some_digit])[0],columns=['predict_proba'])
                bnb_clf_classes1=pd.DataFrame(bnb_clf.classes_,columns=['bnd_clf.classes'])
                bnb_clf_predict=pd.merge(bnb_clf_classes1,bnb_clf_predict_proba1,left_index=True,right_index=True)
                #ensemble soft voting
                ensemble_proba=(1/5)*bys_clf_predict['predict_proba']+(3/5)*forest_clf_predict['predict_proba']+(1/15)*gnb_clf_predict['predict_proba']+(1/15)*mnb_clf_predict['predict_proba']+(1/15)*bnb_clf_predict['predict_proba']
                esm_clf_predict=disease_code.copy()
                esm_clf_predict=pd.DataFrame(esm_clf_predict)
                esm_clf_predict.columns=['esm_clf.classes']
                esm_clf_predict['predict_proba']=ensemble_proba*0.98
                esm_clf_predict=esm_clf_predict.sort_values(by="predict_proba" , ascending=False)
                #extract outcome
                result_code='SUCCESS'
                answer_mainseqno=content["answer_mainseqno"]
                ifend='1'
                next_symptom_code=['']
                next_answer_detail=['']
                #need to calculate the similarity
                confirm_disease_code=str(list(esm_clf_predict['esm_clf.classes'])[0])
                confirm_disease_percent=str(list(esm_clf_predict['predict_proba'])[0])
                disease_array=[{"disease_code":str(list(esm_clf_predict['esm_clf.classes'])[0]),"disease_percent":str(list(esm_clf_predict['predict_proba'])[0])},{"disease_code":str(list(esm_clf_predict['esm_clf.classes'])[1]),"disease_percent":str(list(esm_clf_predict['predict_proba'])[1])},{"disease_code":str(list(esm_clf_predict['esm_clf.classes'])[2]),"disease_percent":str(list(esm_clf_predict['predict_proba'])[2])}]
                errmessage='' 
                cache.delete(('global_dict'+content["answer_mainseqno"]))
                del forest_clf,gnb_clf,mnb_clf,bnb_clf
        python_output = {
            "resultcode": result_code,
            "answer_record_seqno": jsondata["answer_record_seqno"],
            "returnmessage":
                {
                    "answer_mainseqno": answer_mainseqno,
                    "ifend": str(ifend),
                    "next_symptom_code": next_symptom_code,
                    "next_answer_detail": next_answer_detail,
                    "confirm_disease_code": confirm_disease_code,
                    "confirm_disease_percent": str(confirm_disease_percent),
                    "disease_array": disease_array,
                    "disease_case_number": ''
                },
            "errmessage": errmessage
        }
        #print('-'*10 + 'getanswer end')

    # interface 2--cancelanswer
    elif jsondata["pathtype"] == "cancelanswer":
        #print('-'*10 + 'cancelanswer')
        if not global_dict:
            result_code = 'FAIL'
            answer_mainseqno = ''
            errmessage = '整体会话主键不存在'
        else:
            global_dict['A' + content["answer_mainseqno"]].iloc[(int(content["question_seq"]) - 1), 0] = '0'
            global_dict['A' + content["answer_mainseqno"]].iloc[(int(content["question_seq"]) - 1), 1] = 0
            global_dict['B' + content["answer_mainseqno"]][int(content["question_seq"])] = 1
            result_code = 'SUCCESS'
            answer_mainseqno = content["answer_mainseqno"]
            errmessage = ''
            cache.set(('global_dict'+content["answer_mainseqno"]),global_dict,timeout=86400)
        python_output = {
            "resultcode": result_code,
            "answer_record_seqno": jsondata["answer_record_seqno"],
            "answer_mainseqno": answer_mainseqno,
            "errmessage": errmessage
        }
        #print('-'*10 + 'cancelanswer end')

    # output the json string
    del patient_number_data,patient_ratio_data,disease_sym_matrix
    json_output = json.dumps(python_output)
    #print(json_output)
    return JsonResponse(python_output,safe=False)

# answer()

def get_key(dict, value):
    return [k for k, v in dict.items() if v >= value]

def months(birthday_str):
    birth_year=datetime.strptime(birthday_str,"%Y-%m-%d").year
    now_year=datetime.now().year
    birth_month=datetime.strptime(birthday_str,"%Y-%m-%d").month
    now_month=datetime.now().month
    num=(now_year-birth_year)*12+(now_month-birth_month)
    return num

def get_body_result(birth_month,value,csv_name):
    DATA_DIR = os.path.join(PROJECT_DIR, 'data','Growth_data_v1.1')
    data_df = pd.read_csv(os.path.join(DATA_DIR,csv_name),encoding='gb2312')
    #print(data_df.columns)
    if data_df.empty:
        return "No data"
    try:
        # loc->Series->to OrderedDict
        data_dict = data_df.loc[birth_month].to_dict(OrderedDict)
        data_dict.popitem(last=False)[0] # pop dataframe column
        #print(data_dict)
    except:
        return "No data"
    result_list = get_key(data_dict,value)
    del data_df
    if result_list:
        return result_list[0]
    return "No data"


@api_view(['POST'])
def bodyindex(request):
    jsondata = request.data
    #print(jsondata)
    content = jsondata['content']

    birthday,sex,height,weight,bmi,headcirc = content.get("birthday"),content.get("sex"),content.get("height"),content.get("weight"),content.get("bmi"),content.get("headcirc")

    python_output = {
        "resultcode": "SUCCESS",
        "returnmessage": {
        },
        "errmessage": ""
    }
    
    if jsondata["pathtype"] != "getbodyindex":
        python_output["resultcode"] = "FAIL"
        python_output["errmessage"] = "wrong pathtype"
        return JsonResponse(python_output,safe=False)
    if sex not in [u"男",u"女"]:
        python_output["resultcode"] = "FAIL"
        python_output["errmessage"] = "wrong sex"
        return JsonResponse(python_output,safe=False)
    birth_month = months(birthday)
    height_result,weight_result,bmi_result,headcirc_result = "No data","No data","No data","No data"

    csv_dict = {
        u"男_height":"Table_1.csv",u"女_height":"Table_2.csv",
        u"男_weight":"Table_3.csv",u"女_weight":"Table_4.csv",
        u"男_bmi":"Table_5.csv",u"女_bmi":"Table_6.csv",
        u"男_headcirc":"Table_7.csv",u"女_headcirc":"Table_8.csv",
    }

    try:
        height = float(height)
        csv_name = csv_dict.get(u"{}_height".format(sex))
        #print(sex,height,csv_name)
        if csv_name:
            height_result = get_body_result(birth_month,height,csv_name)
    except Exception as e:
        #print("1",e)
        pass
    try:
        weight = float(weight)
        csv_name = csv_dict.get(u"{}_weight".format(sex))
        #print(sex,weight,csv_name)
        if csv_name:
            weight_result = get_body_result(birth_month,weight,csv_name)
    except Exception as e:
        #print("2",e)
        pass
    try:
        bmi = float(bmi)
        csv_name = csv_dict.get(u"{}_bmi".format(sex))
        #print(sex,bmi,csv_name)
        if csv_name:
            bmi_result = get_body_result(birth_month,bmi,csv_name)
    except Exception as e:
        #print("3",e)
        pass
    try:
        headcirc = float(headcirc)
        csv_name = csv_dict.get(u"{}_headcirc".format(sex))
        #print(sex,headcirc,csv_name)
        if csv_name:
            headcirc_result = get_body_result(birth_month,headcirc,csv_name)
    except Exception as e:
        #print("4",e)
        pass
    
    python_output["returnmessage"]["month"] = str(birth_month)
    python_output["returnmessage"]["height"] = str(height_result)
    python_output["returnmessage"]["weight"] = str(weight_result)
    python_output["returnmessage"]["bmi"] = str(bmi_result)
    python_output["returnmessage"]["headcirc"] = str(headcirc_result)
    
    json_output = json.dumps(python_output)
    return JsonResponse(python_output,safe=False) 
