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


def first_standard(address):
    tmp = unidecode(address[1].strip())
    if len(tmp.split('-')) == 3: 
        maps_number = (tmp.split('-')[0]).strip()+' '+(tmp.split('-')[1]).strip()
        maps_neighborhood = (tmp.split('-')[2]).strip()
        tmp2 = unidecode(address[2].strip())
        maps_city = (tmp2.split('-')[0]).strip()
        maps_state = (tmp2.split('-')[1]).strip()  
        maps_zip = (address[3].strip()).replace('-','')
        maps_street = unidecode(address[0])
        maps_street = pattern.sub(lambda match: street_replacements[match.group(0)], maps_street)
        maps_street = maps_street.strip()

        return maps_state, maps_city, maps_neighborhood, maps_street, maps_number, maps_zip

    else:
        tmp1 = unidecode(address[1].strip())
        maps_number = (tmp1.split('-')[0]).strip()
        maps_neighborhood = (tmp1.split('-')[1]).strip()

        tmp2 = unidecode(address[2].strip())
        maps_city = (tmp2.split('-')[0]).strip()
        maps_state = (tmp2.split('-')[1]).strip()                
        maps_zip = (address[3].strip()).replace('-','') if len(address) == 4 else ''
        maps_street = unidecode(address[0])
        maps_street = pattern.sub(lambda match: street_replacements[match.group(0)], maps_street)
        maps_street = maps_street.strip()

        return maps_state, maps_city, maps_neighborhood, maps_street, maps_number, maps_zip
    

def second_standard(address):
    tmp = unidecode(address[1].strip())
    if len(tmp.split('-')) == 2: 
        maps_number = (tmp.split('-')[0]).strip()
        maps_city = (tmp.split('-')[1]).strip()
        maps_state = unidecode(address[2].strip())
        maps_zip = (address[3].strip()).replace('-','')
        maps_street = unidecode(address[0])
        maps_street = pattern.sub(lambda match: street_replacements[match.group(0)], maps_street)
        maps_street = maps_street.strip()
        maps_neighborhood = ''

        return maps_state, maps_city, maps_neighborhood, maps_street, maps_number, maps_zip
    else:
        maps_number = (tmp.split('-')[0]).strip()+' '+(tmp.split('-')[1]).strip()
        maps_neighborhood = (tmp.split('-')[2]).strip()
        tmp2 = unidecode(address[2].strip())
        maps_city = (tmp2.split('-')[0]).strip()
        maps_state = (tmp2.split('-')[1]).strip()  
        maps_zip = (address[3].strip()).replace('-','')
        maps_street = unidecode(address[0])
        maps_street = pattern.sub(lambda match: street_replacements[match.group(0)], maps_street)
        maps_street = maps_street.strip()

        return maps_state, maps_city, maps_neighborhood, maps_street, maps_number, maps_zip
    

def third_standard(address):
    tmp = unidecode(address[2].strip())
    maps_city = (tmp.split('-')[0]).strip()
    maps_state = (tmp.split('-')[1]).strip()
    maps_zip = (address[3].strip()).replace('-','')
    maps_street = unidecode(address[0])
    maps_street = pattern.sub(lambda match: street_replacements[match.group(0)], maps_street)
    maps_street = maps_street.strip()
    maps_number = unidecode(address[1].strip())

    return maps_state, maps_city, maps_street, maps_number, maps_zip


