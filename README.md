# Cheeh model
## Installation
```sh
pip install -r requirements.txt
```

## Run
Run command from folder ``sub_app``
```sh
bokeh serve vir_load_test.py
```

### Run Cheeh model
#### Run GUI 
```sh
python -m app.main
```
#### Run cmdline
```sh
python -m app.main -c path_to_city_config -m path_to_model_config -v path_to_virus_config
```

### Usage GUI
1) Put all parameters by writing boxes or loading parameters from config files
2) Click button **Run!**
3) If you want graph in *log* click checkbox **Log**
4) If you want to stop execution of modelling then press button **Stop!**
5) To clear cell with graph press button **Clear graph**
6) To save config press button **Save config**

### Description

#### Infection step
![infection_step](https://user-images.githubusercontent.com/45848690/200599822-de503862-dd5d-4cac-9eac-f0f9993ca8f7.PNG)


1) Когда здоровый человек контактирует с инфицированным, то он получает от него некоторую заражающую дозу (*giving infecting fraction*), которая зависит от:
* `degreeInteraction` -- степень их взаимодействия
  * `home`
    * `parent with child` -- взаимодействие детей с родителями : `degreeInteraction=80`
    * `pair` -- взаимодействие родителей друг с другом : `degreeInteraction=50`
  * `work`
    * `small group` -- тесный круг общения с коллегами : `degreeInteraction=50`
    * `big group` -- весь офис / целый класс / ... : `degreeInteraction=20`
  * `random`: `degreeInteraction=10`
* `infectingFraction(infectedPerson)` -- заражающая доза инфицированного человека
* `specificImmun(contactPerson)` -- специфический(к заданному вирусу) иммунитет здорового человека
$$givingInfectingFraction = degreeInteraction * (\frac{infectingFraction(infectedPerson)}{R}) \cdot (1 - specificImmun(contactPerson))$$

2) После чего полученная заражающая доля аккумулируется с тем, что он накопил при контакте с другими инфицированными людьми
$$infectingFraction(contactPerson) = infectingFraction(contactPerson) + givingInfectingFraction$$

3) если в некоторый момент в течении дня *infectingFraction* здорового человека станет больше `VIRAL_THRESHOLD`, то человек считается инфицированным. Если человек не заболел, то к началу следующего дня его *infectingFraction* обнуляется


#### Changes in infection state
Аналогично как в [covasim](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1009149)

*Состояния и переходы:*

![img](https://journals.plos.org/ploscompbiol/article/figure/image?size=large&id=10.1371/journal.pcbi.1009149.g001)


*Вероятности переходов:*

![img](https://journals.plos.org/ploscompbiol/article/figure/image?size=large&id=10.1371/journal.pcbi.1009149.t002)



*Время пребывания в каждом из состояний:*

![img](https://journals.plos.org/ploscompbiol/article/figure/image?size=large&id=10.1371/journal.pcbi.1009149.t001)

При этом, когда человек болеет его заражающая доля меняется следующим образом:

$$infectingFraction_t = infectingFraction_{t - 1}\cdot (1 + virusSpreadRate) \cdot (1 - (\frac{specificImmun_t} {\frac{\pi}{2}})) \cdot (1 - nonSpecificImmun)$$

а специфический иммунитет:

$$specificImmun_{t > lag}=\arctan{(N_{t-lag}\cdot \alpha + specificImmun_{t-1})},~where~~ \alpha = \frac{Beta(a, b)}{1000}$$

## Help
Issues and question -> Telegram: IvanKozlov98 or this repository in section "Issues".
