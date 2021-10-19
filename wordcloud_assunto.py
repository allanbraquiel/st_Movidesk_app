from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from appMovidesk import df

# Transformando a coluna assunto em uma lista
df_assunto = df["Assunto"].tolist()

# Transformando a lista em uma unica string
all_assunto = " ".join(s for s in df_assunto)

# Adicionando elementos ao StopWords
stopwords = set(STOPWORDS)
stopwords.update(["o", "do", "da", "de", "ao", "os", "as", "https", "dos", "se", "em", "na", "é", "e", "t", "co"])

mask = np.array(Image.open("images/bandeira-do-brasil.png"))

# gerar o wordcloud
wordcloud = WordCloud(stopwords=stopwords,
                      background_color="white",
                      width=1600, height=1200,
                      mask=mask)

wordcloud.generate(all_assunto)

# tamanho do gráfico
plt.figure(figsize=(20, 15))
# plotagem da nuvem de palavras
plt.imshow(wordcloud, interpolation='bilinear')
# remove as bordas
plt.axis('off')
# mostra a word cloud
# plt.show()
# Salva a figura
plt.savefig("images/wordcloud.png", dpi=300)
