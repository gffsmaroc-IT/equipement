import pandas as pd
import glob
import os
import re

def normalize_existence(val):
    val = str(val).lower().strip()
    if val in ['oui', 'o', '1', 'on', 'yes']:
        return 'O'
    elif val in ['non', 'n', '0', 'no', 'n/a', 'na', 'nan', '']:
        return 'N'
    return val

def normalize_status(val):
    val = str(val).lower().strip()
    if val in ['nan', 'none', '', 'n/a']:
        return ''
    
    operational_keywords = ['bien', 'marche', 'ok', 'fonctionnel', 'fonctionnelle', 'normal', 'opérationnel', 'bon', 'etat']
    broken_keywords = ['panne', 'cassé', 'ne fonctionnent pas', 'non fonctionnelle', 'hors service', 'infonctionnel', 'mal', 'arret', 'non']
    degraded_keywords = ['mauvais', 'instable', 'moyen', 'dégradé', 'intermittent', 'bloquage', 'bloque', 'parfois']
    
    # Check for "not working" phrases first
    if 'pas' in val or 'non' in val or 'ne fonctionnent' in val:
        return 'En Panne'
        
    for kw in broken_keywords:
        if kw in val:
            return 'En Panne'
            
    for kw in degraded_keywords:
        if kw in val:
            return 'Dégradé'

    for kw in operational_keywords:
        if kw in val:
            return 'Opérationnel'
            
    return val

def process_dashboard_data():
    input_files = glob.glob("*Global_Equipment_Data_Styled*.csv")
    output_dir = "Updated_Dashboard_Files"
    os.makedirs(output_dir, exist_ok=True)

    for file_path in input_files:
        try:
            raw_data = pd.read_csv(file_path, header=None, dtype=str).fillna('')
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
            
        # Locate the header row containing 'Description'
        header_row_idx = -1
        for i, row in raw_data.iterrows():
            row_values = [str(x).strip() for x in row]
            if 'Description' in row_values:
                header_row_idx = i
                break
                
        if header_row_idx == -1:
            continue
            
        # Clean restaurant name for the target format
        file_name_clean = os.path.basename(file_path).split(' - ')[-1].replace('.csv', '').strip()
        restaurant_name = file_name_clean.replace('Etat équipement IT 2026', '').strip() + " BK"
            
        df = raw_data.iloc[header_row_idx+1:].copy()
        formatted_data = []
        current_category = ""
        
        for _, row in df.iterrows():
            col0 = str(row[0]).strip().replace(' :', '')
            desc = str(row[1]).strip()
            
            # Skip empty description rows
            if not desc:
                continue
                
            # Update current category if a new one is specified in the first column
            if col0:
                current_category = col0
                
            cat = current_category
            if 'Bureau' in cat: cat = 'Bureau'
            elif 'POS' in cat: cat = 'POS'
            elif 'Imprimantes' in cat: cat = 'Imprimantes'
            elif 'KDS' in cat: cat = 'KDS'
            elif 'DMB' in cat: cat = 'DMB'
            elif 'HD' in cat: cat = 'HD'
            
            existance = normalize_existence(row[2])
            marque = str(row[3]).strip()
            modele = str(row[4]).strip()
            etat = normalize_status(row[5])
            remarque = str(row[6]).strip()
            
            formatted_data.append([cat, desc, existance, marque, modele, etat, remarque])
            
        out_df = pd.DataFrame(formatted_data, columns=[
            'Catégorie', 'Description', 'Existance O/N', 'Marque', 
            'Modèle (a remplir par IT)', 'Etat de mise en marche', 'Remarque'
        ])
        
        output_filename = os.path.join(output_dir, f"DASHBOARD EQUIPEMENT IT - {restaurant_name.upper()}.csv")
        
        with open(output_filename, 'w', encoding='utf-8-sig') as f:
            f.write(f"{restaurant_name.upper()},,,,,,\n")
            f.write(",,,,,,\n")
            f.write(",,,,,,\n")
            out_df.to_csv(f, index=False, lineterminator='\n')

if __name__ == "__main__":
    process_dashboard_data()