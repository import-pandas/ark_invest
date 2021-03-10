import requests
import io
import pandas as pd
from datetime import datetime as dt
from os import listdir
from os.path import isfile, join

#declare csv location urls
urls = ['https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv',
        'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS.csv',
        'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_GENOMIC_REVOLUTION_MULTISECTOR_ETF_ARKG_HOLDINGS.csv',
        'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_AUTONOMOUS_TECHNOLOGY_&_ROBOTICS_ETF_ARKQ_HOLDINGS.csv',
        'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS.csv',
        'https://ark-funds.com/wp-content/fundsiteliterature/csv/THE_3D_PRINTING_ETF_PRNT_HOLDINGS.csv']

#get all directories where data resides
def get_all_paths():
    child_path = ['innovation/', 'internet/', 'genomic/', 'autonomous/', 'fintech/', '3d/']
    paths = [f'data/{x}' for x in child_path]

    return paths

#convert csv url to df
def url_to_temp(target_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    url_data = requests.get(target_url, headers=headers).content
    df = pd.read_csv(io.StringIO(url_data.decode('utf-8')))
    #ark files have two blank lines followed by a line with string. remove these
    df.drop(df.tail(3).index, inplace=True)
    
    return df

def save_temp_dfs():
    data_directories = get_all_paths()
    url_to_temp(urls[0]).to_csv(f'{data_directories[0]}temp.csv')
    url_to_temp(urls[1]).to_csv(f'{data_directories[1]}temp.csv')
    url_to_temp(urls[2]).to_csv(f'{data_directories[2]}temp.csv')
    url_to_temp(urls[3]).to_csv(f'{data_directories[3]}temp.csv')
    url_to_temp(urls[4]).to_csv(f'{data_directories[4]}temp.csv')
    url_to_temp(urls[5]).to_csv(f'{data_directories[5]}temp.csv')

#sort contents of directory
def sort_directory(target_directory):
    sorted_directory = sorted(listdir(target_directory), reverse = True)

    return sorted_directory

#get temp or previous confirmed csv
def get_csv(target_directory, target_file):
    if target_file == 'temp':
        df = pd.read_csv(target_directory + 'temp.csv')
    elif target_file == 'previous':
        df = pd.read_csv(target_directory + sort_directory(target_directory)[1])
    else:
        print('Invalid csv target')
    
    return df

#compare temp csv to latest confirmed df. check if new file or duplicate
def compare_temp_prev_files(temp_df, previous_df):
    temp_df_date = temp_df.date.max()
    temp_df_fund = temp_df.fund.unique().tolist()[0]

    previous_df_date = previous_df.date.max()
    previous_df_fund = previous_df.fund.unique().tolist()[0]

    if (temp_df_date == previous_df_date) and (temp_df_fund == previous_df_fund):
        print(' >>> CAUTION: Duplicate import detected!\n')

        return 0

    elif (temp_df_date == previous_df_date) and (temp_df_fund != previous_df_fund):
        print(' >>> CAUTION: Fund names do not match. Are you in the right directory?\n')

        return 0

    elif (temp_df_date != previous_df_date) and (temp_df_fund == previous_df_fund):
        print(' >>> Incoming file OK to import\n')

        return 1

    else:
        print(' >>> CAUTION: Fund names do not match & Dates do not match. Are you in the right directory?\n')

        return 0

#run through files, compare, assemble queue for further analysis or exit
def import_report(directory_list):
    confirmations = []
    print('ARK_INNOVATION_ETF:')
    confirmations.append(compare_temp_prev_files(get_csv(directory_list[0], 'temp'), get_csv(directory_list[0], 'previous')))
    print('NEXT_GENERATION_INTERNET_ETF:')
    confirmations.append(compare_temp_prev_files(get_csv(directory_list[1], 'temp'), get_csv(directory_list[1], 'previous')))
    print('GENOMIC_REVOLUTION_MULTISECTOR_ETF:')
    confirmations.append(compare_temp_prev_files(get_csv(directory_list[2], 'temp'), get_csv(directory_list[2], 'previous')))
    print('AUTONOMOUS_TECHNOLOGY_&_ROBOTICS_ETF:')
    confirmations.append(compare_temp_prev_files(get_csv(directory_list[3], 'temp'), get_csv(directory_list[3], 'previous')))
    print('FINTECH_INNOVATION_ETF:')
    confirmations.append(compare_temp_prev_files(get_csv(directory_list[4], 'temp'), get_csv(directory_list[4], 'previous')))
    print('3D_PRINTING_ETF:')
    confirmations.append(compare_temp_prev_files(get_csv(directory_list[5], 'temp'), get_csv(directory_list[5], 'previous')))

    index = 0
    queue = []
    for confirmation in confirmations:
        #if new file then save as date stamped csv
        if confirmation == 1:
            temp_df = pd.read_csv(f'{get_all_paths()[index]}temp.csv')
            temp_df.to_csv(f'{get_all_paths()[index]}{dt.today().strftime("%Y-%m-%d")}.csv')
            print(f'>>>{dt.today().strftime("%Y-%m-%d")}.csv SAVED to {get_all_paths()[index]}')
            queue.append(get_all_paths()[index])
            index += 1
        #if old file or error then pass 
        else:
            print(f'No file saved to {get_all_paths()[index]}')
            index += 1
    #evaluate queue directories. if queue then continue else exit
    if len(queue) == 0:
        print('\nNo further analysis, exiting...')
        exit()

    else:
        print('\nNew files detected and saved. Proceeding to analysis...')
        return queue

#check which companies have been added or removed for single etf
def allocation_check(previous_company_dict, current_company_dict):
    output = ''
    for x, y in previous_company_dict.items():
        if x in current_company_dict:
            pass
        else:
            output += (f'>>> ${y} was REMOVED')

    for x, y in current_company_dict.items():
        if x in previous_company_dict:
            pass
        else:
            output += (f'>>> ${y} was ADDED')

    return output

#compare latest two files for additions and removals within each etf
def compare_files(queue):
    paths = queue
    output = []
    for x in paths:
        df_current = pd.read_csv(x + sort_directory(x)[1])
        df_previous = pd.read_csv(x + sort_directory(x)[2])
        fund = df_current.fund.unique()[0]
        curr_company_dict = dict(zip(df_current.company, df_current.ticker))
        prev_company_dict = dict(zip(df_previous.company, df_previous.ticker))
        if sorted(curr_company_dict) == sorted(prev_company_dict):
            output.append(f'{x.split("/")[1].upper()} ETF( ${fund} ): current allocation and previous allocation is EQUAL')
        else:
            output.append(f'{x.split("/")[1].upper()} ETF( ${fund} ): current allocation and previous allocation is DIFFERENT!')
            output.append(allocation_check(prev_company_dict, curr_company_dict))

    return output

#gather full paths and file names for dataframe load
def get_full_files(queue):
    paths = queue

    full_files = []

    for path in paths:
        only_files = [f for f in listdir(path) if isfile(join(path, f))]
        files = []
        for file in only_files:
            files.append(f'{path}{file}')

        full_files.append(files)

    return full_files

#create dataframe from multiple files of the same fund/directory
def create_df(file_list):
    combine = []

    for file in file_list:
        if 'temp.csv' not in file:
            df = pd.read_csv(file)
            combine.append(df)
        else:
            pass

    out = pd.concat(combine, ignore_index=True, axis=0)

    return out

#create list of dataframes for each fund
def create_df_list(full_file_list):
    out = []

    for file_list in full_file_list:
        df = create_df(file_list)
        out.append(df)

    return out

#for each company calculate changes in holdings by taking the most recent 2 reports
def get_gains(df_in):
    combine = []

    for company in df_in.company.unique().tolist():
        df = df_in[df_in.company == company].sort_values(by='date').tail(2).copy()
        df['shares_change(%)'] = df['shares'].pct_change()
        df['shares_change(%)'] = df['shares_change(%)'] * 100
        df['weight_change(%)'] = df['weight(%)'].diff()
        combine.append(df)

    out = pd.concat(combine, ignore_index=True, axis=0)

    return out

#needs to handle partial file ok to import!!!
def change_report(queue):
    df_list = create_df_list(get_full_files(queue))

    innovation = get_gains(df_list[0])
    internet = get_gains(df_list[1])
    genomic = get_gains(df_list[2])
    autonomous = get_gains(df_list[3])
    fintech = get_gains(df_list[4])
    _3d = get_gains(df_list[5])

    return innovation, internet, genomic, autonomous, fintech, _3d


#get highlights from an ETF given an add_remove_threshold
def get_highlights(df, add_remove_threshold):
    add_df = df[(df['shares_change(%)'] >= add_remove_threshold) & ~(df.ticker.isnull())].copy()
    remove_df = df[(df['shares_change(%)'] <= -add_remove_threshold) & ~(df.ticker.isnull())].copy()
    if add_df.ticker.nunique() > 0:
        add_tickers = add_df.ticker.tolist()
        add_change = [int(x) for x in add_df['shares_change(%)'].tolist()]
    else:
        add_tickers = []
        add_change = []
    if remove_df.ticker.nunique() > 0:
        remove_tickers = remove_df.ticker.tolist()
        remove_change = [int(x) for x in remove_df['shares_change(%)'].tolist()]
    else:
        remove_tickers = []
        remove_change = []

    return add_tickers, add_change, remove_tickers, remove_change

#generate %change summary
def change_summary(highlights, etf_name):
    prefix = f'@ARKInvest {etf_name}: '
    output = ''
    if len(highlights[0]) > 0:
        counter = 0
        for ticker in highlights[0]:
            output += (f'${ticker} +{highlights[1][counter]}%, ')
            counter += 1
    else:
        pass

    if len(highlights[2]) > 0:
        counter = 0
        for ticker in highlights[2]:
            output += (f'${ticker} {highlights[3][counter]}%, ')
            counter += 1
    else:
        pass

    if len(output) > 0:
        return prefix + output[:-2]
    else:
        return prefix + 'No significant changes'

def change_highlight_output(change_report, change_threshold):
    innovation = change_summary(get_highlights(change_report[0], change_threshold), 'Innovation ETF( $ARKK )')
    internet = change_summary(get_highlights(change_report[1], change_threshold), 'Internet ETF( $ARKW )')
    genomic = change_summary(get_highlights(change_report[2], change_threshold), 'Genomic ETF( $ARKG )')
    autonomous = change_summary(get_highlights(change_report[3], change_threshold), 'Autonomous ETF( $ARKQ )')
    fintech = change_summary(get_highlights(change_report[4], change_threshold), 'Fintech ETF( $ARKF )')
    _3d = change_summary(get_highlights(change_report[5], change_threshold), '3D ETF( $PRNT )')

    output = [innovation, internet, genomic, autonomous, fintech, _3d]

    return output

#quick functions
def import_status():
    save_temp_dfs()
    import_report(get_all_paths())

def allocation():
    [print(x) for x in compare_files(get_all_paths())]

def changes(significance):
    [print(x) for x in change_highlight_output(change_report(get_all_paths()), significance)]

def all_dfs():
    output = []
    for x in change_report(get_all_paths()):
        output.append(x.dropna())

    return output