import pandas as pd

path_folder = '/home/shinmg/2022barrier-free/autoInformation/Auto-information/result/'

def saveCsv(file_name, sites, regions, categories, disabilityTypes, titles, dates, contents, contentLinks, images):
    df = pd.read_csv(f'{path_folder}format.csv', encoding='utf-8')
    df.to_csv(f'{path_folder}crawl/{file_name}.csv', mode='w', encoding='utf-8')

    df['site'] = sites
    df['region'] = regions
    df['category'] = categories
    df['disability_type'] = disabilityTypes
    df['title'] = titles
    df['date'] = dates
    df['content'] = contents
    df['original_link'] = contentLinks
    df['content_link'] = contentLinks
    df['image'] = images
        

    df.to_csv(f'{path_folder}crawl/{file_name}.csv', mode='a', header=False, encoding='utf-8')
