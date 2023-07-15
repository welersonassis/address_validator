import re
import logging
import time
from tqdm import tqdm
import pandas as pd
from thefuzz import fuzz
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="basic.log"
)

# Define a dictionary of replacements
street_replacements = {
    'AL ':'',
    'ALM ':'',
    'AV ':'',
    'AVN ':'',
    'BRIG ':'',
    'CAP ':'',
    'CEL ':'',
    'DES ':'',
    'DEP ':'',
    'DR ':'',
    'DRA ':'',
    'EST ':'',
    'ESTR ':'',
    'ENG ':'',
    'GEN ':'',
    'GOV ':'',
    'MAJ ':'',
    'MAL ':'',
    'MIN ':'',
    'PC ':'',
    'PREF ':'',
    'PRES ':'',
    'PROF ':'',
    'PROFA ':'',
    'R ':'',
    'ROD ':'',
    'S ':'',
    'SD ':'',
    'SEN ':'',
    'SGT ':'',
    'SR ':'',
    'SRA ':'',
    'ST ':'',
    'STA ':'',
    'STO ':'',
    'TEN ':'',
    'TV ': '',
    'TR ':'',
    'TRAV ':'',
    'VER ':'',
    'VISC ':'',
    'VL ':'',
    'CS ':'',
    'QD ':'',
    'LT ':'',
    'LOT ':'',
    'APT ':'',
    'AL.':'',
    'ALM.':'',
    'AV.':'',
    'AVN.':'',
    'BRIG.':'',
    'CAP.':'',
    'CEL.':'',
    'DES.':'',
    'DEP.':'',
    'DR.':'',
    'DRA.':'',
    'EST.':'',
    'ESTR.':'',
    'ENG.':'',
    'GEN.':'',
    'GOV.':'',
    'MAJ.':'',
    'MAL.':'',
    'MIN.':'',
    'PC.':'',
    'PREF.':'',
    'PRES.':'',
    'PROF.':'',
    'PROFA.':'',
    'R.':'',
    'ROD.':'',
    'S.':'',
    'SD.':'',
    'SEN.':'',
    'SGT.':'',
    'SR.':'',
    'SRA.':'',
    'ST.':'',
    'STA.':'',
    'STO.':'',
    'TEN.':'',
    'TV.': '',
    'TR.':'',
    'TRAV.':'',
    'VER.':'',
    'VISC.':'',
    'VL.':'',
    'CS.':'',
    'QD.':'',
    'LT.':'',
    'LOT.':'',
    'APT.':'',
    'RUA':'',
    'AVENIDA':'',
    'ALAMEDA':'',
    'TRAVESSA':'',
    'CORONEL':'',
    'DOUTOR':'',
    'DOUTORA':'',
    'GENERAL':'',
    'VISCONDE':'',
    'PRESIDENTE':'',
    'RODOVIA':'',
    'ENGENHEIRO':'',
    'ENGENHEIRA':'',
    'PROFESSOR':'',
    'PROFESSORA':'',
    'SENADOR':'',
    'SENADORA':'',
    'ESTRADA':'',
    'ALMIRANTE': '',
    'BRIGADEIRO': '',
    'CAPITAO': '',
    'DESEMBARGADOR': '',
    'DONA': '',
    'DEPUTADA': '',
    'DEPUTADO': '',
    'ENGEN': '',
    'GOVERNADOR': '',
    'MAJOR': '',
    'MARECHAL': '',
    'MINISTRA': '',
    'PRACA': '',
    'PREFEITA': '',
    'SAO': '',
    'SOLDADO': '',
    'SARGENTO': '',
    'SENHOR': '',
    'SENHORA': '',
    'SETOR': '',
    'SANTA': '',
    'SANTO': '',
    'TENENTE': '',
    'VEREADORA': '',
    'VILA': '',
    'CASA': '',
    'QUADRA': '',
    'LOTE': '',
    'APARTAMENTO': '',
    'CONDOMINIO': ''
}

# Create a regex pattern from the keys of the replacements dictionary
pattern = re.compile("|".join(map(re.escape, street_replacements.keys())))


