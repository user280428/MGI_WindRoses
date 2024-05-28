import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from reg import regions, months




# Список вариантов, городов, и частей ссылок на парсер метеорологии





"""
    Функция скачивания каждой страницы для каждого варианта
"""

def downloader():
    # Если не существуют нужные папки, то создает их
    if not os.path.isdir('pages'):
        os.mkdir('pages')
    if len(os.listdir('pages/')) == 0:
        for n in range(1, 31):
            os.mkdir(f'pages/{n}. {list(regions.values())[n-1][0]}')

    # Заголовки для запроса
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'}
    # Куки для запроса
    cookies = {'Cookie': 'PHPSESSID=h6mlu6nf0rcfauor4tk38i8107; autocity=4368; selector_args=%7B%22region%22%3A%22477%22%2C%22country%22%3A%22156%22%2C%22distr%22%3A%22314%22%2C%22city%22%3A%224720%22%2C%22month%22%3Anull%2C%22year%22%3Anull%7D; af_lpdid=38964:4749; _ga=GA1.2.750992000.1712558009; _gid=GA1.2.1554870860.1712558009; _gat=1'}
    # Двойной цикл который пробегается по каждому варианту и по каждому месяцу внутри варианта и скачивает html файлы для каждого месяца
    for n in regions.keys():
        for i in range(1, 13):
            url = f'https://www.gismeteo.ru/diary{regions[n][1]}{i}/'
            src = requests.get(url, headers=headers, cookies=cookies)
            with open(f'pages/{n}. {list(regions.values())[n-1][0]}/{list(regions.values())[n-1][0]}___page_{i}.html', 'w', encoding='utf-8') as page:
                page.write(src.text)
            print(f'{n}. {list(regions.values())[n-1][0]} page_{i}.html has downloaded')





'''
    Функция парсящая html файлы 
'''
def parser_pictures():
    # Пробегается по директориям и составляет пути к файлам
    var_list = os.listdir('pages')
    for var in var_list:
        page_list = os.listdir(f'pages/{var}')
        dict = {}

        '''
            Большой блок, который извлекает из страниц информацию и соберает их в DataFrame
        '''

        for page in page_list:
            month = page.split('_')[-1][:-5]
            with open(f'pages/{var}/{page}', 'r', encoding='utf-8') as p:
                page_text = p.read()
            dict[month] = []
            soup = BeautifulSoup(page_text, "html.parser")
            lst = soup.find('div', id="data_block").find('table').find('tbody').find_all('span')
            for i in range(0, len(lst), 2):
                if len(lst[i].text.split()) > 1:
                    dir = lst[i].text.split()[0]
                    speed = lst[i].text.split()[1].strip('м/с')
                elif len(lst[i].text.split()) == 1:
                    dir = lst[i].text
                    speed = 0
                day = int((i + 2) / 2)
                daily_dict = {}
                daily_dict[day] = [dir, speed]
                dict[month].append(daily_dict)

            dt = {}
            for month in dict:
                dt[month] = {}
                for day in dict[month]:
                    day_num = list(day.keys())[0]
                    for day_info in day.values():
                        dir = day_info[0]
                        speed = int(day_info[1])
                        if dir not in dt[month]:
                            dt[month][dir] = []
                        dt[month][dir].append(speed)

            final_dict = {}
            c = 0
            a = 0
            for month in dt:
                final_dict[month] = {}
                for dirs in dt[month]:
                    count = len(dt[month][dirs])
                    avg = round(sum(dt[month][dirs]) / count, 1)
                    if dirs not in final_dict[month]:
                        final_dict[month][dirs] = [count, avg]
                    c += count
                    a += count * avg

            df = pd.DataFrame.from_dict(final_dict, orient='index')

            final_dict['year'] = {}
            for col in df.columns:
                final_dict['year'][col] = []
                c = 0
                a = 0
                for i in df.index:
                    if isinstance(df[col][i], list):
                        c += df[col][i][0]
                        a += df[col][i][0] * df[col][i][1]
                a = round(a / c, 1)
                final_dict['year'][col].append(c)
                final_dict['year'][col].append(a)

                df = pd.DataFrame.from_dict(final_dict, orient='index')

                '''
                    Конец блока
                '''
                # Если нет какого то из столбцов в df, то добавляет его
                di = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
                for d in di:
                    if d not in df:
                        df[d] = np.nan

                '''
                    Блок формирование DataFrame которая послужит исходными данными для 
                '''

                df_speed = df[['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']]
                df_speed = df_speed.fillna(0)
                df_speed = df_speed.map(lambda x: [0, 0] if x == 0 else x)
                df_speed = df_speed.map(lambda x: x[1])
                df_speed = df_speed.reindex(
                    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'year']
                )

                '''
                    Конец блока
                '''


                # Создание нужных папок
                if not os.path.isdir('pics'):
                    os.mkdir('pics')
                if len(os.listdir('pics/')) == 0:
                    for n in range(1, 31):
                        os.mkdir(f'pics/{n}. {list(regions.values())[n-1][0]}')



        '''
            Блок создания картинок
        '''


        for i in range(len(months)):
            month_data = df_speed.iloc[i, :].tolist()
            directions = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
            angles = np.linspace(0, 2 * np.pi, len(directions), endpoint=False)
            fig = plt.figure(figsize=(12, 12))
            ax = fig.add_subplot(111, polar=True)
            ax.plot(angles, month_data, color='r', linewidth=1, label='Количество дней')
            ax.fill(angles, month_data, 'pink', alpha=0.5)
            ax.plot((angles[-1], angles[0]), (month_data[-1], month_data[0]), color='r', linewidth=1)
            ax.set_theta_direction(-1)
            ax.set_theta_offset(np.pi / 2)
            ax.set_xticks(angles)
            # ax.set_ylim(0, max(df_speed.max()) + 1)
            ax.set_xticklabels([f'{dir}' for dir in directions], fontsize=12)
            ax.grid(True, which='major', linestyle='--')
            ax.set_title(f'{months[i]}', loc='center')
            plt.savefig(f'pics/{var}/{var} {months[i]}.png')
            plt.close()
            print(f'{var} {months[i]}.png has printed')
        '''
            Конец блока
        '''



def main():
    downloader()
    parser_pictures()




if __name__ == '__main__':
    main()