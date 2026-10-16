# Loterias — Análise Honesta

Uma central offline para as loterias da Caixa (Mega-Sena, Lotofácil, Quina, Dupla Sena,
Super Sete, Dia de Sorte, +Milionária, Timemania e Loteca) que faz o **oposto** dos apps
que prometem "números certos": usa estatística real sobre o histórico oficial para mostrar
que **nenhum padrão prevê o resultado**.

> ⚠️ Nenhuma análise aumenta a chance de ganhar. Cada aposta tem a mesma chance, sempre.
> O projeto só ajuda a evitar **dividir** o prêmio (combinações pouco jogadas) e a organizar
> um cupom. Jogue por diversão, com responsabilidade.

## O que faz

- **Gerador** de jogos por loteria, respeitando as regras de cada uma.
- **Análise estatística** (qui-quadrado de uniformidade e teste de independência) com gráfico
  e grade de frequências — tudo rodando no navegador, sem internet.
- **Loteca**: tratada como futebol (distribuição histórica de 1/X/2, com o "fator casa").
- **Cupom**: some jogos de várias loterias, veja o custo total e **imprima ou baixe** para
  levar à lotérica. Preços de aposta editáveis na própria página.

## Como usar

- **Recomendado:** abra pelo atalho **"Loterias"** (Área de Trabalho). Ele sobe um servidor
  local (`servidor.py`), abre a página no navegador e faz o botão **"🔄 Atualizar resultados"**
  (topo da página) funcionar. Mantenha a janela aberta enquanto usa; feche para encerrar.
- Também dá para abrir o `Loterias.html` direto (offline); nesse modo o botão de atualizar
  não funciona (o navegador bloqueia a busca na Caixa por CORS), então use o servidor ou:
  ```
  python atualizar.py        # baixa só os concursos novos e regenera a página
  python download_all.py     # (re)baixa o histórico completo
  ```

> Nota: a API da Caixa não envia cabeçalhos CORS, por isso a atualização é feita pelo Python
> (servidor local), nunca pelo navegador diretamente.

## Como é feito

- **Front-end:** um único HTML com CSS e JavaScript puro (sem frameworks nem bibliotecas).
  O qui-quadrado é implementado na mão (função gama incompleta).
- **Coleta/atualização:** Python (`urllib`, `concurrent.futures`) consumindo a API pública
  do Portal de Loterias da Caixa.

## Estrutura

```
template.html       # página-modelo (contém __DATA_JSON__, substituído na montagem)
servidor.py         # servidor local; abre a página e serve o endpoint /atualizar
atualizar.py        # baixa só os concursos novos e regenera Loterias.html
download_all.py     # baixa o histórico completo (uso pontual / primeira carga)
assemble.py         # injeta os dados no template e grava Loterias.html
validate.js         # testa o JS de todas as loterias num DOM simulado (Node)
loteria.ico         # ícone do atalho
*.json              # cache do histórico de cada loteria
```

## Dados

Fonte: API oficial da Caixa (`servicebus2.caixa.gov.br/portaldeloterias/api/<loteria>`).
É pública mas não documentada; se mudar, ajuste a extração em `download_all.py`/`atualizar.py`.

## Aviso

Projeto pessoal, para estudo e entretenimento. Não tem vínculo com a Caixa.
Se o jogo virar problema: 0800 611 0911 (Jogadores Anônimos).