def has_number(string):
    pattern = r'\d+'  # Match one or more digits
    match = re.search(pattern, string)
    return bool(match)



if __name__ == '__main__':
    df = pd.read_excel('./base_proporcional_mercado_50000.xlsx')
    df_dict = df.to_dict('records')
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.get('https://buscacepinter.correios.com.br/app/endereco/index.php')
    
    for row in tqdm(df_dict):
        score = 0
        mail_neighborhood_score = 0
        mail_street_score = 0
        try:
            # Input address
            input_zip = str(row['zip_code'])
            input_street = unidecode(str(row['address'])).upper()
            input_street = pattern.sub(lambda match: street_replacements[match.group(0)], input_street)
            input_street = input_street.strip()
            input_number = row['number']
            input_neighborhood = unidecode(str(row['quarter'])).upper()
            input_city = unidecode(row['city']).upper()
            input_state = unidecode(row['state_code']).upper()
            input_zip = input_zip.zfill(8)
            zip_search = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.NAME, "endereco"))) 
            zip_search.send_keys(input_zip)
            zip_search.send_keys(Keys.ENTER)
            # get mail address
            element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'td[data-th="Logradouro/Nome"]'))) 
            mail_street_raw = unidecode(element.text).upper()
            if '-' in mail_street_raw:
                mail_street = mail_street.split('-')[0]
            if ',' in mail_street_raw:
                mail_street = mail_street.split(',')[0]
            else:
                mail_street = mail_street_raw
            mail_street = pattern.sub(lambda match: street_replacements[match.group(0)], mail_street).strip()
            mail_street = mail_street.strip()
            element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'td[data-th="Bairro/Distrito"]'))) 
            mail_neighborhood = unidecode(element.text).upper()
            element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'td[data-th="Localidade/UF"]'))) 
            tmp = element.text
            mail_city = unidecode(tmp.split('/')[0]).upper()
            mail_state = unidecode(tmp.split('/')[1]).upper()
            element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'td[data-th="CEP"]')))
            mail_zip = (element.text).replace('-','')
            if mail_street and mail_neighborhood and mail_city and mail_state and mail_zip: 
                #ESTADO
                if input_state == mail_state:
                    score += 5   
                #CIDADE
                if  input_city == mail_city:
                    score += 5       
                #BAIRRO
                mail_neighborhood_score = fuzz.token_sort_ratio(input_neighborhood,mail_neighborhood)
                if mail_neighborhood_score >= 80:
                    score += 10            
                #RUA
                mail_street_score = fuzz.token_sort_ratio(mail_street,input_street)
                if  mail_street_score >= 80:
                    score += 20 
                #CEP  
                if input_zip[:5] == mail_zip[:5]:  
                    score += 20

                row['CORREIOS_OUTPUT'] = mail_street_raw+' , '+mail_neighborhood+' , '+mail_city+' , '+mail_state+' , '+mail_zip

                if score >= 50:
                    row['AUTO_CORREIOS'] = 'SIM'

            elif mail_street and mail_city and mail_state and mail_zip:
                #ESTADO
                if input_state == mail_state:
                    score += 20
                #CIDADE
                if  input_city == mail_city:
                    score += 5
                #RUA
                mail_street_score = fuzz.token_sort_ratio(mail_street,input_street)
                if  mail_street_score >= 80:
                    score += 5  
                #CEP  
                if input_zip[:5] == mail_zip[:5]:  
                    score += 20

                row['CORREIOS_OUTPUT'] = mail_street_raw+' , '+mail_city+' , '+mail_state+' , '+mail_zip

                if score == 50:
                    df_dict['AUTO_CORREIOS'] = 'SIM'
            else:
                row['AUTO_CORREIOS'] = 'NÃO'

            new_search = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'btn_nbusca')))
            new_search.click()

        except Exception as error:
                element = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, 'mensagem-resultado-alerta')))
                alert = element.text
                if alert == 'Dados não encontrado':
                    row['AUTO_CORREIOS'] = 'NÃO'
                new_search = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'btn_nbusca')))
                new_search.click()
  

    df = pd.DataFrame(df_dict)
    df.to_excel('base_50k_rotulada.xlsx', index=False)
