# Importing libraries:
import streamlit as st
import json
import os
import re
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from web_app_functions import *

# Page formatting :
st.title('Scrapping user page')
st.sidebar.title('Menu')

if st.sidebar.checkbox('Run scrapping'):

    st.markdown('## Scrapping setting')

    st.write(
        "afficher les main category qu'on veut scrap, les cocher et faire un bouton go")
    st.write("Which categories do you want to scrap?")

    with open('urls_extractor/urls_extractor/spiders/urls.json', 'r') as file:
        categories_to_get = json.load(file)
    categories = []
    for cat in categories_to_get:
        for key, value in cat.items():
            category = value.split('/')[4]
            categories.append(category)
    categories = list(set(categories))

    for cat in categories:
        st.checkbox(cat)

    if st.button("Scrap"):
        st.markdown('Start scraping on selected categories')

    if st.button("Scrap all"):
        st.markdown('Scrapping on going')
        with open('urls_extractor/urls_extractor/spiders/urls.json', 'r') as file:
            datas = json.load(file)

        urls_to_scrap = []

        for data in datas:
            for key, value in data.items():
                urls_to_scrap.append(value)

        u = urls_to_scrap[0:3]

        results = urls_scrapped(u)
        scraping = results[0]
        urls_processed = results[1]
        st.markdown(f'last urls scrapped : {results[1]}')
        st.markdown('Do you want to save?')
        if st.button("Yes!"):
            json__saving(scraping)


