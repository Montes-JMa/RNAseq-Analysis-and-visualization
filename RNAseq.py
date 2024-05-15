import pandas as pd
import numpy as np

def filter_data(DF,pth,FCth):
    """Esta función deberia de poder filtrarnos los DataFrames de acuerdo a umbrales/threshold
    y nos deberia de regresar los datos significativos y datos no significativos.
    
    Parametros:
    DF: Es un PandasDataFrame 
    pth(pvalue threshold): Debe ser un float
    FCth(FoldChange threshold): Debe ser un float"""
    lgpth = -1 * np.log10(pth)
    
    DF["plog"] = np.log10(DF["padj"]) * -1
    status = DF[DF["Status"].isin(["UP", "DOWN"])]
    
    uplc = status[status["log2FoldChange"] > FCth]   #Mayor a FC
    lwlc = status[status["log2FoldChange"] < -FCth]  #Menor a FC
    lc = pd.concat([uplc,lwlc])
    
    ns1lc = status[status["log2FoldChange"] < FCth]   #Menor a FC
    ns2lc = ns1lc[ns1lc["log2FoldChange"] > -FCth]  #Mayor a FC
    
    sigp = lc[lc["plog"] > lgpth ]   #Se pone mayor  porque con el p ajustado 
    nsigp = lc[lc["plog"] < lgpth ]   #Tenemos que cambiar el signo
    none = DF[DF["Status"] =="None"]
       
    nsig =pd.concat([ns2lc,nsigp,none])
    
    return sigp, nsig


def up_down(DF,tsv=None):
    """Lo que hace esta funcion es darnos una lista de los genes que se expresaron
    de manera diferencial UP o DOWN, pero el DF debe ser ya filtrado o sea tu le metes
    los datos significativos, la funcion te da lista de cuales fueron UP cuales DOWN
    tambien si hay genes repetidos, nos da el ensemble ID
    """
    #Saquemos los nombres de los UP y LOW
    up_df = DF[DF["Status"] == "UP"]
    up = up_df["external_gene_name"]
    
    lw_df = DF[DF["Status"] == "DOWN"]
    lw = lw_df["external_gene_name"]
    
    #Creamos el diccionario de nombres UP
    nup = {}                         
    for i in range(len(up)):
        nup[up[i]] = up.index[i] 
    
    #Creamos el diccionario de nombres LOW
    nlw = {}
    for i in range(len(lw)):
        nlw[lw[i]] = lw.index[i] 
    
    #Veamos si alguno se repite en los UP
    x = np.unique(np.array(list(nup.keys())),return_counts=True) #Vemos los unicos y su cuenta
    mensajeup = []
    for i in range(len(x[1])):
        if x[1][i]!= 1:   #Si la cuenta es mayor a 1 entonces dinos cual se repite y su ID
            mensajeup.append("El gen UP "+ str(x[0][i])+ "esta repetido "+str(x[1][i])+" veces")
            a=" "
            for i in list(qq[qq["Gene names"]==str(x[0][i])].EnsambleID):
                a += i+" " 
            mensajeup.append('\x1b[1m' +"Con ensemble ID" + a + '\033[0m'+ "\n")
    
    for i in mensajeup: #Imprimelo para que el usuario sepa chido lo que hace
        print(i)
    
    #Veamos si en los LOW alguno se repite 
    y = np.unique(np.array(list(nlw.keys())),return_counts=True)
    mensajelw = []
    for i in range(len(y[1])):
        if y[1][i] != 1:
            mensajelw.append("El gen LOW "+ str(y[0][i])+"esta repetido "+str(y[1][i])+" veces \n")
            a=" "
            for i in list(qq[qq["Gene names"]==str(y[0][i])].EnsambleID):
                a += i+" " 
            mensajelw.append('\x1b[1m' +"Con ensemble ID" + a + '\033[0m'+ "\n")
    for i in mensajelw:
        print(i)
    
    return nup,nlw

def repetidos(tsv,n=8,eid=0,):
    """
    La funcion deberia de darte un PandasDataFrame con los nombres de los genes repetidos
    y con su respectivo ensemble ID
    Parametros:
    tsv: string  de forma name.tsv
    n: numero de la columna que contiene los nombres
    eid: numero de columna que contiene los ensemble id
    """
    
    #Cargamos la columnas de los nombres y de los ID
    names = np.genfromtxt(tsv, delimiter='\t',skip_header=1,usecols=n,dtype='str') 
    ensembleid = np.genfromtxt(tsv, delimiter='\t',skip_header=1,usecols=eid,dtype='str') 
    
    #Buscamos los genes unicos y cuanto se repiten cada uno
    gen_unique = np.unique(names, return_inverse = True,return_counts = True)                     
    #Los nombres de los que se repiten
    gen_rep = gen_unique[0][np.where(gen_unique[-1] == 2)[0]] 

    gen_rep2 = []                                      #Como los genes se repiten hagamos una lista de repetidos
    for i in gen_rep:                                  #Funcionara para un dataframe
        gen_rep2.append(i)
        gen_rep2.append(i) 

    ensemble_id = []
    for i in gen_rep:                                  #Para cada gen
        for j in np.where(names == i)[0]:              #Ubica donde estan en las tablas
            ensemble_id.append(ensembleid[j:j+1][0])   #Agreguemos a la lista el id de ensemble

    zelda = []
    for i in ensemble_id:                              #Es para buscar rapido keske
        zelda.append("https://www.ensembl.org/Human/Search/Results?q="+ str(i) +";site=ensembl;facet_species=Human")
    
    pre_rep ={"Gene names":gen_rep2,            #Creamos el diccionario
         "EnsambleID":ensemble_id,
         "Información":zelda}
    info_repetidos = pd.DataFrame(pre_rep)      #Creamos el Pandas DataFrame
    
    return info_repetidos

