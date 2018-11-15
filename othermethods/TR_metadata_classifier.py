bank_codes = ['M:8','M:I','M:QF', # Central bank
            'N2:IMF','M:Q', # IMF
            'M:Y','P:4296937871','N2:FED','N2:F1', # Federal Reserve
            'N2:1'] # Interest Rates

politics_codes = ['M:2', 'M:4','M:9','M:B','M:C','M:G','M:N','M:R','M:T','M:X',
'M:AJ','M:DF','M:DU','M:E9','M:EG','M:EI','M:EL','M:EM','M:EQ','M:F7','M:LK','M:M0',
'M:MW','M:MX','M:MY','M:MZ','M:N4','M:N5','M:N6','M:N8','M:N9','M:NX','M:RA','M:RB',
'M:RC','M:RD','M:1P3','M:1R7','M:1SJ','M:1U0','M:1V6','M:1V7','M:1V8','M:1W4','M:1W8',
'P:1000314762','P:1000314702','P:1000339175','P:1000314708','P:1000314701','P:1000314821',
'P:400266','P:1000314703','P:1000314713','P:1000314761','P:1000314696','P:1000318127',
'P:1001097640','P:1000314845','P:1000314704','P:1000314706','P:1000314710','P:1000314711',
'P:1000314712','P:1000339176','P:1000314794','P:1000314759','P:1000339177','P:1000339178',
'P:1000339179','P:1000314718','P:1000314720','P:1000314721','P:1000314722','P:1000314724',
'P:1000314725','P:1000314733','P:1000314697','P:1000314698','P:1000314699','P:1000314700',
'P:1002115542','P:1000487182','P:1003534517','N2:WAR','N2:IMM','N2:VIO','N2:DEF','N2:DIP',
'N2:VOTE','N2:POL','N2:TRD','N2:LAW','N2:TAX','N2:WASH','N2:CVN','N2:INTAG','N2:GFIN',
'N2:TRF','N2:SDS','N2:CWP','N2:AID','N2:WELF','N2:BOMB','N2:SECUR','N2:HRGT','N2:NGO',
'N2:HUMA','N2:ADVO','N2:NUCL','N2:WRM','N2:CIV','N2:CENS','N2:DAT','N2:DEFBUY',
'N2:INSURG','N2:VOTP','N2:VOTS','N2:VOTH','N2:VOTG','N2:BRU','N2:POTUS','N2:BRI',
'N2:LRIGHV','N2:TERRO','N2:ISISR','N2:TERRO1','N2:HRIGHT','N2:HRIGHV',
'N2:G0','N2:TRUMP','N2:OBOR']

def bank_filter(labels):
    """
    labels: a list or set of Reuters codes
    True if at least one of the labels are about banks, IMF, FED, interest rates
    """
    if len(set(bank_codes)&set(labels)) > 0:
        return True
    else:
        return False

def politics_filter(labels):
    """
    labels: a list or set of Reuters codes
    True if at least one of the labels are about politics
    """
    if len(set(politics_codes)&set(labels)) > 0:
        return True
    else:
        return False