elif st.sidebar.checkbox('Benchmark visualisation'):

    path_to_json = 'scrapings/'

    dataframes = {}
    requests_saved = []
    max_deepness = []

    files_name = os.listdir(path_to_json)

    for file in files_name:
        full_path = os.path.join(path_to_json, file)
        if os.path.isfile(full_path):
            with open(full_path, 'r') as myfile:
                datas = json.load(myfile)

                for data in datas:

                    max_depth = find_nested_depth(data)
                    max_deepness.append(max_depth)
                    max_max_deepness = max(max_deepness)
                    all_branches = find_branches(data, 1, max_depth)
                    for branches in all_branches:
                        req = "data"
                        title = str()
                        requests = str()
                        for branch in branches.split('\\'):
                            req += f"['{branch}']"
                            title += branch + ' '
                            requests += f"['{branch}']"
                        result = eval(req)
                        requests_saved.append(requests)

                        variable_name = f"df_{file}_{req}"

                        dataframes[variable_name] = pd.DataFrame(result)

    requests_saved_cleaned = list(set(requests_saved))
    requests_saved_cleaned_list = [chain_to_list(
        request) for request in requests_saved_cleaned]
    # ICI JE DOIS REGARDER LA LONGEUR DE TOUTE LES LISTES ET CREE OPTION I DE LA TAILLE DE LA PLUS ONGUE LISTE

    my_final_request = []

    # Create a dropdown menu with selectbox method
    first_layer = []
    for req in requests_saved_cleaned_list:
        first_layer.append(req[0])
    first_layer = set(first_layer)

    option1 = st.selectbox(
        'Choose an option',
        (first_layer)
    )

    my_final_request.append(option1)

    second_layer = []
    for req in requests_saved_cleaned_list:
        if req[0] == option1:
            second_layer.append(req[1])
    second_layer = set(second_layer)
    option2 = st.selectbox(
        'Choose an option',
        (second_layer)
    )
    my_final_request.append(option2)

    third_layer = []
    for req in requests_saved_cleaned_list:
        if req[0] == "Circular Light Bulbs & Lamps":
            if req[1] == "Circular Lamps":
                third_layer.append(req[2])
    third_layer = set(third_layer)
    option3 = st.selectbox(
        'Choose an option',
        (third_layer)
    )
    my_final_request.append(option3)

    my_final_request_chain = list_to_chain(my_final_request)

    modele_regex = r"df_\d{4}-\d{2}-\d{2}_mon_fichier\.json_data" + \
        re.escape(my_final_request_chain)

    cles_trouvees = []

    for cle in dataframes.keys():

        if re.match(modele_regex, cle):
            cles_trouvees.append(cle)

    print("Clés correspondantes au modèle regex :")
    dataframes_to_concat = []
    for cle_trouvee in cles_trouvees:
        print(cle_trouvee)
        dataframes_to_concat.append(dataframes[cle_trouvee])

    df_concatene = pd.concat(dataframes_to_concat, ignore_index=True)

    # In order to thing the same items, I attribute them a Ref number. If the items is the same, everything but price and date has to be the same
    colonnes_a_exclure = ['Date', 'Price']

    df_concatene['Ref'] = df_concatene.groupby(
        [colonne for colonne in df_concatene.columns if colonne not in colonnes_a_exclure]).ngroup()
    df_concatene.sort_values(by=['Ref'], inplace=True)

    fig, axes = plt.subplots(
        nrows=(max(df_concatene['Ref']) // 2) + 1, ncols=2, figsize=(15, 15))
    fig.suptitle(my_final_request_chain.replace("[", "").replace(
        "]", "").replace("''", " ").replace("'", ""), fontsize=16)
    for i, ax in enumerate(axes.flat):
        if i < max(df_concatene['Ref']):
            df = df_concatene[df_concatene['Ref'] == i]
            ax.plot(df['Date'], df['Price'], color='blue', linestyle='-')
            ax.scatter(x=df['Date'], y=df['Price'])
            ax.set_xlabel('Date')
            ax.set_ylabel('Price')

            first_row_values = df_concatene.drop(
                columns=['Date', 'Price']).iloc[0].values
            string_first_row = ', '.join(map(str, first_row_values))
            ax.set_title(string_first_row, fontsize=11)

    plt.tight_layout()

    st.pyplot(fig)

    '''# Display the selected option
    st.write('You selected:', option)
                        
    # Create lists to store data for each level
    lists_by_depth = [[] for _ in range(max_max_deepness)]

    for file in files_name:
        full_path = os.path.join(path_to_json, file)
        if os.path.isfile(full_path):
            with open(full_path, 'r') as myfile:
                datas = json.load(myfile)

                for data in datas:
                    max_depth = find_nested_depth(data)
                    all_branches = find_branches(data, 1, max_depth)

                    # Populate lists_by_depth with data from all_branches
                    for i in range(len(all_branches)):
                        branch = all_branches[i]
                        branch_parts = branch.strip('[').strip(']').split('][')
                        for j in range(len(branch_parts)):
                            part = branch_parts[j].strip("'")
                            lists_by_depth[j].append(part)

    for reqst in requests_saved_cleaned:
        print(reqst)

    main = []
    second = []
    third = []

    for req in requests_saved_cleaned[0].strip('[').strip(']').split('][') :
        req_splitted = req.strip("'")
        main.append(req_splitted[0])
        second.append(req_splitted[1])
        third.append(req_splitted[2])


    requests_saved_cleaned = list(set(requests_saved))

    for request in requests_saved_cleaned:
        modele_regex = r"df_\d{4}-\d{2}-\d{2}_mon_fichier\.json_data" + re.escape(request)

        cles_trouvees = []

        # Parcours des clés du dictionnaire
        for cle in dataframes.keys():
            # Vérification si la clé correspond au modèle regex
            if re.match(modele_regex, cle):
                cles_trouvees.append(cle)

        dataframes_to_concat = []

        for cle_trouvee in cles_trouvees:
            dataframes_to_concat.append(dataframes[cle_trouvee])

        df_concatene = pd.concat(dataframes_to_concat, ignore_index=True)
        
        colonnes_a_exclure = ['Date', 'Price']

        df_concatene['Ref'] = df_concatene.groupby([colonne for colonne in df_concatene.columns if colonne not in colonnes_a_exclure]).ngroup()
        df_concatene.sort_values(by=['Ref'], inplace=True)
        

        fig, axes = plt.subplots(nrows=(max(df_concatene['Ref']) // 2) + 1, ncols=2, figsize=(15, 15))
        fig.suptitle(request.replace("[", "").replace("]", "").replace("''", " ").replace("'", ""), fontsize=16)
        for i, ax in enumerate(axes.flat):
            if i < max(df_concatene['Ref']):
                df = df_concatene[df_concatene['Ref'] == i]
                ax.plot(df['Date'], df['Price'], color='blue', linestyle='-')  
                ax.scatter(x=df['Date'], y=df['Price'])
                ax.set_xlabel('Date')
                ax.set_ylabel('Price')
                
                first_row_values = df_concatene.drop(columns=['Date', 'Price']).iloc[0].values
                string_first_row = ', '.join(map(str, first_row_values))
                ax.set_title(string_first_row, fontsize = 11)

        plt.tight_layout()
        plt.show()'''
