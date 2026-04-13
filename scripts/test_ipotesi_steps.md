# Test delle Ipotesi

Abbiamo in esame 9 stati europei, Italia compresa. 
Austria, Germania, Danimarca, Spagna, Finlandia, Francia, Norvegia, Svezia.

Il lasso temporale che consideriamo è 2017-2021.

Avendo acquisito dati categorici rilevati da ISTAT e Eurostat il test più idoneo per analizzare le frequenze è il *Chi Quadrato*. 

## STEP 1: Formulazione dell'Ipotesi Nulla e Alternativa

**$H_0$ = ISTAT ed Eurostat hanno la stessa distribuzione percentuale dei flussi nei 5 anni 2017–2021.**

**$H_1$ = ISTAT ed Eurostat non hanno la stessa distribuzione percentuale dei flussi nei 5 anni 2017–2021.**

Pur avendo livelli diversi, i due sistemi raccontano lo stesso andamento nel tempo?

## STEP 2: Livello di significatività $\alpha$

Questo significa che accettiamo un rischio del 5% di rifiutare l’ipotesi nulla quando in realtà è vera.

## STEP 3: Determinare i gradi di libertà e i valori critici

Dato che confrontiamo le distribuzioni su 5 anni ($k = 5$), i gradi di libertà ($gdl$) si calcolano come:
$$gdl = (k - 1) = 4$$

Consultando le tavole della distribuzione Chi Quadrato con un livello di significatività $\alpha = 0,05$ e $gdl = 4$, il valore critico è:
$$\chi^2_{\text{critico}} = 9,49$$

## STEP 4: Calcolare la statistica $\chi^2$

In questo test, verifichiamo se la distribuzione di ISTAT si discosta significativamente dal modello di riferimento rappresentato da Eurostat.

*   **Frequenze Osservate ($O_i$):** Sono i flussi reali registrati da **ISTAT**. Rappresentano il campione che vogliamo testare per vedere se *segue* l'andamento dei paesi di destinazione.
*   **Frequenze Attese ($E_i$):** Sono i valori che ci aspetteremmo di trovare nei dati ISTAT se l'ipotesi nulla fosse vera. Poiché assumiamo che **Eurostat** rifletta la reale distribuzione temporale dei flussi, usiamo le sue percentuali annue per calcolare quanto ISTAT *dovrebbe* aver registrato per ogni anno:
    $$E_i = \text{Totale ISTAT} \times \frac{\text{Eurostat}_i}{\text{Totale Eurostat}}$$

La formula per calcolare il valore del test è:
$$\chi^2 = \sum_{i=1}^{k} \frac{(O_i - E_i)^2}{E_i}$$

Se il $\chi^2$ calcolato è basso, significa che ISTAT, pur sottostimando i volumi, segue l'andamento temporale dettato dai dati Eurostat.

## STEP 5: Accettazione o rifiuto dell'ipotesi nulla

Si confronta il valore della statistica $\chi^2$ calcolato con il valore critico:

*   **Se $\chi^2_{\text{calcolato}} > 9,49$**: Si rifiuta l'ipotesi nulla $H_0$. Esiste una differenza statisticamente significativa nella distribuzione temporale dei flussi tra i due sistemi.
*   **Se $\chi^2_{\text{calcolato}} \leq 9,49$**: Non si può rifiutare l'ipotesi nulla $H_0$. Le differenze riscontrate sono imputabili al caso e i due sistemi, pur avendo volumi diversi, descrivono lo stesso andamento temporale.