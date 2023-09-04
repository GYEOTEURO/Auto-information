import pandas as pd

def saveCsv(file_name, sites, regions, categories, disabilityTypes, titles, dates, contents, contentLinks, images):
    df = pd.read_csv(f'result/format.csv', encoding='utf-8')

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
        

    df.to_csv(f'result/crawl/{file_name}.csv', mode='a', header=False, encoding='utf-8')