if __name__ == '__main__':
    df = pd.read_excel('./base_proporcional_mercado_50000.xlsx')
    df_dict = df.to_dict('records')
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)

    for row in tqdm(df_dict[:100]):
        # start_time = time.time()
        score = 0
        street_score = 0
        neighborhood_score = 0
        driver.get('https://www.google.com/')
        # Input address
        input_zip = str(row['zip_code'])
        input_street = unidecode(str(row['address'])).upper()
        input_number = str(int(row['number']))
        input_neighborhood = unidecode(str(row['quarter'])).upper()
        input_city = unidecode(str(row['city'])).upper()
        input_state = unidecode(str(row['state_code'])).upper()
        input_zip = str(input_zip).zfill(8)

        input_maps = input_street+' '+input_number+', '+input_neighborhood+', '+input_zip+', '+input_city+', '+input_state

        input_street = pattern.sub(lambda match: street_replacements[match.group(0)], input_street)
        input_street = input_street.strip()
        # end_time = time.time()
        # logging.info(f'INPUT: {end_time - start_time}') 
        # OUTPUT
        # start_time = time.time()
        output = ''
        maps_zip = ''
        maps_number = ''
        maps_street = ''
        maps_city = ''
        maps_state = ''
        maps_neighborhood = ''


        # Selenium
        # Wait for the search input field to be visible
        search_input = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.NAME, "q"))) 
        search_input.send_keys(input_maps)
        search_input.send_keys(Keys.ENTER)
        #Maps
        # Locate the maps_ bar element
        maps__bar = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Maps')]")))
        # Perform a click action on the maps_ bar
        actions = ActionChains(driver)
        actions.click(maps__bar).perform()        
        # end_time = time.time()
        # logging.info(f'SEARCH: {end_time - start_time}') 
        try:
            # start_time = time.time()
            time.sleep(2)
            element = driver.find_element(By.CLASS_NAME, 'DkEaL')
            output = unidecode(element.text)
            maps_split = (output.upper()).split(',')

            if  len(maps_split) == 1:
                element = driver.find_element(By.CLASS_NAME, 'rogA2c ')
                output = unidecode(element.text)
                maps_split = (output.upper()).split(',')
            if len(maps_split) > 3:
                if '-' in maps_split[1] and '-' in maps_split[2]:
                    maps_state, maps_city, maps_neighborhood, maps_street, maps_number, maps_zip = first_standard(maps_split)
                elif '-' in maps_split[1]:
                    maps_state, maps_city, maps_neighborhood, maps_street, maps_number, maps_zip = second_standard(maps_split)
                elif '-' in maps_split[2]:
                    maps_state, maps_city, maps_street, maps_number, maps_zip = third_standard(maps_split)
            elif len(maps_split) > 2:
                if '-' in maps_split[1] and '-' in maps_split[2]:
                    maps_state, maps_city, maps_neighborhood, maps_street, maps_number, maps_zip = first_standard(maps_split)
            # end_time = time.time()
            # logging.info(f'1 TRY: {end_time - start_time}') 
        except NoSuchElementException:
            # start_time = time.time()
            time.sleep(2)
            try:
                search_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'searchbox-searchbutton')))
                search_button.click()
                first_element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'hfpxzc')))
                first_element.click()
                element = driver.find_element(By.CLASS_NAME, 'DkEaL')
                output = unidecode(element.text)
                maps_split = (output.upper()).split(',')

                if  len(maps_split) == 1:
                    element = driver.find_element(By.CLASS_NAME, 'rogA2c ')
                    output = unidecode(element.text)
                    maps_split = (output.upper()).split(',')

                if len(maps_split) > 3:
                    if '-' in maps_split[1] and '-' in maps_split[2]:
                        maps_state, maps_city, maps_neighborhood, maps_street, maps_number, maps_zip = first_standard(maps_split)
                    elif '-' in maps_split[1]:
                        maps_state, maps_city, maps_neighborhood, maps_street, maps_number, maps_zip = second_standard(maps_split)
                    elif '-' in maps_split[2]:
                        maps_state, maps_city, maps_street, maps_number, maps_zip = third_standard(maps_split)
                # end_time = time.time()
                # logging.info(f'2 TRY: {end_time - start_time}') 
            except StaleElementReferenceException:
                    continue    
            except NoSuchElementException:
                # start_time = time.time()
                time.sleep(2)
                try:
                    element = driver.find_element(By.CLASS_NAME, 'DkEaL')
                    output = unidecode(element.text)
                    maps_split = (output.upper()).split(',')

                    if  len(maps_split) == 1:
                        element = driver.find_element(By.CLASS_NAME, 'rogA2c ')
                        output = unidecode(element.text)
                        maps_split = (output.upper()).split(',')

                    if len(maps_split) > 3:
                        if '-' in maps_split[1] and '-' in maps_split[2]:
                            maps_state, maps_city, maps_neighborhood, maps_street, maps_number, maps_zip = first_standard(maps_split)
                        elif '-' in maps_split[1]:
                            maps_state, maps_city, maps_neighborhood, maps_street, maps_number, maps_zip = second_standard(maps_split)
                        elif '-' in maps_split[2]:
                            maps_state, maps_city, maps_street, maps_number, maps_zip = third_standard(maps_split)
                    # end_time = time.time()
                    # logging.info(f'3 TRY: {end_time - start_time}') 
                except WebDriverException:
                    continue
                except:
                    continue


            except WebDriverException:
                continue
        
        if output:
            row['MAPS_OUTPUT'] = output


        if maps_state and maps_city and maps_neighborhood and maps_street and maps_number and maps_zip:
            # start_time = time.time()
            #ESTADO
            if input_state == maps_state:
                score += 10
            #CIDADE
            if  input_city == maps_city:
                score += 10
            #BAIRRO
            neighborhood_score = fuzz.token_sort_ratio(input_neighborhood,maps_neighborhood)
            if neighborhood_score >= 80:
                score += 10
            #RUA
            street_score = fuzz.token_sort_ratio(maps_street, input_street)
            if  street_score >= 80:
                score += 10 
            #NUMERO
            if  input_number == maps_number:
                score += 10
            #CEP 
            #TODO range    
            if input_zip[:5] == maps_zip[:5]:
                score += 10
            # end_time = time.time()
            # logging.info(f'1 IF: {end_time - start_time}') 
        elif maps_state and maps_city and maps_street and maps_number and maps_zip:
            # start_time = time.time()
            #ESTADO
            if input_state == maps_state:
                score += 10
            #CIDADE
            if  input_city == maps_city:
                score += 10
            #RUA
            street_score = fuzz.token_sort_ratio(maps_street, input_street)
            if  street_score >= 80:
                score += 10 
            #NUMERO
            if  input_number == maps_number:
                score += 10
            #CEP 
            #TODO range    
            if input_zip[:5] == maps_zip[:5]:
                score += 10
            # end_time = time.time()
            # logging.info(f'2 IF: {end_time - start_time}') 
        elif maps_state and maps_city and maps_neighborhood and maps_street and maps_number:
            # start_time = time.time()
            #ESTADO
            if input_state == maps_state:
                score += 10
            #CIDADE
            if  input_city == maps_city:
                score += 10
            #BAIRRO
            neighborhood_score = fuzz.token_sort_ratio(input_neighborhood,maps_neighborhood)
            if neighborhood_score >= 80:
                score += 10
            #RUA
            street_score = fuzz.token_sort_ratio(maps_street, input_street)
            if  street_score >= 80:
                score += 10 
            #NUMERO
            if  input_number == maps_number:
                score += 10
            # end_time = time.time()
            # logging.info(f'3 IF: {end_time - start_time}') 
        if score >= 50:
            row['AUTO_MAPS'] = 'SIM'  


        df = pd.DataFrame(df_dict)
        df.to_excel('base_50k_rotulada_test.xlsx', index=False)   