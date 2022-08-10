import pandas as pd

def add_user_interaction(tag, question):
    df = pd.DataFrame([
        [tag,question]
    ],
    columns=['predicted_tag', 'question_asked']
    )

    df.to_csv(r'user_interaction.csv', mode = 'a', header = False, index = False, sep=';')