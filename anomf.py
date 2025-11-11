# anomf.py
import re

def zamien_numery_telefonow(text):
    wzorzec = r'\d{3}[- ]?\d{3}[- ]?\d{3}'
    tnr = {}
    i = 0  
    def zamien(nr):
        nonlocal i
        nr=re.sub("[- ]","",nr)
        if nr not in tnr:
            tnr[nr] = f"nr telefonu{i}"
            i+=1
        return tnr[nr]
    wynik = re.sub(wzorzec, lambda m: zamien(m.group(0)), text)   
    return wynik

def zamien_adresy_mail(text):
    wzorzec = r'\S*@\S*\.\S*'
    tnr = {}
    i = 0  
    def zamien(mail):
        nonlocal i
        if mail not in tnr:
            tnr[mail] = f"mail{i}"
            i+=1
        return tnr[mail]
    wynik = re.sub(wzorzec, lambda m: zamien(m.group(0)), text)   
    return wynik

def zamien_osoby(text):
    wzorzec = r'[A-ZĆŁŃŚŻŹ][a-zążźćęóńł]+ [A-ZĆŁŃŚŻŹ][a-zążźćęóńł]+'
    tnr = {}
    i = 0  
    def zamien(osoba):
        nonlocal i
        if osoba not in tnr:
            tnr[osoba] = f"osoba{i}"
            i+=1
        return tnr[osoba]
    wynik = re.sub(wzorzec, lambda m: zamien(m.group(0)), text)   
    return wynik

def zamien_kwoty(text):
    wzorzec = r'\d+[.,]\d{2}zł'
    tnr = {}
    i = 0  
    def zamien(kwota):
        nonlocal i
        if kwota not in tnr:
            tnr[kwota] = f"kwota{i}"
            i+=1
        return tnr[kwota]
    wynik = re.sub(wzorzec, lambda m: zamien(m.group(0)), text)   
    return wynik

def zamien_daty(text):
    wzorzec = r'\d{2}[.-]\d{2}[.-]\d{4}'
    tnr = {}
    i = 0  
    def zamien(data):
        nonlocal i
        if data not in tnr:
            tnr[data] = f"data{i}"
            i+=1
        return tnr[data]
    wynik = re.sub(wzorzec, lambda m: zamien(m.group(0)), text)   
    return wynik

def zamien_numery_kont(text):
    wzorzec = r'\d{2}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}'
    tnr = {}
    i = 0  
    def zamien(nrk):
        nonlocal i
        nrk=re.sub("[- ]","",nrk)
        if nrk not in tnr:
            tnr[nrk] = f"nr konta{i}"
            i+=1
        return tnr[nrk]
    wynik = re.sub(wzorzec, lambda m: zamien(m.group(0)), text)   
    return wynik

def anonimizacja(text,tel=True,mail=True,kwot=True,date=True, osob=True):
    wynik=text
    if tel:
        wynik=zamien_numery_telefonow(wynik)
    if mail:
        wynik=zamien_adresy_mail(wynik)
    if kwot:
        wynik=zamien_kwoty(wynik)
    if date:
        wynik=zamien_daty(wynik)
    if osob:
        wynik=zamien_osoby(wynik)
    return wynik

