from postgres import Module, my_session
import pandas as pd


all_modules = my_session.query(Module)

for module in all_modules:
    name = module.module_name.replace('Wahlfach ', '')
    name = name.replace('Wahlfach: ', '')

    question1 = f'Wann habe ich {name}?'
    question2 = f'Wann habe ich heute {name}?'
    question3 = f'Wann habe ich morgen {name}?'
    question4 = f'Wann habe ich diese Woche {name}?'
    question5 = f'Habe ich diese Woche {name}?'

    df = pd.DataFrame([
        [name, question1],
        [name, question2],
        [name, question3],
        [name, question4],
        [name, question5]
    ],
    columns= ['tags', 'patterns']
    )

    df.to_csv(r'training_data.csv', mode = 'a', header = False, index = False, sep=';')