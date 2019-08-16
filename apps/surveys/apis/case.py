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

import os
import json
import numpy as np
import pandas as pd
import math
from pandas import Series,DataFrame

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
    print(DATA_DIR)
    print('read case data')
    data = pd.read_csv(os.path.join(DATA_DIR,'162020_case_data.csv'))
    print('read case number data')
    patient_number_data = pd.read_csv(os.path.join(DATA_DIR,"case_number(real_value_bycol_162020).csv"))[0:62]

    patient_number = pd.Series(patient_number_data['case_number'].values, index=patient_number_data['disease_code'])
    patient_number.name = 'number'

    print('read case number ratio data')
    patient_ratio_data = pd.read_csv(os.path.join(DATA_DIR,"case_number_ratio(real_value_bycol_162020).csv"))[0:62]
    patient_ratio = pd.Series(patient_ratio_data['case_ratio'].values, index=patient_ratio_data['disease_code'])
    patient_ratio.name = 'ratio'
    symptom_code = Series(data.columns[2:])
    disease_code_duplicate = data.case_disease
    disease_code = Series(list(disease_code_duplicate.drop_duplicates()))
    disease_number = patient_number_data.shape[0]
    symptom_number = len(symptom_code)

    print('read disease data')
    disease_sym_matrix = pd.read_csv(os.path.join(DATA_DIR,'62_disease_data.csv'))
    disease_sym_matrix.set_index(["symptom_cause"], inplace=True)
    data['0'] = 0
    user_list = []

    # input data information
    jsondata = {
        "pathtype": "getanswer",
        "answer_record_seqno": "201908051619300001938_007",
        "content":
            {
                "answer_mainseqno": "201908051619300001938",
                "question_seq": "1",
                "actual_symptom_code": ["C0015230"],
                "answer_detail": ["是"]
            }
    }
    print(jsondata["pathtype"])
    content = jsondata['content']
    print(content)

    global_dict = {}
    # programming
    # interface 1--getanswer
    if jsondata["pathtype"] == "getanswer":
        print('-'*10 + 'getanswer')
        if content["question_seq"] == "1":
            # establish unit matrix and update user list
            global_dict['A' + content["answer_mainseqno"]] = pd.DataFrame(data=0,
                                                                        columns=["symptom_code", "answer_detail"],
                                                                        index=range(1, 21))
            global_dict['A' + content["answer_mainseqno"]]['symptom_code'] = '0'
            global_dict['B' + content["answer_mainseqno"]] = pd.DataFrame(data=1, columns=range(1, 21),
                                                                        index=patient_number.index, dtype=float)
            user_list.append(content["answer_mainseqno"])
        # check the json string whether has wrong information or whether to end(20 question so far).
        if content["answer_mainseqno"] not in user_list:
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
            # establish temporary dataframe,store A and B,perform single-threaded operations
            A = global_dict['A' + content["answer_mainseqno"]].copy()
            A.loc[np.isnan(A['answer_detail']), 'symptom_code'] = '0'
            A.loc[np.isnan(A['answer_detail']), 'answer_detail'] = 0
            B = global_dict['B' + content["answer_mainseqno"]]
            # calculate similar disease case number(disease_case_number) and probability(disease_array)
            DC_number = data[(data[A.iloc[0, 0]] == A.iloc[0, 1]) & (data[A.iloc[1, 0]] == A.iloc[1, 1]) & (
                        data[A.iloc[2, 0]] == A.iloc[2, 1]) & (data[A.iloc[3, 0]] == A.iloc[3, 1]) & (
                                         data[A.iloc[4, 0]] == A.iloc[4, 1]) & (
                                         data[A.iloc[5, 0]] == A.iloc[5, 1]) & (
                                         data[A.iloc[6, 0]] == A.iloc[6, 1]) & (
                                         data[A.iloc[7, 0]] == A.iloc[7, 1]) & (
                                         data[A.iloc[8, 0]] == A.iloc[8, 1]) & (
                                         data[A.iloc[9, 0]] == A.iloc[9, 1]) & (
                                         data[A.iloc[10, 0]] == A.iloc[10, 1]) & (
                                         data[A.iloc[11, 0]] == A.iloc[11, 1]) & (
                                         data[A.iloc[12, 0]] == A.iloc[12, 1]) & (
                                         data[A.iloc[13, 0]] == A.iloc[13, 1]) & (
                                         data[A.iloc[14, 0]] == A.iloc[14, 1]) & (
                                         data[A.iloc[15, 0]] == A.iloc[15, 1]) & (
                                         data[A.iloc[16, 0]] == A.iloc[16, 1]) & (
                                         data[A.iloc[17, 0]] == A.iloc[17, 1]) & (
                                         data[A.iloc[18, 0]] == A.iloc[18, 1]) & (
                                         data[A.iloc[19, 0]] == A.iloc[19, 1])]['case_disease'].groupby(
                data['case_disease']).count()
            disease_case_number = DC_number.sum()
            data_pba = DC_number.div(patient_number, axis=0)
            data_pba = data_pba.fillna(0)
            data_mul = data_pba.mul(patient_ratio, axis=0)
            data_pab = data_mul / data_mul.sum()
            data_pab_d0 = data_pab[data_pab != 0]
            data_pab_d01 = pd.DataFrame(data_pab_d0)
            data_pab_d01.columns = ['probability']
            disease_array0 = data_pab_d01.sort_values(by="probability", ascending=False)
            disease_array0.loc[0] = 0
            disease_array0.loc[1] = 0
            disease_array0.loc[2] = 0
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
                confirm_disease_code = disease_array0.index[0]
                confirm_disease_percent = disease_array0.iloc[0, 0]
                disease_array = [
                    {"disease_code": disease_array0.index[0], "disease_percent": str(disease_array0.iloc[0, 0])},
                    {"disease_code": disease_array0.index[1], "disease_percent": str(disease_array0.iloc[1, 0])},
                    {"disease_code": disease_array0.index[2], "disease_percent": str(disease_array0.iloc[2, 0])}]
                errmessage = ''
            else:
                result_code = 'SUCCESS'
                answer_mainseqno = content["answer_mainseqno"]
                ifend = '1'
                next_symptom_code = ['']
                next_answer_detail = ['']
                # need to calculate the similarity
                confirm_disease_code = ''
                confirm_disease_percent = ''
                disease_array = ['']
                errmessage = ''
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
                    "disease_case_number": str(disease_case_number)
                },
            "errmessage": ""
        }
        print('-'*10 + 'getanswer end')

    # interface 2--cancelanswer
    elif jsondata["pathtype"] == "cancelanswer":
        print('-'*10 + 'cancelanswer')
        if content["answer_mainseqno"] not in user_list:
            result_code = 'FAIL'
            answer_mainseqno = ''
            errmessage = '整体会话主键不存在'
        else:
            global_dict['A' + content["answer_mainseqno"]].iloc[(int(content["question_seq"]) - 1), 0] = '0'
            global_dict['A' + content["answer_mainseqno"]].iloc[(int(content["question_seq"]) - 1), 1] = 0
            global_dict['B' + content["answer_mainseqno"]][int(content["question_seq"])] = 1
            if content["question_seq"] == "1":
                user_list.remove(content["answer_mainseqno"])
            result_code = 'SUCCESS'
            answer_mainseqno = content["answer_mainseqno"]
            errmessage = ''
        python_output = {
            "resultcode": result_code,
            "answer_record_seqno": jsondata["answer_record_seqno"],
            "answer_mainseqno": answer_mainseqno,
            "errmessage": ""
        }
        print('-'*10 + 'cancelanswer end')

    # output the json string
    json_output = json.dumps(python_output)
    print(json_output)
    return JsonResponse(json_output,safe=False)

# answer()