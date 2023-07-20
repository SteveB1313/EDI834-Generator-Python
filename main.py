import pandas as pd
from constants import *
# Load functions
from functions import generate_ISA, generate_GS, generate_ST, generate_BGN, generate_N1, generate_segment_from_array
# Load the data
enrollees = pd.read_csv(ENROLLEE_CSV)
dependents = pd.read_csv(DEPENDENT_CSV)
# EDI Document List
edi_documents = []
# Group enrollees by benefit plan provider name
grouped = enrollees.groupby(PROVIDER_NAME_COL)
unique_control_num = 1
for provider_name, enrollee_group in grouped:
    # print(f"Provider Name: {provider_name}")
    # EDI Document Data List for Each Provider
    edi_provider_documents = []

    # ISA SEGMENT
    isa_segment = generate_ISA(unique_control_num)
    print(f"ISA SEGMENT: {isa_segment}")
    # END ISA SEGMENT

    # GS SEGMENT
    gs_segment = generate_GS(unique_control_num)
    print(f"GS SEGMENT: {gs_segment}")
    # END GS SEGMENT

    # ST SEGMENT
    st_segment = generate_ST(unique_control_num)
    print(f"ST SEGMENT: {st_segment}")
    # END ST SEGMENT

    # BGN SEGMENT
    ## Pass the params for the BGN Segment here
    trans_set_ref_num = 'TRANS_SET_REF_NUM'
    original_trans_set_ref_num = 'ORIGIN_TRANS_SET_REF_NUM'
    bgn_segment = generate_BGN(BGN_TRANS_PURP_CODE_ORIGIN, trans_set_ref_num, original_trans_set_ref_num)
    print(f"BGN SEGMENT: {bgn_segment}")
    #End BGN SEGMENT

    # N1 SEGMENTS for Sponsor and Payer
    ## sponsor segment
    sponser_name = 'LBMC Employment Partners LLC'
    sponsor_id_number = 'XXX'   # Sponser Identifier: Code identifying a party or other code (Min 2, Max 80)
    n1_sponsor_segment = generate_N1(N1_PLAN_SPONSOR_CODE, sponser_name, N1_FEDERAL_ID_NUMBER, sponsor_id_number)
    print(f"N1_SPONSOR: {n1_sponsor_segment}")
    ## payer segment
    insurer_id_code = 'XXXX'
    n1_payer_segment = generate_N1(N1_INSURER_CODE, provider_name, N1_FEDERAL_ID_NUMBER, insurer_id_code)
    print(f"N1_PAYER: {n1_payer_segment}")
    for _, enrollee in enrollee_group.iterrows():
        # print(f"Enrollee: {enrollee[FIRST_NAME_COL]} {enrollee[LAST_NAME_COL]}")

        # Generate Ins Segment for Enrollee
        enrollee_medicare_status_code = enrollee['MedicarePlanCode']
        if enrollee['MedicareReasonCode'] != '':
            enrollee_medicare_status_code = str(enrollee_medicare_status_code) + '>' + str(int(enrollee['MedicareReasonCode']))
        ins_seg_array = [
            'INS',                                  # Segment Name
            'Y',                                    # Member Indicator (Y/N)
            '18',                                   # Individual Relationship Code
            '030',                                  # Maintenance Type Code
            str(enrollee['ReasonCode']),            # Maintenance Reason Code
            str(enrollee['BenefitStatusCode']),     # Benefit Status Code
            str(enrollee_medicare_status_code),     # Medicare Status Code
            '',                                     # Consolidated Omnibus Budget Reconciliation Act (COBRA) Qualifying Event Code
            str(enrollee['EmployeeStatus']),        # Employment Status Code
            '',                             # Student Status Code
            '',                             # Handicap Indicator
            'D8',                           # Date Time Period Format Qualifier
            '',                             # Member Individual Death Date
            'U',                            # Confidentiality Code (R: Restricted Access, U: Unrestricted Access)
            '',                             # Birth Sequence Number (Min 1, Max 9)
        ]

        enrollee_ins_segment = generate_segment_from_array(ins_seg_array)
        print(f"Enrollee Ins Segment: {enrollee_ins_segment}")


        # REF Segments (Subscriber Identifier)
        ref_seg_array = [
            'REF',                                      # Segment Name
            '0F',                                       # Reference Identification Qualifier
            str(enrollee['EmployeeId'])                 # Subscriber Identifier
        ]
        enrollee_ref_segment = generate_segment_from_array(ref_seg_array)
        print(f"Enrollee REF Segment: {enrollee_ref_segment}")
        # REF Segments (Member Policy Number) --- Optional
        ref_seg_array = [
            'REF',                                      # Segment Name
            '1L',                                       # Reference Identification Qualifier
            str(enrollee['SocialSecurityNumber'])       # Member Group or Policy Number
        ]
        enrollee_ref_segment = generate_segment_from_array(ref_seg_array)
        print(f"Member Policy Number: {enrollee_ref_segment}")


        enrollee_dependents = dependents[dependents[EMPLOYEE_ID_COL] == enrollee[EMPLOYEE_ID_COL]]

        for _, dependent in enrollee_dependents.iterrows():
            print(f"\tDependent: {dependent[FIRST_NAME_COL]} {dependent[LAST_NAME_COL]}")
