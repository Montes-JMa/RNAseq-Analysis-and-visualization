# Dependencias que utilizamos 
# pip3.9 install pandas dash dash-core-components dash-daq dash-html-components dash-table plotly dash-renderer numpy gprofiler-official dash_bootstrap_components dash-extensions 

#Importemos las librerias que necesitamos

#Estas nos permiten un manejo de los archivos
import base64
import io

# Estas son las que corresponden a dash y plotly 
import dash 
from dash import dcc
from dash import html
import plotly.graph_objs as go
import plotly.express as px
import dash_daq as daq
from dash.dependencies import Input, Output, State
from dash import dash_table
from dash_extensions.snippets import send_data_frame
import dash_bootstrap_components as dbc


#Importamos numpy y pandas para el manejo de DataFrames
import pandas as pd
import numpy as np

#IMportamos para el de enriquecimiento
from gprofiler import GProfiler
gp = GProfiler(return_dataframe=True)


# # Definamos algunas funciones que nos seran de utilidad

# In[2]:


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

# In[3]:


#Vamos a cargar en una lista los organismos con los que puede trabajar gprofile
# =============================================================================
# organismos = pd.read_csv("assets/organismos.csv")
# organismos = [{"label" : organismos["LABEL-2"].values[i]+ " (" + organismos["LABEL-1"].values[i] + ")" , "value" : organismos["LABEL-3"].values[i]} for i in range(len(organismos))]
# =============================================================================
organismos = [{'label': 'Bos mutus (Wild yak)', 'value': 'bmutus'},
 {'label': 'Choloepus hoffmanni (Sloth)', 'value': 'choffmanni'},
 {'label': 'Danio rerio (Zebrafish)', 'value': 'drerio'},
 {'label': 'Ficedula albicollis (Collared flycatcher)',
  'value': 'falbicollis'},
 {'label': 'Canis lupus dingo (Dingo)', 'value': 'cldingo'},
 {'label': 'Struthio camelus australis (African ostrich)',
  'value': 'scaustralis'},
 {'label': 'Callithrix jacchus (Marmoset)', 'value': 'cjacchus'},
 {'label': 'Mus caroli (Ryukyu mouse)', 'value': 'mcaroli'},
 {'label': 'Jaculus jaculus (Lesser Egyptian jerboa)', 'value': 'jjaculus'},
 {'label': 'Poecilia latipinna (Sailfin molly)', 'value': 'platipinna'},
 {'label': 'Ovis aries (Sheep)', 'value': 'oarambouillet'},
 {'label': 'Astyanax mexicanus (Mexican tetra)', 'value': 'amexicanus'},
 {'label': 'Oryctolagus cuniculus (Rabbit)', 'value': 'ocuniculus'},
 {'label': 'Oncorhynchus mykiss (Rainbow trout)', 'value': 'omykiss'},
 {'label': 'Moschus moschiferus (Siberian musk deer)',
  'value': 'mmoschiferus'},
 {'label': 'Canis lupus familiaris (Dog)', 'value': 'clfamiliaris'},
 {'label': 'Amphilophus citrinellus (Midas cichlid)', 'value': 'acitrinellus'},
 {'label': 'Nothobranchius furzeri (Turquoise killifish)',
  'value': 'nfurzeri'},
 {'label': 'Ictidomys tridecemlineatus (Squirrel)',
  'value': 'itridecemlineatus'},
 {'label': 'Scleropages formosus (Asian bonytongue)', 'value': 'sformosus'},
 {'label': 'Homo sapiens (Human)', 'value': 'hsapiens'},
 {'label': 'Salmo salar (Atlantic salmon)', 'value': 'ssalar'},
 {'label': 'Macaca mulatta (Macaque)', 'value': 'mmulatta'},
 {'label': 'Labrus bergylta (Ballan wrasse)', 'value': 'lbergylta'},
 {'label': 'Rhinolophus ferrumequinum (Greater horseshoe bat)',
  'value': 'rferrumequinum'},
 {'label': 'Microcebus murinus (Mouse Lemur)', 'value': 'mmurinus'},
 {'label': 'Tursiops truncatus (Dolphin)', 'value': 'ttruncatus'},
 {'label': 'Anolis carolinensis (Green anole)', 'value': 'acarolinensis'},
 {'label': 'Saimiri boliviensis boliviensis (Bolivian squirrel monkey)',
  'value': 'sbboliviensis'},
 {'label': 'Ciona savignyi (C.savignyi)', 'value': 'csavignyi'},
 {'label': 'Vulpes vulpes (Red fox)', 'value': 'vvulpes'},
 {'label': 'Amphiprion percula (Orange clownfish)', 'value': 'apercula'},
 {'label': 'Anabas testudineus (Climbing perch)', 'value': 'atestudineus'},
 {'label': 'Carlito syrichta (Tarsier)', 'value': 'csyrichta'},
 {'label': 'Sciurus vulgaris (Eurasian red squirrel)', 'value': 'svulgaris'},
 {'label': "Propithecus coquereli (Coquerel's sifaka)", 'value': 'pcoquereli'},
 {'label': 'Capra hircus (Goat)', 'value': 'chircus'},
 {'label': 'Camelus dromedarius (Arabian camel)', 'value': 'cdromedarius'},
 {'label': 'Neolamprologus brichardi (Lyretail cichlid)',
  'value': 'nbrichardi'},
 {'label': 'Nannospalax galili (Upper Galilee mountains blind mole rat)',
  'value': 'ngalili'},
 {'label': 'Cynoglossus semilaevis (Tongue sole)', 'value': 'csemilaevis'},
 {'label': 'Mus pahari (Shrew mouse)', 'value': 'mpahari'},
 {'label': 'Sphenodon punctatus (Tuatara)', 'value': 'spunctatus'},
 {'label': 'Sus scrofa (Pig)', 'value': 'sscrofa'},
 {'label': 'Seriola lalandi dorsalis (Yellowtail amberjack)',
  'value': 'sldorsalis'},
 {'label': "Haplochromis burtoni (Burton's mouthbrooder)",
  'value': 'hburtoni'},
 {'label': 'Parus major (Great Tit)', 'value': 'pmajor'},
 {'label': 'Vombatus ursinus (Common wombat)', 'value': 'vursinus'},
 {'label': 'Oryzias sinensis (Chinese medaka)', 'value': 'osinensis'},
 {'label': 'Betta splendens (Siamese fighting fish)', 'value': 'bsplendens'},
 {'label': 'Astatotilapia calliptera (Eastern happy)', 'value': 'acalliptera'},
 {'label': 'Esox lucius (Northern pike)', 'value': 'elucius'},
 {'label': 'Oryzias latipes (Japanese medaka HdrR)', 'value': 'olatipes'},
 {'label': 'Dipodomys ordii (Kangaroo rat)', 'value': 'dordii'},
 {'label': 'Podarcis muralis (Common wall lizard)', 'value': 'pmuralis'},
 {'label': 'Anas platyrhynchos platyrhynchos (Duck)',
  'value': 'applatyrhynchos'},
 {'label': 'Cyclopterus lumpus (Lumpfish)', 'value': 'clumpus'},
 {'label': 'Notamacropus eugenii (Wallaby)', 'value': 'neugenii'},
 {'label': 'Cricetulus griseus (Chinese hamster CHOK1GS)',
  'value': 'cgchok1gshd'},
 {'label': 'Anser brachyrhynchus (Pink-footed goose)',
  'value': 'abrachyrhynchus'},
 {'label': 'Xenopus tropicalis (Tropical clawed frog)',
  'value': 'xtropicalis'},
 {'label': 'Hippocampus comes (Tiger tail seahorse)', 'value': 'hcomes'},
 {'label': 'Gallus gallus (Chicken)', 'value': 'ggallus'},
 {'label': 'Gopherus evgoodei (Goodes thornscrub tortoise)',
  'value': 'gevgoodei'},
 {'label': 'Latimeria chalumnae (Coelacanth)', 'value': 'lchalumnae'},
 {'label': 'Naja naja (Indian cobra)', 'value': 'nnaja'},
 {'label': 'Cebus imitator (Capuchin)', 'value': 'ccapucinus'},
 {'label': 'Sparus aurata (Gilthead seabream)', 'value': 'saurata'},
 {'label': 'Balaenoptera musculus (Blue whale)', 'value': 'bmusculus'},
 {'label': 'Tupaia belangeri (Tree Shrew)', 'value': 'tbelangeri'},
 {'label': 'Procavia capensis (Hyrax)', 'value': 'pcapensis'},
 {'label': 'Rhinopithecus bieti (Black snub-nosed monkey)', 'value': 'rbieti'},
 {'label': 'Aquila chrysaetos chrysaetos (Golden eagle)',
  'value': 'acchrysaetos'},
 {'label': 'Erpetoichthys calabaricus (Reedfish)', 'value': 'ecalabaricus'},
 {'label': 'Phocoena sinus (Vaquita)', 'value': 'psinus'},
 {'label': 'Heterocephalus glaber (Naked mole-rat female)',
  'value': 'hgfemale'},
 {'label': 'Petromyzon marinus (Lamprey)', 'value': 'pmarinus'},
 {'label': 'Bison bison bison (American bison)', 'value': 'bbbison'},
 {'label': 'Lates calcarifer (Barramundi perch)', 'value': 'lcalcarifer'},
 {'label': 'Cercocebus atys (Sooty mangabey)', 'value': 'catys'},
 {'label': 'Leptobrachium leishanense (Leishan spiny toad)',
  'value': 'lleishanense'},
 {'label': 'Gorilla gorilla gorilla (Gorilla)', 'value': 'ggorilla'},
 {'label': 'Maylandia zebra (Zebra mbuna)', 'value': 'mzebra'},
 {'label': 'Taeniopygia guttata (Zebra finch)', 'value': 'tguttata'},
 {'label': 'Chrysemys picta bellii (Painted turtle)', 'value': 'cpbellii'},
 {'label': 'Erinaceus europaeus (Hedgehog)', 'value': 'eeuropaeus'},
 {'label': 'Crocodylus porosus (Australian saltwater crocodile)',
  'value': 'cporosus'},
 {'label': 'Terrapene carolina triunguis (Three-toed box turtle)',
  'value': 'tctriunguis'},
 {'label': 'Ochotona princeps (Pika)', 'value': 'oprinceps'},
 {'label': 'Pongo abelii (Orangutan)', 'value': 'pabelii'},
 {'label': 'Nomascus leucogenys (Gibbon)', 'value': 'nleucogenys'},
 {'label': 'Oryzias javanicus (Javanese ricefish)', 'value': 'ojavanicus'},
 {'label': 'Hucho hucho (Huchen)', 'value': 'hhucho'},
 {'label': 'Urocitellus parryii (Arctic ground squirrel)',
  'value': 'uparryii'},
 {'label': "Aotus nancymaae (Ma's night monkey)", 'value': 'anancymaae'},
 {'label': 'Ursus americanus (American black bear)', 'value': 'uamericanus'},
 {'label': 'Microtus ochrogaster (Prairie vole)', 'value': 'mochrogaster'},
 {'label': 'Echinops telfairi (Lesser hedgehog tenrec)', 'value': 'etelfairi'},
 {'label': 'Bos indicus x Bos taurus (Hybrid - Bos Indicus)',
  'value': 'bihybrid'},
 {'label': 'Marmota marmota marmota (Alpine marmot)', 'value': 'mmmarmota'},
 {'label': 'Callorhinchus milii (Elephant shark)', 'value': 'cmilii'},
 {'label': 'Monodon monoceros (Narwhal)', 'value': 'mmonoceros'},
 {'label': 'Cyprinodon variegatus (Sheepshead minnow)',
  'value': 'cvariegatus'},
 {'label': 'Cavia porcellus (Guinea Pig)', 'value': 'cporcellus'},
 {'label': 'Oryzias melastigma (Indian medaka)', 'value': 'omelastigma'},
 {'label': 'Serinus canaria (Common canary)', 'value': 'scanaria'},
 {'label': 'Panthera pardus (Leopard)', 'value': 'ppardus'},
 {'label': 'Delphinapterus leucas (Beluga whale)', 'value': 'dleucas'},
 {'label': 'Caenorhabditis elegans (Caenorhabditis elegans)',
  'value': 'celegans'},
 {'label': 'Sinocyclocheilus grahami (Golden-line barbel)',
  'value': 'sgrahami'},
 {'label': 'Neovison vison (American mink)', 'value': 'nvison'},
 {'label': 'Sorex araneus (Shrew)', 'value': 'saraneus'},
 {'label': 'Scophthalmus maximus (Turbot)', 'value': 'smaximus'},
 {'label': 'Salmo trutta (Brown trout)', 'value': 'strutta'},
 {'label': 'Pelodiscus sinensis (Chinese softshell turtle)',
  'value': 'psinensis'},
 {'label': 'Eptatretus burgeri (Hagfish)', 'value': 'eburgeri'},
 {'label': 'Panthera tigris altaica (Tiger)', 'value': 'ptaltaica'},
 {'label': 'Catagonus wagneri (Chacoan peccary)', 'value': 'cwagneri'},
 {'label': 'Ailuropoda melanoleuca (Giant panda)', 'value': 'amelanoleuca'},
 {'label': 'Seriola dumerili (Greater amberjack)', 'value': 'sdumerili'},
 {'label': 'Anas platyrhynchos (Mallard)', 'value': 'aplatyrhynchos'},
 {'label': 'Physeter catodon (Sperm whale)', 'value': 'pcatodon'},
 {'label': 'Clupea harengus (Atlantic herring)', 'value': 'charengus'},
 {'label': 'Pseudonaja textilis (Eastern brown snake)', 'value': 'ptextilis'},
 {'label': 'Equus asinus asinus (Donkey)', 'value': 'eaasinus'},
 {'label': 'Carassius auratus (Goldfish)', 'value': 'cauratus'},
 {'label': 'Ictalurus punctatus (Channel catfish)', 'value': 'ipunctatus'},
 {'label': 'Larimichthys crocea (Large yellow croaker)', 'value': 'lcrocea'},
 {'label': 'Paramormyrops kingsleyae (Paramormyrops kingsleyae)',
  'value': 'pkingsleyae'},
 {'label': 'Pan paniscus (Bonobo)', 'value': 'ppaniscus'},
 {'label': 'Vicugna pacos (Alpaca)', 'value': 'vpacos'},
 {'label': 'Cervus hanglu yarkandensis (Yarkand deer)',
  'value': 'chyarkandensis'},
 {'label': 'Oncorhynchus tshawytscha (Chinook salmon)',
  'value': 'otshawytscha'},
 {'label': 'Chlorocebus sabaeus (Vervet-AGM)', 'value': 'csabaeus'},
 {'label': 'Ciona intestinalis (C.intestinalis)', 'value': 'cintestinalis'},
 {'label': 'Acanthochromis polyacanthus (Spiny chromis)',
  'value': 'apolyacanthus'},
 {'label': 'Macaca fascicularis (Crab-eating macaque)',
  'value': 'mfascicularis'},
 {'label': 'Geospiza fortis (Medium ground-finch)', 'value': 'gfortis'},
 {'label': 'Salvator merianae (Argentine black and white tegu)',
  'value': 'smerianae'},
 {'label': 'Pan troglodytes (Chimpanzee)', 'value': 'ptroglodytes'},
 {'label': 'Strigops habroptila (Kakapo)', 'value': 'shabroptila'},
 {'label': 'Prolemur simus (Greater bamboo lemur)', 'value': 'psimus'},
 {'label': 'Bos taurus (Cow)', 'value': 'btaurus'},
 {'label': 'Saccharomyces cerevisiae (Saccharomyces cerevisiae)',
  'value': 'scerevisiae'},
 {'label': 'Sander lucioperca (Pike-perch)', 'value': 'slucioperca'},
 {'label': 'Amphiprion ocellaris (Clown anemonefish)', 'value': 'aocellaris'},
 {'label': 'Ovis aries (Sheep (texel))', 'value': 'oaries'},
 {'label': 'Dicentrarchus labrax (European seabass)', 'value': 'dlabrax'},
 {'label': 'Mesocricetus auratus (Golden Hamster)', 'value': 'mauratus'},
 {'label': 'Peromyscus maniculatus bairdii (Northern American deer mouse)',
  'value': 'pmbairdii'},
 {'label': 'Bos grunniens (Domestic yak)', 'value': 'bgrunniens'},
 {'label': 'Laticauda laticaudata (Blue-ringed sea krait)',
  'value': 'llaticaudata'},
 {'label': 'Rhinopithecus roxellana (Golden snub-nosed monkey)',
  'value': 'rroxellana'},
 {'label': 'Fundulus heteroclitus (Mummichog)', 'value': 'fheteroclitus'},
 {'label': 'Takifugu rubripes (Fugu)', 'value': 'trubripes'},
 {'label': 'Cottoperca gobio (Channel bull blenny)', 'value': 'cgobio'},
 {'label': 'Kryptolebias marmoratus (Mangrove rivulus)',
  'value': 'kmarmoratus'},
 {'label': 'Lepisosteus oculatus (Spotted gar)', 'value': 'loculatus'},
 {'label': 'Cyprinus carpio (Common carp)', 'value': 'ccarpio'},
 {'label': 'Felis catus (Cat)', 'value': 'fcatus'},
 {'label': 'Tetraodon nigroviridis (Tetraodon)', 'value': 'tnigroviridis'},
 {'label': 'Ursus maritimus (Polar bear)', 'value': 'umaritimus'},
 {'label': 'Xiphophorus maculatus (Platyfish)', 'value': 'xmaculatus'},
 {'label': 'Macaca nemestrina (Pig-tailed macaque)', 'value': 'mnemestrina'},
 {'label': 'Otolemur garnettii (Bushbaby)', 'value': 'ogarnettii'},
 {'label': 'Meleagris gallopavo (Turkey)', 'value': 'mgallopavo'},
 {'label': 'Poecilia formosa (Amazon molly)', 'value': 'pformosa'},
 {'label': 'Rattus norvegicus (Rat)', 'value': 'rnorvegicus'},
 {'label': 'Electrophorus electricus (Electric eel)', 'value': 'eelectricus'},
 {'label': 'Myripristis murdjan (Pinecone soldierfish)', 'value': 'mmurdjan'},
 {'label': 'Poecilia reticulata (Guppy)', 'value': 'preticulata'},
 {'label': 'Myotis lucifugus (Microbat)', 'value': 'mlucifugus'},
 {'label': 'Ornithorhynchus anatinus (Platypus)', 'value': 'oanatinus'},
 {'label': 'Pteropus vampyrus (Megabat)', 'value': 'pvampyrus'},
 {'label': 'Mus spretus (Algerian mouse)', 'value': 'mspretus'},
 {'label': 'Chinchilla lanigera (Long-tailed chinchilla)',
  'value': 'clanigera'},
 {'label': 'Loxodonta africana (Elephant)', 'value': 'lafricana'},
 {'label': 'Pundamilia nyererei (Makobe Island cichlid)',
  'value': 'pnyererei'},
 {'label': 'Oncorhynchus kisutch (Coho salmon)', 'value': 'okisutch'},
 {'label': 'Stegastes partitus (Bicolor damselfish)', 'value': 'spartitus'},
 {'label': 'Equus caballus (Horse)', 'value': 'ecaballus'},
 {'label': 'Papio anubis (Olive baboon)', 'value': 'panubis'},
 {'label': 'Mandrillus leucophaeus (Drill)', 'value': 'mleucophaeus'},
 {'label': 'Coturnix japonica (Japanese quail)', 'value': 'cjaponica'},
 {'label': 'Octodon degus (Degu)', 'value': 'odegus'},
 {'label': 'Drosophila melanogaster (Drosophila melanogaster)',
  'value': 'dmelanogaster'},
 {'label': 'Gadus morhua (Atlantic cod)', 'value': 'gmorhua'},
 {'label': 'Phascolarctos cinereus (Koala)', 'value': 'pcinereus'},
 {'label': 'Pygocentrus nattereri (Red-bellied piranha)',
  'value': 'pnattereri'},
 {'label': 'Chelonoidis abingdonii (Abingdon island giant tortoise)',
  'value': 'cabingdonii'},
 {'label': 'Mus spicilegus (Steppe mouse)', 'value': 'mspicilegus'},
 {'label': 'Oreochromis niloticus (Nile tilapia)', 'value': 'oniloticus'},
 {'label': 'Gasterosteus aculeatus (Stickleback)', 'value': 'gaculeatus'},
 {'label': 'Sarcophilus harrisii (Tasmanian devil)', 'value': 'sharrisii'},
 {'label': 'Mastacembelus armatus (Zig-zag eel)', 'value': 'marmatus'},
 {'label': 'Dasypus novemcinctus (Armadillo)', 'value': 'dnovemcinctus'},
 {'label': 'Mustela putorius furo (Ferret)', 'value': 'mpfuro'},
 {'label': 'Denticeps clupeoides (Denticle herring)', 'value': 'dclupeoides'},
 {'label': 'Panthera leo (Lion)', 'value': 'pleo'},
 {'label': 'Notechis scutatus (Mainland tiger snake)', 'value': 'nscutatus'},
 {'label': 'Monodelphis domestica (Opossum)', 'value': 'mdomestica'},
 {'label': 'Mus musculus (Mouse)', 'value': 'mmusculus'},
 {'label': 'Yarrowia lipolytica CLIB122 (Yarrowia lipolytica)',
  'value': 'ylipolytica'},
 {'label': 'Colletotrichum orbiculare MAFF 240422 (Colletotrichum orbiculare)',
  'value': 'corbiculare'},
 {'label': 'Beauveria bassiana (Beauveria bassiana)', 'value': 'bbassiana'},
 {'label': 'Aspergillus fumigatus A1163 (Aspergillus fumigatus A1163)',
  'value': 'afumigatusa1163'},
 {'label': 'Aspergillus niger (Aspergillus niger)', 'value': 'aniger'},
 {'label': 'Dothistroma septosporum NZE10 (Dothistroma septosporum)',
  'value': 'dseptosporum'},
 {'label': 'Aspergillus nidulans FGSC A4 (Aspergillus nidulans)',
  'value': 'anidulans'},
 {'label': 'Schizosaccharomyces japonicus yFS275 (Schizosaccharomyces japonicus)',
  'value': 'sjaponicus'},
 {'label': 'Aspergillus fischeri NRRL 181 (Aspergillus fischeri NRRL 181)',
  'value': 'nfischeri'},
 {'label': 'Puccinia graminis f. sp. tritici CRL 75-36-700-3 (Puccinia graminis)',
  'value': 'pgraminis'},
 {'label': 'Fusarium vanettenii 77-13-4 (Fusarium solani)',
  'value': 'fsolani'},
 {'label': 'Microbotryum lychnidis-dioicae p1A1 Lamole (Microbotryum violaceum)',
  'value': 'mviolaceum'},
 {'label': 'Komagataella phaffii GS115 (Komagataella pastoris)',
  'value': 'kpastoris'},
 {'label': 'Cryptococcus neoformans var. neoformans JEC21 (Cryptococcus neoformans var. neoformans JEC21)',
  'value': 'cneoformans'},
 {'label': 'Colletotrichum higginsianum (Colletotrichum higginsianum)',
  'value': 'chigginsianum'},
 {'label': 'Blumeria graminis f. sp. hordei DH14 (Blumeria graminis)',
  'value': 'bgraminis'},
 {'label': 'Puccinia graminis f. sp. tritici 04KEN156/4 (Puccinia graminis Ug99)',
  'value': 'pgraminisug99'},
 {'label': 'Neurospora crassa OR74A (Neurospora crassa)', 'value': 'ncrassa'},
 {'label': 'Schizosaccharomyces pombe 972h- (Schizosaccharomyces pombe)',
  'value': 'spombe'},
 {'label': 'Tuber melanosporum Mel28 (Tuber melanosporum)',
  'value': 'tmelanosporum'},
 {'label': 'Aspergillus terreus NIH2624 (Aspergillus terreus NIH2624)',
  'value': 'aterreus'},
 {'label': 'Fusarium fujikuroi (Fusarium fujikuroi)', 'value': 'ffujikuroi'},
 {'label': 'Parastagonospora nodorum SN15 (Phaeosphaeria nodorum)',
  'value': 'pnodorum'},
 {'label': 'Aspergillus oryzae RIB40 (Aspergillus oryzae RIB40)',
  'value': 'aoryzae'},
 {'label': 'Puccinia striiformis f. sp. tritici PST-130 (Puccinia striiformis f. sp. tritici PST-130 str. Race 130)',
  'value': 'pstriiformis'},
 {'label': 'Pyrenophora teres f. teres 0-1 (Pyrenophora teres)',
  'value': 'pteres'},
 {'label': 'Verticillium dahliae VdLs.17 (Verticillium dahliae)',
  'value': 'vdahliae'},
 {'label': 'Sporisorium reilianum SRZ2 (Sporisorium reilianum)',
  'value': 'sreilianum'},
 {'label': 'Trichoderma virens Gv29-8 (Trichoderma virens)',
  'value': 'tvirens'},
 {'label': 'Schizosaccharomyces octosporus yFS286 (Schizosaccharomyces octosporus)',
  'value': 'soctosporus'},
 {'label': 'Colletotrichum graminicola M1.001 (Colletotrichum graminicola)',
  'value': 'cgraminicola'},
 {'label': 'Fusarium verticillioides 7600 (Fusarium verticillioides)',
  'value': 'fverticillioides'},
 {'label': 'Aspergillus clavatus NRRL 1 (Aspergillus clavatus NRRL 1)',
  'value': 'aclavatus'},
 {'label': 'Ustilago maydis 521 (Ustilago maydis)', 'value': 'umaydis'},
 {'label': 'Zymoseptoria tritici IPO323 (Zymoseptoria tritici)',
  'value': 'ztritici'},
 {'label': 'Aspergillus flavus NRRL3357 (Aspergillus flavus NRRL3357)',
  'value': 'aflavus'},
 {'label': 'Leptosphaeria maculans JN3 (Leptosphaeria maculans)',
  'value': 'lmaculans'},
 {'label': 'Trichoderma reesei QM6a (Trichoderma reesei)', 'value': 'treesei'},
 {'label': 'Schizosaccharomyces cryophilus OY26 (Schizosaccharomyces cryophilus)',
  'value': 'scryophilus'},
 {'label': 'Gaeumannomyces tritici R3-111a-1 (Gaeumannomyces tritici R3-111a-1)',
  'value': 'ggraminis'},
 {'label': 'Aspergillus fumigatus Af293 (Aspergillus fumigatus Af293)',
  'value': 'afumigatus'},
 {'label': 'Pyrenophora tritici-repentis Pt-1C-BFP (Pyrenophora tritici-repentis Pt-1C-BFP)',
  'value': 'ptriticirepentis'},
 {'label': 'Melampsora larici-populina 98AG31 (Melampsora larici-populina)',
  'value': 'mlaricipopulina'},
 {'label': 'Fusarium oxysporum f. sp. lycopersici 4287 (Fusarium oxysporum)',
  'value': 'foxysporum'},
 {'label': 'Botrytis cinerea B05.10 (Botrytis cinerea B05.10)',
  'value': 'bcinerea'},
 {'label': 'Magnaporthiopsis poae ATCC 64411 (Magnaporthe poae)',
  'value': 'mpoae'},
 {'label': 'Fusarium pseudograminearum CS3096 (Fusarium pseudograminearum)',
  'value': 'fpseudograminearum'},
 {'label': 'Fusarium graminearum (Fusarium graminearum str. PH-1)',
  'value': 'fgraminearum'},
 {'label': 'Eremothecium gossypii ATCC 10895 (Ashbya gossypii)',
  'value': 'agossypii'},
 {'label': 'Sclerotinia sclerotiorum 1980 UF-70 (Sclerotinia sclerotiorum)',
  'value': 'ssclerotiorum'},
 {'label': 'Verticillium dahliae JR2 (Verticillium dahliae JR2)',
  'value': 'vdahliaejr2'},
 {'label': 'Colletotrichum fructicola Nara gc5 (Colletotrichum gloeosporioides)',
  'value': 'cgloeosporioides'},
 {'label': 'Puccinia triticina 1-1 BBBD Race 1 (Puccinia triticina)',
  'value': 'ptriticina'},
 {'label': 'Fusarium culmorum CS7071 (Fusarium culmorum UK99)',
  'value': 'fculmorum'},
 {'label': 'Pyricularia oryzae 70-15 (Magnaporthe oryzae)',
  'value': 'moryzae'},
 {'label': 'Caenorhabditis briggsae (Caenorhabditis briggsae)',
  'value': 'cbriggsae'},
 {'label': 'Glossina brevipalpis (Glossina brevipalpis)',
  'value': 'gbrevipalpis'},
 {'label': 'Aedes albopictus (Aedes albopictus)', 'value': 'aalbopictus'},
 {'label': 'Adineta vaga (Adineta vaga)', 'value': 'avaga'},
 {'label': 'Pristionchus pacificus (Pristionchus pacificus)',
  'value': 'ppacificus'},
 {'label': 'Schistosoma mansoni (Schistosoma mansoni)', 'value': 'smansoni'},
 {'label': 'Drosophila virilis (Drosophila virilis (TSC#15010-1051.87))',
  'value': 'dvirilis'},
 {'label': 'Anopheles darlingi (Anopheles darlingi)', 'value': 'adarlingi'},
 {'label': 'Bemisia tabaci (Bemisia tabaci (ASIAII-5))', 'value': 'btasiaii5'},
 {'label': 'Strongyloides ratti (Strongyloides ratti)', 'value': 'sratti'},
 {'label': 'Anopheles sinensis (Anopheles sinensis (China))',
  'value': 'aschina'},
 {'label': 'Drosophila grimshawi (Drosophila grimshawi (TSC#15287-2541.00))',
  'value': 'dgrimshawi'},
 {'label': 'Glossina palpalis gambiensis (Glossina palpalis)',
  'value': 'gpalpalis'},
 {'label': 'Atta cephalotes (Atta cephalotes)', 'value': 'acephalotes'},
 {'label': 'Solenopsis invicta (Solenopsis invicta)', 'value': 'sinvicta'},
 {'label': 'Strongylocentrotus purpuratus (Strongylocentrotus purpuratus (Spur 01))',
  'value': 'spurpuratus'},
 {'label': 'Drosophila ananassae (Drosophila ananassae (TSC#14024-0371.13))',
  'value': 'dananassae'},
 {'label': 'Bemisia tabaci (Bemisia tabaci (SSA3 NG))', 'value': 'btssa3nig'},
 {'label': 'Lepeophtheirus salmonis (Lepeophtheirus salmonis)',
  'value': 'lsalmonis'},
 {'label': 'Biomphalaria glabrata (Biomphalaria glabrata)',
  'value': 'bglabrata'},
 {'label': 'Apis mellifera (Apis mellifera (DH4))', 'value': 'amellifera'},
 {'label': 'Mnemiopsis leidyi (Mnemiopsis leidyi)', 'value': 'mleidyi'},
 {'label': 'Caenorhabditis remanei (Caenorhabditis remanei)',
  'value': 'cremanei'},
 {'label': 'Branchiostoma lanceolatum (Branchiostoma lanceolatum)',
  'value': 'blanceolatum'},
 {'label': 'Drosophila erecta (Drosophila erecta (TSC#14021-0224.01))',
  'value': 'derecta'},
 {'label': 'Megaselia scalaris (Megaselia scalaris)', 'value': 'mscalaris'},
 {'label': 'Drosophila willistoni (Drosophila willistoni (TSC#14030-0811.24))',
  'value': 'dwillistoni'},
 {'label': 'Anopheles minimus (Anopheles minimus)', 'value': 'aminimus'},
 {'label': 'Loa loa (Loa loa)', 'value': 'lloa'},
 {'label': 'Strigamia maritima (Strigamia maritima)', 'value': 'smaritima'},
 {'label': 'Dendroctonus ponderosae (Dendroctonus ponderosae)',
  'value': 'dponderosae'},
 {'label': 'Anopheles melas (Anopheles melas)', 'value': 'amelas'},
 {'label': 'Trichinella spiralis (Trichinella spiralis)',
  'value': 'tspiralis'},
 {'label': 'Bombyx mori (Bombyx mori)', 'value': 'bmori'},
 {'label': 'Tetranychus urticae (Tetranychus urticae)', 'value': 'turticae'},
 {'label': 'Glossina fuscipes fuscipes (Glossina fuscipes fuscipes)',
  'value': 'gfuscipes'},
 {'label': 'Rhodnius prolixus (Rhodnius prolixus)', 'value': 'rprolixus'},
 {'label': 'Drosophila simulans (Drosophila simulans (w501))',
  'value': 'dsimulans'},
 {'label': 'Anopheles epiroticus (Anopheles epiroticus)',
  'value': 'aepiroticus'},
 {'label': 'Anopheles culicifacies (Anopheles culicifacies)',
  'value': 'aculicifacies'},
 {'label': 'Bemisia tabaci (Bemisia tabaci (SSA1-SG1 UG))',
  'value': 'btssa1ug'},
 {'label': 'Stegodyphus mimosarum (Stegodyphus mimosarum)',
  'value': 'smimosarum'},
 {'label': 'Melitaea cinxia (Melitaea cinxia)', 'value': 'mcinxia'},
 {'label': 'Caenorhabditis brenneri (Caenorhabditis brenneri)',
  'value': 'cbrenneri'},
 {'label': 'Aedes aegypti (Aedes aegypti (LVP_AGWG))', 'value': 'aalvpagwg'},
 {'label': 'Ixodes scapularis (Ixodes scapularis (ISE6))', 'value': 'isise6'},
 {'label': 'Amphimedon queenslandica (Amphimedon queenslandica)',
  'value': 'aqueenslandica'},
 {'label': 'Anopheles stephensi (Anopheles stephensi)', 'value': 'astephensi'},
 {'label': 'Onchocerca volvulus (Onchocerca volvulus)', 'value': 'ovolvulus'},
 {'label': 'Anopheles quadriannulatus (Anopheles quadriannulatus)',
  'value': 'aquadriannulatus'},
 {'label': 'Brugia malayi (Brugia malayi)', 'value': 'bmalayi'},
 {'label': 'Capitella teleta (Capitella teleta)', 'value': 'cteleta'},
 {'label': 'Belgica antarctica (Belgica antarctica)', 'value': 'bantarctica'},
 {'label': 'Anopheles stephensi (Anopheles stephensi (Indian))',
  'value': 'asindian'},
 {'label': 'Danaus plexippus (Danaus plexippus)', 'value': 'dplexippus'},
 {'label': 'Anopheles funestus (Anopheles funestus)', 'value': 'afunestus'},
 {'label': 'Drosophila mojavensis (Drosophila mojavensis (TSC#15081-1352.22))',
  'value': 'dmojavensis'},
 {'label': 'Anopheles atroparvus (Anopheles atroparvus)',
  'value': 'aatroparvus'},
 {'label': 'Tribolium castaneum (Tribolium castaneum)', 'value': 'tcastaneum'},
 {'label': 'Anoplophora glabripennis (Anoplophora glabripennis)',
  'value': 'aglabripennis'},
 {'label': 'Anopheles albimanus (Anopheles albimanus)', 'value': 'aalbimanus'},
 {'label': 'Culex quinquefasciatus (Culex quinquefasciatus)',
  'value': 'cquinquefasciatus'},
 {'label': 'Drosophila persimilis (Drosophila persimilis (MSH-3))',
  'value': 'dpersimilis'},
 {'label': 'Crassostrea gigas (Crassostrea gigas)', 'value': 'cgigas'},
 {'label': 'Anopheles gambiae (Anopheles gambiae)', 'value': 'agambiae'},
 {'label': 'Bemisia tabaci (Bemisia tabaci (SSA2 NG))', 'value': 'btssa2nig'},
 {'label': 'Leptotrombidium deliense (Leptotrombidium deliense)',
  'value': 'ldeliense'},
 {'label': 'Daphnia magna (Daphnia magna)', 'value': 'dmagna'},
 {'label': 'Nematostella vectensis (Nematostella vectensis)',
  'value': 'nvectensis'},
 {'label': 'Drosophila sechellia (Drosophila sechellia (Rob3c))',
  'value': 'dsechellia'},
 {'label': 'Stomoxys calcitrans (Stomoxys calcitrans)',
  'value': 'scalcitrans'},
 {'label': 'Anopheles maculatus (Anopheles maculatus)', 'value': 'amaculatus'},
 {'label': 'Bombus terrestris (Bombus terrestris)', 'value': 'bterrestris'},
 {'label': 'Octopus bimaculoides (Octopus bimaculoides)',
  'value': 'obimaculoides'},
 {'label': 'Teleopsis dalmanni (Teleopsis dalmanni)', 'value': 'tdalmanni'},
 {'label': 'Daphnia pulex (Daphnia pulex)', 'value': 'dpulex'},
 {'label': 'Thelohanellus kitauei (Thelohanellus kitauei)',
  'value': 'tkitauei'},
 {'label': 'Drosophila yakuba (Drosophila yakuba (Tai18E2))',
  'value': 'dyakuba'},
 {'label': 'Anopheles coluzzii (Anopheles coluzzii (Ngousso))',
  'value': 'acngousso'},
 {'label': 'Helobdella robusta (Helobdella robusta)', 'value': 'hrobusta'},
 {'label': 'Anopheles dirus (Anopheles dirus)', 'value': 'adirus'},
 {'label': 'Anopheles arabiensis (Anopheles arabiensis)',
  'value': 'aarabiensis'},
 {'label': 'Glossina pallidipes (Glossina pallidipes)',
  'value': 'gpallidipes'},
 {'label': 'Ixodes scapularis (Ixodes scapularis)', 'value': 'iscapularis'},
 {'label': 'Orchesella cincta (Orchesella cincta)', 'value': 'ocincta'},
 {'label': 'Nasonia vitripennis (Nasonia vitripennis (AsymCx))',
  'value': 'nvitripennis'},
 {'label': 'Anopheles merus (Anopheles merus)', 'value': 'amerus'},
 {'label': 'Dinothrombium tinctorium (Dinothrombium tinctorium)',
  'value': 'dtinctorium'},
 {'label': 'Lottia gigantea (Lottia gigantea)', 'value': 'lgigantea'},
 {'label': 'Cimex lectularius (Cimex lectularius)', 'value': 'clectularius'},
 {'label': 'Anopheles coluzzii (Anopheles coluzzii)', 'value': 'acoluzzii'},
 {'label': 'Anopheles sinensis (Anopheles sinensis)', 'value': 'asinensis'},
 {'label': 'Phlebotomus papatasi (Phlebotomus papatasi)',
  'value': 'ppapatasi'},
 {'label': 'Pediculus humanus corporis (Pediculus humanus)',
  'value': 'phumanus'},
 {'label': 'Glossina morsitans morsitans (Glossina morsitans)',
  'value': 'gmorsitans'},
 {'label': 'Hofstenia miamia (Hofstenia miamia)', 'value': 'hmiamia'},
 {'label': 'Lucilia cuprina (Lucilia cuprina)', 'value': 'lcuprina'},
 {'label': 'Heliconius melpomene (Heliconius melpomene)',
  'value': 'hmelpomene'},
 {'label': 'Bemisia tabaci (Bemisia tabaci (SSA1-SG1 NG))',
  'value': 'btssa1nig'},
 {'label': 'Lutzomyia longipalpis (Lutzomyia longipalpis)',
  'value': 'llongipalpis'},
 {'label': 'Bemisia tabaci (Bemisia tabaci (Uganda 1))',
  'value': 'btsweetpotug'},
 {'label': 'Glossina austeni (Glossina austeni)', 'value': 'gausteni'},
 {'label': 'Culicoides sonorensis (Culicoides sonorensis)',
  'value': 'csonorensis'},
 {'label': 'Zootermopsis nevadensis (Zootermopsis nevadensis)',
  'value': 'znevadensis'},
 {'label': 'Folsomia candida (Folsomia candida str. VU population)',
  'value': 'fcandida'},
 {'label': 'Bombus impatiens (Bombus impatiens)', 'value': 'bimpatiens'},
 {'label': 'Sarcoptes scabiei (Sarcoptes scabiei)', 'value': 'sscabiei'},
 {'label': 'Mayetiola destructor (Mayetiola destructor)',
  'value': 'mdestructor'},
 {'label': 'Anopheles farauti (Anopheles farauti)', 'value': 'afarauti'},
 {'label': 'Lingula anatina (Lingula anatina)', 'value': 'lanatina'},
 {'label': 'Drosophila pseudoobscura pseudoobscura (Drosophila pseudoobscura pseudoobscura (MV2-25))',
  'value': 'dpseudoobscura'},
 {'label': 'Trichoplax adhaerens (Trichoplax adhaerens)',
  'value': 'tadhaerens'},
 {'label': 'Acyrthosiphon pisum (Acyrthosiphon pisum)', 'value': 'apisum'},
 {'label': 'Anopheles christyi (Anopheles christyi)', 'value': 'achristyi'},
 {'label': 'Mesorhabditis belari (Mesorhabditis belari (PRJEB30104))',
  'value': 'mebelaprjeb30104'},
 {'label': 'Heligmosomoides polygyrus (Heligmosomoides polygyrus (PRJEB1203))',
  'value': 'hepolyprjeb1203'},
 {'label': 'Caenorhabditis sp. 21 LS-2015 (Caenorhabditis parvicauda (PRJEB12595))',
  'value': 'caparvprjeb12595'},
 {'label': 'Meloidogyne floridensis (Meloidogyne floridensis (PRJEB6016))',
  'value': 'meflorprjeb6016'},
 {'label': 'Rodentolepis nana (Hymenolepis nana (PRJEB508))',
  'value': 'hynanaprjeb508'},
 {'label': 'Necator americanus (Necator americanus (PRJNA72135))',
  'value': 'neamerprjna72135'},
 {'label': 'Caenorhabditis inopinata (Caenorhabditis inopinata (PRJDB5687))',
  'value': 'cainopprjdb5687'},
 {'label': 'Steinernema scapterisci (Steinernema scapterisci (PRJNA204942))',
  'value': 'stscapprjna204942'},
 {'label': 'Taenia multiceps (Taenia multiceps (PRJNA307624))',
  'value': 'tamultprjna307624'},
 {'label': 'Diploscapter coronatus (Diploscapter coronatus (PRJDB3143))',
  'value': 'dicoroprjdb3143'},
 {'label': 'Plectus sambesii (Plectus sambesii (PRJNA390260))',
  'value': 'plsambprjna390260'},
 {'label': 'Meloidogyne incognita (Meloidogyne incognita (PRJEB8714))',
  'value': 'meincoprjeb8714'},
 {'label': 'Trichinella nativa (Trichinella nativa (PRJNA257433))',
  'value': 'trnatiprjna257433'},
 {'label': 'Schistosoma haematobium (Schistosoma haematobium (PRJNA78265))',
  'value': 'schaemprjna78265'},
 {'label': 'Schistosoma margrebowiei (Schistosoma margrebowiei (PRJEB522))',
  'value': 'scmargprjeb522'},
 {'label': 'Caenorhabditis elegans (Caenorhabditis elegans (PRJNA13758) [WS276])',
  'value': 'caelegprjna13758'},
 {'label': 'Ascaris suum (Ascaris suum (PRJNA80881))',
  'value': 'assuumprjna80881'},
 {'label': 'Panagrolaimus sp. ES5 (Panagrolaimus es5 (PRJEB32708))',
  'value': 'paes5prjeb32708'},
 {'label': 'Brugia malayi (Brugia malayi (PRJNA10729) [WS276])',
  'value': 'brmalaprjna10729'},
 {'label': 'Trichuris muris (Trichuris muris (PRJEB126) [WS276])',
  'value': 'trmuriprjeb126'},
 {'label': 'Schmidtea mediterranea (Schmidtea mediterranea (PRJNA12585))',
  'value': 'scmediprjna12585'},
 {'label': 'Caenorhabditis latens (Caenorhabditis latens (PRJNA248912))',
  'value': 'calateprjna248912'},
 {'label': 'Fasciola gigantica (Fasciola gigantica (PRJNA230515))',
  'value': 'fagigaprjna230515'},
 {'label': 'Syphacia muris (Syphacia muris (PRJEB524))',
  'value': 'symuriprjeb524'},
 {'label': 'Caenorhabditis remanei (Caenorhabditis remanei (PRJNA248909))',
  'value': 'caremaprjna248909'},
 {'label': 'Pristionchus exspectatus (Pristionchus exspectatus (PRJEB24288))',
  'value': 'prexspprjeb24288'},
 {'label': 'Elaeophora elaphi (Elaeophora elaphi (PRJEB502))',
  'value': 'elelapprjeb502'},
 {'label': 'Trichinella sp. T9 (Trichinella sp. T9 (PRJNA257433))',
  'value': 'trt9prjna257433'},
 {'label': 'Parascaris equorum (Parascaris equorum (PRJEB514))',
  'value': 'paequoprjeb514'},
 {'label': 'Echinococcus multilocularis (Echinococcus multilocularis (PRJEB122))',
  'value': 'ecmultprjeb122'},
 {'label': 'Echinococcus granulosus (Echinococcus granulosus (PRJEB121))',
  'value': 'ecgranprjeb121'},
 {'label': 'Steinernema monticolum (Steinernema monticolum (PRJNA205067))',
  'value': 'stmontprjna205067'},
 {'label': 'Schistocephalus solidus (Schistocephalus solidus (PRJEB527))',
  'value': 'scsoliprjeb527'},
 {'label': 'Caenorhabditis angaria (Caenorhabditis angaria (PRJNA51225))',
  'value': 'caangaprjna51225'},
 {'label': 'Hymenolepis diminuta (Hymenolepis diminuta (PRJEB30942))',
  'value': 'hydimiprjeb30942'},
 {'label': 'Brugia timori (Brugia timori (PRJEB4663))',
  'value': 'brtimoprjeb4663'},
 {'label': 'Onchocerca flexuosa (Onchocerca flexuosa (PRJEB512))',
  'value': 'onflexprjeb512'},
 {'label': 'Strongyloides venezuelensis (Strongyloides venezuelensis (PRJEB530))',
  'value': 'stveneprjeb530'},
 {'label': 'Parapristionchus giblindavisi (Parapristionchus giblindavisi (PRJEB27334))',
  'value': 'pagiblprjeb27334'},
 {'label': 'Trichinella spiralis (Trichinella spiralis (PRJNA257433))',
  'value': 'trspirprjna257433'},
 {'label': 'Dracunculus medinensis (Dracunculus medinensis (PRJEB500))',
  'value': 'drmediprjeb500'},
 {'label': 'Meloidogyne arenaria (Meloidogyne arenaria (PRJEB8714))',
  'value': 'mearenprjeb8714'},
 {'label': 'Haemonchus contortus (Haemonchus contortus (PRJEB506))',
  'value': 'hacontprjeb506'},
 {'label': 'Soboliphyme baturini (Soboliphyme baturini (PRJEB516))',
  'value': 'sobatuprjeb516'},
 {'label': 'Pristionchus pacificus (Pristionchus pacificus (PRJNA12644) [WS276])',
  'value': 'prpaciprjna12644'},
 {'label': 'Schistosoma rodhaini (Schistosoma rodhaini (PRJEB526))',
  'value': 'scrodhprjeb526'},
 {'label': 'Caenorhabditis nigoni (Caenorhabditis nigoni (PRJNA384657))',
  'value': 'canigoprjna384657'},
 {'label': 'Heterodera glycines (Heterodera glycines (PRJNA381081))',
  'value': 'heglycprjna381081'},
 {'label': 'Ditylenchus destructor (Ditylenchus destructor (PRJNA312427))',
  'value': 'didestprjna312427'},
 {'label': 'Panagrellus redivivus (Panagrellus redivivus (PRJNA186477))',
  'value': 'parediprjna186477'},
 {'label': 'Caenorhabditis brenneri (Caenorhabditis brenneri (PRJNA20035) [WS276])',
  'value': 'cabrenprjna20035'},
 {'label': 'Taenia saginata (Taenia saginata (PRJNA71493))',
  'value': 'tasagiprjna71493'},
 {'label': 'Panagrolaimus superbus (Panagrolaimus superbus (PRJEB32708))',
  'value': 'pasupeprjeb32708'},
 {'label': 'Haemonchus placei (Haemonchus placei (PRJEB509))',
  'value': 'haplacprjeb509'},
 {'label': 'Diploscapter pachys (Diploscapter pachys (PRJNA280107))',
  'value': 'dipachprjna280107'},
 {'label': 'Caenorhabditis panamensis (Caenorhabditis panamensis (PRJEB28259))',
  'value': 'capanaprjeb28259'},
 {'label': 'Mesocestoides corti (Mesocestoides corti (PRJEB510))',
  'value': 'mecortprjeb510'},
 {'label': 'Ditylenchus dipsaci (Ditylenchus dipsaci (PRJNA498219))',
  'value': 'didipsprjna498219'},
 {'label': 'Brugia pahangi (Brugia pahangi (PRJEB497))',
  'value': 'brpahaprjeb497'},
 {'label': 'Echinococcus canadensis (Echinococcus canadensis (PRJEB8992))',
  'value': 'eccanaprjeb8992'},
 {'label': 'Taenia asiatica (Taenia asiatica (PRJNA299871))',
  'value': 'taasiaprjna299871'},
 {'label': 'Caenorhabditis sp. 40 LS-2015 (Caenorhabditis tribulationis (PRJEB12608))',
  'value': 'catribprjeb12608'},
 {'label': 'Trichinella britovi (Trichinella britovi (PRJNA257433))',
  'value': 'trbritprjna257433'},
 {'label': 'Trichobilharzia regenti (Trichobilharzia regenti (PRJEB4662))',
  'value': 'trregeprjeb4662'},
 {'label': 'Heterorhabditis bacteriophora (Heterorhabditis bacteriophora (PRJNA13977))',
  'value': 'hebactprjna13977'},
 {'label': 'Trichuris trichiura (Trichuris trichiura (PRJEB535))',
  'value': 'trtricprjeb535'},
 {'label': 'Panagrolaimus davidi (Panagrolaimus davidi (PRJEB32708))',
  'value': 'padaviprjeb32708'},
 {'label': 'Ascaris suum (Ascaris suum (PRJNA62057))',
  'value': 'assuumprjna62057'},
 {'label': 'Steinernema glaseri (Steinernema glaseri (PRJNA204943))',
  'value': 'stglasprjna204943'},
 {'label': 'Gyrodactylus salaris (Gyrodactylus salaris (PRJNA244375))',
  'value': 'gysalaprjna244375'},
 {'label': 'Globodera pallida (Globodera pallida (PRJEB123))',
  'value': 'glpallprjeb123'},
 {'label': 'Spirometra erinaceieuropaei (Spirometra erinaceieuropaei (PRJEB1202))',
  'value': 'sperinprjeb1202'},
 {'label': 'Litomosoides sigmodontis (Litomosoides sigmodontis (PRJEB3075))',
  'value': 'lisigmprjeb3075'},
 {'label': 'Ascaris lumbricoides (Ascaris lumbricoides (PRJEB4950))',
  'value': 'aslumbprjeb4950'},
 {'label': 'Dibothriocephalus latus (Dibothriocephalus latus (PRJEB1206))',
  'value': 'dilatuprjeb1206'},
 {'label': 'Setaria digitata (Setaria digitata (PRJNA479729))',
  'value': 'sedigiprjna479729'},
 {'label': 'Echinococcus granulosus (Echinococcus granulosus (PRJNA182977))',
  'value': 'ecgranprjna182977'},
 {'label': 'Globodera rostochiensis (Globodera rostochiensis (PRJEB13504))',
  'value': 'glrostprjeb13504'},
 {'label': 'Caenorhabditis remanei (Caenorhabditis remanei (PRJNA53967) [WS276])',
  'value': 'caremaprjna53967'},
 {'label': 'Meloidogyne arenaria (Meloidogyne arenaria (PRJNA438575))',
  'value': 'mearenprjna438575'},
 {'label': 'Oesophagostomum dentatum (Oesophagostomum dentatum (PRJNA72579))',
  'value': 'oedentprjna72579'},
 {'label': 'Pristionchus arcanus (Pristionchus arcanus (PRJEB27334))',
  'value': 'prarcaprjeb27334'},
 {'label': 'Pristionchus maxplancki (Pristionchus maxplancki (PRJEB27334))',
  'value': 'prmaxpprjeb27334'},
 {'label': 'Meloidogyne graminicola (Meloidogyne graminicola (PRJNA411966))',
  'value': 'megramprjna411966'},
 {'label': 'Schistosoma japonicum (Schistosoma japonicum (PRJEA34885))',
  'value': 'scjapoprjea34885'},
 {'label': 'Clonorchis sinensis (Clonorchis sinensis (PRJDA72781))',
  'value': 'clsineprjda72781'},
 {'label': 'Onchocerca flexuosa (Onchocerca flexuosa (PRJNA230512))',
  'value': 'onflexprjna230512'},
 {'label': 'Dictyocaulus viviparus (Dictyocaulus viviparus (PRJNA72587))',
  'value': 'diviviprjna72587'},
 {'label': 'Opisthorchis viverrini (Opisthorchis viverrini (PRJNA222628))',
  'value': 'opviveprjna222628'},
 {'label': 'Parascaris univalens (Parascaris univalens (PRJNA386823))',
  'value': 'paunivprjna386823'},
 {'label': 'Romanomermis culicivorax (Romanomermis culicivorax (PRJEB1358))',
  'value': 'roculiprjeb1358'},
 {'label': 'Steinernema feltiae (Steinernema feltiae (PRJNA204661))',
  'value': 'stfeltprjna204661'},
 {'label': 'Haemonchus contortus (Haemonchus contortus (PRJNA205202))',
  'value': 'hacontprjna205202'},
 {'label': 'Ancylostoma caninum (Ancylostoma caninum (PRJNA72585))',
  'value': 'ancaniprjna72585'},
 {'label': 'Trichinella sp. T6 (Trichinella sp. T6 (PRJNA257433))',
  'value': 'trt6prjna257433'},
 {'label': 'Caenorhabditis sp. 31 LS-2015 (Caenorhabditis uteleia (PRJEB12600))',
  'value': 'cautelprjeb12600'},
 {'label': 'Onchocerca volvulus (Onchocerca volvulus (PRJEB513) [WS276])',
  'value': 'onvolvprjeb513'},
 {'label': 'Steinernema carpocapsae (Steinernema carpocapsae (PRJNA202318))',
  'value': 'stcarpprjna202318'},
 {'label': 'Fasciola hepatica (Fasciola hepatica (PRJNA179522))',
  'value': 'fahepaprjna179522'},
 {'label': 'Ancylostoma ceylanicum (Ancylostoma ceylanicum (PRJNA231479))',
  'value': 'anceylprjna231479'},
 {'label': 'Nippostrongylus brasiliensis (Nippostrongylus brasiliensis (PRJEB511))',
  'value': 'nibrasprjeb511'},
 {'label': 'Wuchereria bancrofti (Wuchereria bancrofti (PRJNA275548))',
  'value': 'wubancprjna275548'},
 {'label': 'Trichinella zimbabwensis (Trichinella zimbabwensis (PRJNA257433))',
  'value': 'trzimbprjna257433'},
 {'label': 'Panagrolaimus sp. JU765 (Propanagrolaimus ju765 (PRJEB32708))',
  'value': 'prju76prjeb32708'},
 {'label': 'Trichinella nelsoni (Trichinella nelsoni (PRJNA257433))',
  'value': 'trnelsprjna257433'},
 {'label': 'Dirofilaria immitis (Dirofilaria immitis (PRJEB1797))',
  'value': 'diimmiprjeb1797'},
 {'label': 'Wuchereria bancrofti (Wuchereria bancrofti (PRJEB536))',
  'value': 'wubancprjeb536'},
 {'label': 'Strongylus vulgaris (Strongylus vulgaris (PRJEB531))',
  'value': 'stvulgprjeb531'},
 {'label': 'Strongyloides ratti (Strongyloides ratti (PRJEB125) [WS276])',
  'value': 'strattprjeb125'},
 {'label': 'Meloidogyne incognita (Meloidogyne incognita (PRJNA340324))',
  'value': 'meincoprjna340324'},
 {'label': 'Teladorsagia circumcincta (Teladorsagia circumcincta (PRJNA72569))',
  'value': 'tecircprjna72569'},
 {'label': 'Caenorhabditis sp. 39 LS-2015 (Caenorhabditis waitukubuli (PRJEB12602))',
  'value': 'cawaitprjeb12602'},
 {'label': 'Angiostrongylus cantonensis (Angiostrongylus cantonensis (PRJNA350391))',
  'value': 'ancantprjna350391'},
 {'label': 'Enterobius vermicularis (Enterobius vermicularis (PRJEB503))',
  'value': 'envermprjeb503'},
 {'label': 'Loa loa (Loa loa (PRJNA37757))', 'value': 'loloaprjna37757'},
 {'label': 'Trichinella patagoniensis (Trichinella patagoniensis (PRJNA257433))',
  'value': 'trpataprjna257433'},
 {'label': 'Hymenolepis microstoma (Hymenolepis microstoma (PRJEB124))',
  'value': 'hymicrprjeb124'},
 {'label': 'Schistosoma curassoni (Schistosoma curassoni (PRJEB519))',
  'value': 'sccuraprjeb519'},
 {'label': 'Hymenolepis diminuta (Hymenolepis diminuta (PRJEB507))',
  'value': 'hydimiprjeb507'},
 {'label': 'Caenorhabditis sp. 32 LS-2015 (Caenorhabditis sulstoni (PRJEB12601))',
  'value': 'casulsprjeb12601'},
 {'label': 'Trichinella pseudospiralis (Trichinella pseudospiralis (ISS13 PRJNA257433))',
  'value': 'iss13prjna257433'},
 {'label': 'Gongylonema pulchrum (Gongylonema pulchrum (PRJEB505))',
  'value': 'gopulcprjeb505'},
 {'label': 'Meloidogyne javanica (Meloidogyne javanica (PRJNA340324))',
  'value': 'mejavaprjna340324'},
 {'label': 'Steinernema feltiae (Steinernema feltiae (PRJNA353610))',
  'value': 'stfeltprjna353610'},
 {'label': 'Trichinella pseudospiralis (Trichinella pseudospiralis (ISS141 PRJNA257433))',
  'value': 'iss141prjna257433'},
 {'label': 'Micoletzkya japonica (Micoletzkya japonica (PRJEB27334))',
  'value': 'mijapoprjeb27334'},
 {'label': 'Heligmosomoides polygyrus (Heligmosomoides polygyrus (PRJEB15396))',
  'value': 'hepolyprjeb15396'},
 {'label': 'Ancylostoma ceylanicum (Ancylostoma ceylanicum (PRJNA72583))',
  'value': 'anceylprjna72583'},
 {'label': 'Acanthocheilonema viteae (Acanthocheilonema viteae (PRJEB1697))',
  'value': 'acviteprjeb1697'},
 {'label': 'Trichinella spiralis (Trichinella spiralis (PRJNA12603))',
  'value': 'trspirprjna12603'},
 {'label': 'Pristionchus entomophagus (Pristionchus entomophagus (PRJEB27334))',
  'value': 'prentoprjeb27334'},
 {'label': 'Caenorhabditis sinica (Caenorhabditis sinica (PRJNA194557))',
  'value': 'casiniprjna194557'},
 {'label': 'Trichinella sp. T8 (Trichinella sp. T8 (PRJNA257433))',
  'value': 'trt8prjna257433'},
 {'label': 'Trichinella nativa (Trichinella nativa (PRJNA179527))',
  'value': 'trnatiprjna179527'},
 {'label': 'Toxocara canis (Toxocara canis (PRJNA248777))',
  'value': 'tocaniprjna248777'},
 {'label': 'Onchocerca ochengi (Onchocerca ochengi (PRJEB1465))',
  'value': 'onocheprjeb1465'},
 {'label': 'Schistosoma bovis (Schistosoma bovis (PRJNA451066))',
  'value': 'scboviprjna451066'},
 {'label': 'Trichinella pseudospiralis (Trichinella pseudospiralis (ISS588 PRJNA257433))',
  'value': 'iss588prjna257433'},
 {'label': 'Anisakis simplex (Anisakis simplex (PRJEB496))',
  'value': 'ansimpprjeb496'},
 {'label': 'Hydatigera taeniaeformis (Hydatigera taeniaeformis (PRJEB534))',
  'value': 'hytaenprjeb534'},
 {'label': 'Onchocerca ochengi (Onchocerca ochengi (PRJEB1204))',
  'value': 'onocheprjeb1204'},
 {'label': 'Echinostoma caproni (Echinostoma caproni (PRJEB1207))',
  'value': 'eccaprprjeb1207'},
 {'label': 'Trichinella pseudospiralis (Trichinella pseudospiralis (ISS470 PRJNA257433))',
  'value': 'iss470prjna257433'},
 {'label': 'Schmidtea mediterranea (Schmidtea mediterranea (PRJNA379262))',
  'value': 'scmediprjna379262'},
 {'label': 'Caenorhabditis sp. 38 MB-2015 (Caenorhabditis quiockensis (PRJEB11354))',
  'value': 'caquioprjeb11354'},
 {'label': 'Schistosoma japonicum (Schistosoma japonicum (PRJNA520774))',
  'value': 'scjapoprjna520774'},
 {'label': 'Taenia solium (Taenia solium (PRJNA170813))',
  'value': 'tasoliprjna170813'},
 {'label': 'Cylicostephanus goldi (Cylicostephanus goldi (PRJEB498))',
  'value': 'cygoldprjeb498'},
 {'label': 'Ancylostoma duodenale (Ancylostoma duodenale (PRJNA72581))',
  'value': 'anduodprjna72581'},
 {'label': 'Caenorhabditis tropicalis (Caenorhabditis tropicalis (PRJNA53597))',
  'value': 'catropprjna53597'},
 {'label': 'Angiostrongylus cantonensis (Angiostrongylus cantonensis (PRJEB493))',
  'value': 'ancantprjeb493'},
 {'label': 'Halicephalobus sp. WB-2010a (Halicephalobus mephisto (PRJNA528747))',
  'value': 'hamephprjna528747'},
 {'label': 'Protopolystoma xenopodis (Protopolystoma xenopodis (PRJEB1201))',
  'value': 'prxenoprjeb1201'},
 {'label': 'Meloidogyne hapla (Meloidogyne hapla (PRJNA29083))',
  'value': 'mehaplprjna29083'},
 {'label': 'Steinernema carpocapsae (Steinernema carpocapsae (v1 PRJNA202318))',
  'value': 'stcav1prjna202318'},
 {'label': 'Trichuris suis (Trichuris suis (PRJNA208416 - female))',
  'value': 'trsuisprjna208416'},
 {'label': 'Oscheius tipulae (Oscheius tipulae (PRJEB15512))',
  'value': 'ostipuprjeb15512'},
 {'label': 'Meloidogyne arenaria (Meloidogyne arenaria (PRJNA340324))',
  'value': 'mearenprjna340324'},
 {'label': 'Meloidogyne floridensis (Meloidogyne floridensis (PRJNA340324))',
  'value': 'meflorprjna340324'},
 {'label': 'Rhabditophanes sp. KR3021 (Rhabditophanes sp. KR3021 (PRJEB1297))',
  'value': 'rhkr30prjeb1297'},
 {'label': 'Acrobeloides nanus (Acrobeloides nanus (PRJEB26554))',
  'value': 'acnanuprjeb26554'},
 {'label': 'Angiostrongylus costaricensis (Angiostrongylus costaricensis (PRJEB494))',
  'value': 'ancostprjeb494'},
 {'label': 'Toxocara canis (Toxocara canis (PRJEB533))',
  'value': 'tocaniprjeb533'},
 {'label': 'Macrostomum lignano (Macrostomum lignano (PRJNA371498))',
  'value': 'malignprjna371498'},
 {'label': 'Pristionchus mayeri (Pristionchus mayeri (PRJEB27334))',
  'value': 'prmayeprjeb27334'},
 {'label': 'Trichinella murrelli (Trichinella murrelli (PRJNA257433))',
  'value': 'trmurrprjna257433'},
 {'label': 'Trichuris suis (Trichuris suis (PRJNA208415 - male))',
  'value': 'trsuisprjna208415'},
 {'label': 'Caenorhabditis remanei (Caenorhabditis remanei (PRJNA248911))',
  'value': 'caremaprjna248911'},
 {'label': 'Parastrongyloides trichosuri (Parastrongyloides trichosuri (PRJEB515))',
  'value': 'patricprjeb515'},
 {'label': 'Trichinella pseudospiralis (Trichinella pseudospiralis (ISS176 PRJNA257433))',
  'value': 'iss176prjna257433'},
 {'label': 'Dictyocaulus viviparus (Dictyocaulus viviparus (PRJEB5116))',
  'value': 'diviviprjeb5116'},
 {'label': 'Caenorhabditis becei (Caenorhabditis becei (PRJEB28243))',
  'value': 'cabeceprjeb28243'},
 {'label': 'Paragonimus westermani (Paragonimus westermani (PRJNA454344))',
  'value': 'pawestprjna454344'},
 {'label': 'Thelazia callipaeda (Thelazia callipaeda (PRJEB1205))',
  'value': 'thcallprjeb1205'},
 {'label': 'Meloidogyne javanica (Meloidogyne javanica (PRJEB8714))',
  'value': 'mejavaprjeb8714'},
 {'label': 'Fasciola hepatica (Fasciola hepatica (PRJEB25283))',
  'value': 'fahepaprjeb25283'},
 {'label': 'Caenorhabditis japonica (Caenorhabditis japonica (PRJNA12591) [WS276])',
  'value': 'cajapoprjna12591'},
 {'label': 'Loa loa (Loa loa (PRJNA24608))', 'value': 'loloaprjna246086'},
 {'label': 'Echinococcus oligarthrus (Echinococcus oligarthrus (PRJEB31222))',
  'value': 'ecoligprjeb31222'},
 {'label': 'Trichuris suis (Trichuris suis (PRJNA179528))',
  'value': 'trsuisprjna179528'},
 {'label': 'Pristionchus fissidentatus (Pristionchus fissidentatus (PRJEB27334))',
  'value': 'prfissprjeb27334'},
 {'label': 'Meloidogyne enterolobii (Meloidogyne enterolobii (PRJNA340324))',
  'value': 'meenteprjna340324'},
 {'label': 'Clonorchis sinensis (Clonorchis sinensis (PRJNA386618))',
  'value': 'clsineprjna386618'},
 {'label': 'Pristionchus japonicus (Pristionchus japonicus (PRJEB27334))',
  'value': 'prjapoprjeb27334'},
 {'label': 'Bursaphelenchus xylophilus (Bursaphelenchus xylophilus (PRJEA64437))',
  'value': 'buxyloprjea64437'},
 {'label': 'Strongyloides papillosus (Strongyloides papillosus (PRJEB525))',
  'value': 'stpapiprjeb525'},
 {'label': 'Trichinella papuae (Trichinella papuae (PRJNA257433))',
  'value': 'trpapuprjna257433'},
 {'label': 'Strongyloides stercoralis (Strongyloides stercoralis (PRJEB528))',
  'value': 'ststerprjeb528'},
 {'label': 'Schistosoma mansoni (Schistosoma mansoni (PRJEA36577))',
  'value': 'scmansprjea36577'},
 {'label': 'Caenorhabditis sp. 26 LS-2015 (Caenorhabditis zanzibari (PRJEB12596))',
  'value': 'cazanzprjeb12596'},
 {'label': 'Taenia asiatica (Taenia asiatica (PRJEB532))',
  'value': 'taasiaprjeb532'},
 {'label': 'Macrostomum lignano (Macrostomum lignano (PRJNA284736))',
  'value': 'malignprjna284736'},
 {'label': 'Caenorhabditis bovis (Caenorhabditis bovis (PRJEB34497))',
  'value': 'caboviprjeb34497'},
 {'label': 'Opisthorchis felineus (Opisthorchis felineus (PRJNA413383))',
  'value': 'opfeliprjna413383'},
 {'label': 'Schistosoma mattheei (Schistosoma mattheei (PRJEB523))',
  'value': 'scmattprjeb523'},
 {'label': 'Panagrolaimus sp. PS1159 (Panagrolaimus ps1159 (PRJEB32708))',
  'value': 'paps11prjeb32708'},
 {'label': 'Caenorhabditis briggsae (Caenorhabditis briggsae (PRJNA10731) [WS276])',
  'value': 'cabrigprjna10731'},
 {'label': 'Oryza sativa Indica Group (Oryza sativa Indica Group)',
  'value': 'oindica'},
 {'label': 'Ananas comosus (Ananas comosus)', 'value': 'acomosus'},
 {'label': 'Oryza rufipogon (Oryza rufipogon)', 'value': 'orufipogon'},
 {'label': 'Chenopodium quinoa (Chenopodium quinoa)', 'value': 'cquinoa'},
 {'label': 'Oryza barthii (Oryza barthii)', 'value': 'obarthii'},
 {'label': 'Cynara cardunculus var. scolymus (Cynara cardunculus)',
  'value': 'ccardunculus'},
 {'label': 'Actinidia chinensis var. chinensis (Actinidia chinensis)',
  'value': 'achinensis'},
 {'label': 'Lupinus angustifolius (Lupinus angustifolius)',
  'value': 'langustifolius'},
 {'label': 'Kalanchoe fedtschenkoi (Kalanchoe fedtschenkoi)',
  'value': 'kfedtschenkoi'},
 {'label': 'Solanum tuberosum (Solanum tuberosum)', 'value': 'stuberosum'},
 {'label': 'Triticum aestivum (Triticum aestivum Stanley)',
  'value': 'tastanley'},
 {'label': 'Triticum aestivum (Triticum aestivum Weebill)',
  'value': 'taweebil'},
 {'label': 'Papaver somniferum (Papaver somniferum)', 'value': 'psomniferum'},
 {'label': 'Medicago truncatula (Medicago truncatula)',
  'value': 'mtruncatula'},
 {'label': 'Ipomoea triloba (Ipomoea triloba)', 'value': 'itriloba'},
 {'label': 'Olea europaea var. sylvestris (Olea europaea var. sylvestris)',
  'value': 'oesylvestris'},
 {'label': 'Chondrus crispus (Chondrus crispus)', 'value': 'ccrispus'},
 {'label': 'Brassica napus (Brassica napus)', 'value': 'bnapus'},
 {'label': 'Capsicum annuum (Capsicum annuum)', 'value': 'cannuum'},
 {'label': 'Ostreococcus lucimarinus CCE9901 (Ostreococcus lucimarinus)',
  'value': 'olucimarinus'},
 {'label': 'Juglans regia (Juglans regia)', 'value': 'jregia'},
 {'label': 'Vitis vinifera (Vitis vinifera)', 'value': 'vvinifera'},
 {'label': 'Brassica oleracea var. oleracea (Brassica oleracea)',
  'value': 'boleracea'},
 {'label': 'Marchantia polymorpha (Marchantia polymorpha)',
  'value': 'mpolymorpha'},
 {'label': 'Saccharum spontaneum (Saccharum spontaneum)',
  'value': 'sspontaneum'},
 {'label': 'Cyanidioschyzon merolae strain 10D (Cyanidioschyzon merolae)',
  'value': 'cmerolae'},
 {'label': 'Oryza glaberrima (Oryza glaberrima)', 'value': 'oglaberrima'},
 {'label': 'Gossypium raimondii (Gossypium raimondii)', 'value': 'graimondii'},
 {'label': 'Glycine max (Glycine max)', 'value': 'gmax'},
 {'label': 'Setaria viridis (Setaria viridis)', 'value': 'sviridis'},
 {'label': 'Triticum urartu (Triticum urartu)', 'value': 'turartu'},
 {'label': 'Triticum aestivum (Triticum aestivum Cadenza)',
  'value': 'tacadenza'},
 {'label': 'Physcomitrium patens (Physcomitrium patens)', 'value': 'ppatens'},
 {'label': 'Sesamum indicum (Sesamum indicum)', 'value': 'sindicum'},
 {'label': 'Triticum aestivum (Triticum aestivum Norin61)',
  'value': 'tanorin61'},
 {'label': 'Prunus avium (Prunus avium)', 'value': 'pavium'},
 {'label': 'Triticum aestivum (Triticum aestivum Arinalrfor)',
  'value': 'taarinalrfor'},
 {'label': 'Nymphaea colorata (Nymphaea colorata)', 'value': 'ncolorata'},
 {'label': 'Triticum aestivum (Triticum aestivum Claire)',
  'value': 'taclaire'},
 {'label': 'Daucus carota subsp. sativus (Daucus carota)', 'value': 'dcarota'},
 {'label': 'Cucumis sativus (Cucumis sativus)', 'value': 'csativus'},
 {'label': 'Eucalyptus grandis (Eucalyptus grandis)', 'value': 'egrandis'},
 {'label': 'Oryza brachyantha (Oryza brachyantha)', 'value': 'obrachyantha'},
 {'label': 'Arabidopsis thaliana (Arabidopsis thaliana)',
  'value': 'athaliana'},
 {'label': 'Leersia perrieri (Leersia perrieri)', 'value': 'lperrieri'},
 {'label': 'Phaseolus vulgaris (Phaseolus vulgaris)', 'value': 'pvulgaris'},
 {'label': 'Populus trichocarpa (Populus trichocarpa)',
  'value': 'ptrichocarpa'},
 {'label': 'Oryza glumipatula (Oryza glumipatula)', 'value': 'oglumipatula'},
 {'label': 'Oryza nivara (Oryza nivara)', 'value': 'onivara'},
 {'label': 'Triticum aestivum (Triticum aestivum Landmark)',
  'value': 'talandmark'},
 {'label': 'Triticum aestivum (Triticum aestivum Lancer)',
  'value': 'talancer'},
 {'label': 'Oryza sativa Japonica Group (Oryza sativa Japonica Group)',
  'value': 'osativa'},
 {'label': 'Dioscorea cayenensis subsp. rotundata (Dioscorea rotundata)',
  'value': 'drotundata'},
 {'label': 'Hordeum vulgare subsp. vulgare (Hordeum vulgare TRITEX)',
  'value': 'hvtritex'},
 {'label': 'Triticum aestivum (Triticum aestivum Robigus)',
  'value': 'tarobigus'},
 {'label': 'Triticum spelta (Triticum spelta)', 'value': 'tspelta'},
 {'label': 'Zea mays (Zea mays)', 'value': 'zmays'},
 {'label': 'Triticum aestivum (Triticum aestivum Mace)', 'value': 'tamace'},
 {'label': 'Corchorus capsularis (Corchorus capsularis)',
  'value': 'ccapsularis'},
 {'label': 'Musa acuminata subsp. malaccensis (Musa acuminata)',
  'value': 'macuminata'},
 {'label': 'Triticum aestivum (Triticum aestivum Sy Mattis)',
  'value': 'tamattis'},
 {'label': 'Triticum aestivum (Triticum aestivum Paragon)',
  'value': 'taparagon'},
 {'label': 'Cucumis melo (Cucumis melo)', 'value': 'cmelo'},
 {'label': 'Manihot esculenta (Manihot esculenta)', 'value': 'mesculenta'},
 {'label': 'Prunus persica (Prunus persica)', 'value': 'ppersica'},
 {'label': 'Brachypodium distachyon (Brachypodium distachyon)',
  'value': 'bdistachyon'},
 {'label': 'Nicotiana attenuata (Nicotiana attenuata)', 'value': 'nattenuata'},
 {'label': 'Oryza meridionalis (Oryza meridionalis)',
  'value': 'omeridionalis'},
 {'label': 'Trifolium pratense (Trifolium pratense)', 'value': 'tpratense'},
 {'label': 'Arabidopsis lyrata subsp. lyrata (Arabidopsis lyrata)',
  'value': 'alyrata'},
 {'label': 'Camelina sativa (Camelina sativa)', 'value': 'csativa'},
 {'label': 'Cannabis sativa (Cannabis sativa female)', 'value': 'csfemale'},
 {'label': 'Selaginella moellendorffii (Selaginella moellendorffii)',
  'value': 'smoellendorffii'},
 {'label': 'Eutrema salsugineum (Eutrema salsugineum)',
  'value': 'esalsugineum'},
 {'label': 'Arabis alpina (Arabis alpina)', 'value': 'aalpina'},
 {'label': 'Triticum turgidum subsp. durum (Triticum turgidum)',
  'value': 'tturgidum'},
 {'label': 'Eragrostis tef (Eragrostis tef)', 'value': 'etef'},
 {'label': 'Triticum aestivum (Triticum aestivum Jagger)',
  'value': 'tajagger'},
 {'label': 'Oryza longistaminata (Oryza longistaminata)',
  'value': 'olongistaminata'},
 {'label': 'Rosa chinensis (Rosa chinensis)', 'value': 'rchinensis'},
 {'label': 'Helianthus annuus (Helianthus annuus)', 'value': 'hannuus'},
 {'label': 'Citrullus lanatus (Citrullus lanatus)', 'value': 'clanatus'},
 {'label': 'Triticum aestivum (Triticum aestivum)', 'value': 'taestivum'},
 {'label': 'Citrus clementina (Citrus clementina)', 'value': 'cclementina'},
 {'label': 'Sorghum bicolor (Sorghum bicolor)', 'value': 'sbicolor'},
 {'label': 'Theobroma cacao (Theobroma cacao Belizian Criollo B97-61/B2)',
  'value': 'tccriollo'},
 {'label': 'Aegilops tauschii subsp. strangulata (Aegilops tauschii)',
  'value': 'atauschii'},
 {'label': 'Chara braunii (Chara braunii)', 'value': 'cbraunii'},
 {'label': 'Asparagus officinalis (Asparagus officinalis)',
  'value': 'aofficinalis'},
 {'label': 'Pistacia vera (Pistacia vera)', 'value': 'pvera'},
 {'label': 'Panicum hallii var. hallii (Panicum hallii HAL2)',
  'value': 'phallii'},
 {'label': 'Panicum hallii (Panicum hallii FIL2)', 'value': 'phfil2'},
 {'label': 'Vigna angularis (Vigna angularis)', 'value': 'vangularis'},
 {'label': 'Setaria italica (Setaria italica)', 'value': 'sitalica'},
 {'label': 'Amborella trichopoda (Amborella trichopoda)',
  'value': 'atrichopoda'},
 {'label': 'Triticum aestivum (Triticum aestivum Julius)',
  'value': 'tajulius'},
 {'label': 'Triticum dicoccoides (Triticum dicoccoides)',
  'value': 'tdicoccoides'},
 {'label': 'Arabidopsis halleri subsp. gemmifera (Arabidopsis halleri)',
  'value': 'ahalleri'},
 {'label': 'Oryza punctata (Oryza punctata)', 'value': 'opunctata'},
 {'label': 'Hordeum vulgare subsp. vulgare (Hordeum vulgare GoldenPromise)',
  'value': 'hvgoldenpromise'},
 {'label': 'Eragrostis curvula (Eragrostis curvula)', 'value': 'ecurvula'},
 {'label': 'Solanum lycopersicum (Solanum lycopersicum)',
  'value': 'slycopersicum'},
 {'label': 'Hordeum vulgare subsp. vulgare (Hordeum vulgare)',
  'value': 'hvulgare'},
 {'label': 'Brassica rapa (Brassica rapa)', 'value': 'brapa'},
 {'label': 'Coffea canephora (Coffea canephora)', 'value': 'ccanephora'},
 {'label': 'Theobroma cacao (Theobroma cacao Matina 1-6)', 'value': 'tcacao'},
 {'label': 'Chlamydomonas reinhardtii (Chlamydomonas reinhardtii)',
  'value': 'creinhardtii'},
 {'label': 'Prunus dulcis (Prunus dulcis)', 'value': 'pdulcis'},
 {'label': 'Galdieria sulphuraria (Galdieria sulphuraria)',
  'value': 'gsulphuraria'},
 {'label': 'Malus domestica (Malus domestica Golden)', 'value': 'mdgolden'},
 {'label': 'Vigna radiata var. radiata (Vigna radiata)', 'value': 'vradiata'},
 {'label': 'Beta vulgaris subsp. vulgaris (Beta vulgaris)',
  'value': 'bvulgaris'},
 {'label': 'Quercus lobata (Quercus lobata)', 'value': 'qlobata'},
 {'label': 'Trypanosoma brucei (Trypanosoma brucei)', 'value': 'tbrucei'},
 {'label': 'Plasmodium falciparum 3D7 (Plasmodium falciparum 3D7)',
  'value': 'pfalciparum'},
 {'label': 'Plasmodium knowlesi strain H (Plasmodium knowlesi)',
  'value': 'pknowlesi'},
 {'label': 'Globisporangium irregulare DAOM BR486 (Pythium irregulare)',
  'value': 'pirregulare'},
 {'label': 'Albugo laibachii Nc14 (Albugo laibachii)', 'value': 'alaibachii'},
 {'label': 'Guillardia theta CCMP2712 (Guillardia theta CCMP2712)',
  'value': 'gtheta'},
 {'label': 'Phytophthora infestans T30-4 (Phytophthora infestans)',
  'value': 'pinfestans'},
 {'label': 'Phytopythium vexans DAOM BR484 (Pythium vexans)',
  'value': 'pvexans'},
 {'label': 'Globisporangium ultimum DAOM BR144 (Pythium ultimum)',
  'value': 'pultimum'},
 {'label': 'Pseudo-nitzschia multistriata (Pseudo-nitzschia multistriata)',
  'value': 'pmultistriata'},
 {'label': 'Paramecium tetraurelia (Paramecium tetraurelia)',
  'value': 'ptetraurelia'},
 {'label': 'Plasmodium vivax (Plasmodium vivax)', 'value': 'pvivax'},
 {'label': 'Hyaloperonospora arabidopsidis Emoy2 (Hyaloperonospora arabidopsidis)',
  'value': 'harabidopsidis'},
 {'label': 'Tetrahymena thermophila SB210 (Tetrahymena thermophila)',
  'value': 'tthermophila'},
 {'label': 'Phaeodactylum tricornutum CCAP 1055/1 (Phaeodactylum tricornutum)',
  'value': 'ptricornutum'},
 {'label': 'Phytophthora kernoviae 00238/432 (Phytophthora kernoviae)',
  'value': 'pkernoviae'},
 {'label': 'Plasmodium chabaudi chabaudi (Plasmodium chabaudi)',
  'value': 'pchabaudi'},
 {'label': 'Bigelowiella natans CCMP2755 (Bigelowiella natans)',
  'value': 'bnatans'},
 {'label': 'Pythium arrhenomanes ATCC 12531 (Pythium arrhenomanes)',
  'value': 'parrhenomanes'},
 {'label': 'Thalassiosira pseudonana CCMP1335 (Thalassiosira pseudonana)',
  'value': 'tpseudonana'},
 {'label': 'Entamoeba histolytica HM-1:IMSS (Entamoeba histolytica)',
  'value': 'ehistolytica'},
 {'label': 'Toxoplasma gondii ME49 (Toxoplasma gondii ME49)',
  'value': 'tgondii'},
 {'label': 'Phytophthora ramorum (Phytophthora ramorum)', 'value': 'pramorum'},
 {'label': 'Pythium aphanidermatum DAOM BR444 (Pythium aphanidermatum)',
  'value': 'paphanidermatum'},
 {'label': 'Phytophthora parasitica P1569 (Phytophthora parasitica)',
  'value': 'pparasitica'},
 {'label': 'Globisporangium iwayamae DAOM BR242034 (Pythium iwayamai)',
  'value': 'piwayamai'},
 {'label': 'Phytophthora sojae (Phytophthora sojae)', 'value': 'psojae'},
 {'label': 'Leishmania major strain Friedlin (Leishmania major)',
  'value': 'lmajor'},
 {'label': 'Phytophthora lateralis MPF4 (Phytophthora lateralis)',
  'value': 'plateralis'},
 {'label': 'Plasmodium berghei ANKA (Plasmodium berghei)',
  'value': 'pberghei'},
 {'label': 'Giardia lamblia ATCC 50803 (Giardia lamblia)',
  'value': 'glamblia'},
 {'label': 'Emiliania huxleyi CCMP1516 (Emiliania huxleyi)',
  'value': 'ehuxleyi'},
 {'label': 'Dictyostelium discoideum AX4 (Dictyostelium discoideum)',
  'value': 'ddiscoideum'}]

# # Esqueleto
# Vamos a usar una barra lateral de navegación por lo cualvamos a tener que definir cada una de las estructuras que van a estar en cada uno de los apartados de contenido

# In[4]:


# F O R M A T O   D E   L A   B A R R A  Y  C O N T E N I D O

# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",  #Se mantiene aunque tu hagas mas chica la ventana
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "22rem",     #Ancho del sidebar 
    "padding": "2rem 1rem", #Cuanto de espacio hay arriba antes de que empiece el texto y el espacio que debe quedar a la derecha
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "25rem",  #Cuanto deja de espacio dsde TODA la pantalla
    "margin-right": "0rem",  #Margen a la dercha
    "padding": "0rem 0rem",  #Espacio arriba y a la derecha
}

sidebar = html.Div(
    [
        dcc.Markdown("""**Selecciona el analisis que deseas realizar**"""),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Introducción", href="/", active="exact"),
                dbc.NavLink("Plots", href="/plots", active="exact"),
                dbc.NavLink("Analisis de enriqueciemiento", href="/ea", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)


# In[5]:


encabezado  = dbc.Row([
    dbc.Col(html.A(html.Img(src="assets/UNAM.png",style={'height':'130%', 'width':'95%'},className="d-flex align-self-center"),
                   href="https://www.unam.mx/",target='_blank'), 
            width={"size":2,"offset":0}),

    dbc.Col(html.H2("Analisis  RNA-seq",style={"color":"#8a070d"},className="text-center" "mb-4" "h50"),
            width={"size":4,"offset":2}),

    dbc.Col(html.A(html.Img(src="assets/IFC.png",style={'height':'105%', 'width':'70%'},className="d-flex align-self-center"),
                   href="http://www.ifc.unam.mx/",target='_blank'),
            width={"size":2,"offset":2})
],justify="center", align="center")


# In[6]:


Intro = html.Div([
    html.H4("Introducción"),
    html.P([html.Span("Esta página fue diseñada mediante dash-plotly y otras librerias de python, tiene como objetivo ayudar a explorar los resultados obtenidos de "),
            html.A("DESeq2", href='https://genomebiology.biomedcentral.com/articles/10.1186/s13059-014-0550-8', target="_blank"),
            html.Span(" de una manera interactiva. En esta seccion encontraras una breve descripción de los objetos con los cuales podras interactuar.")]),
    html.Span("A lo largo de las paginas las instrucciónes se marcan en azul",style={"color":"#052080"}),
    html.H4("Objetos interactivos"),
    html.H6("Gráficos"),
    html.P("Diseñamos los gráficos para analizar los datos de una forma rápida y fácil. Ten en cuenta que si colocas el cursor sobre un punto, se mostrará la información asociada, y si vas a la esquina superior derecha del gráfico, encontrarás una barra de herramientas, que te permitira desplazarte dentro de la figura o descargar la imagen. Los graficos se pueden descargar como figuras estaticas. En el siguiente menu desplegable podras escoger el tipo de formato en el cual se descargaran las imagenes (de manera predeterminada esta png). "),

    html.Br(),
    
    dbc.Row([
        dbc.Col(html.Span("Escoge el formato en cual quieres descargar tus plots",style={"color":"#052080"})),
        dbc.Col(dcc.Dropdown(
            id="format-dw-img",
            options=[{'label': 'svg', 'value': 'svg'},
                     {'label': 'png', 'value': 'png'},
                     {'label': 'jpeg', 'value': 'jpeg'},
                     {'label': 'webp', 'value': 'webp'}],
            value='png',style={'width':"45%"}))],
        justify="center", align="center"),
    html.Br(),
    html.H6("Tablas"),
    html.P("Las tablas también son objetos interactivos. Con el ícono de flechas 🔼🔽 se puede ordenar toda la tabla segun los valores de una columna en especifico.Con el icono de ojo podra ocultar columnas, esta misma acción se podra realizar con el botón de toggle columns."),
])


# In[7]:


p_container = html.Div([
    html.H4("Introducción"),
    html.P("La mayoria de los analisis requieren de un valor de p, que permite diferenciar los resultados que son el producto de un muestreo aleatorio de los resultados que son estadísticamente significativos. Por lo general, se acepta un valor p de 0,05, pero tal vez pueda probar con 0,01 o menos para que los datos sean más sólidos. Otro valor que queremos explicar es el log2FoldChange (lFC) que nos informa de cambios en la expresión relativa. Como se calcula con un logaritmo en base 2. Un lFC de 1 indica una que el gen se ha expresado al doble, mientras que un lFC de -1 indica que la expresión del gen se ha reducido a la mitad. Las gráficas solicitarán un valor de lFC, para usarlo como umbral y filtrar cambios en la expresión.  "),
    html.P("Los conteos que se muestran dentro del MA-plot y el gene-count plot refieren a los conteos normalizados por DESeq2. "),

    html.H4("Gráficos"),
    html.Span('1. Al mismo tiempo carga los archivos de DESeq2 correspondientes a los resultados y conteos. Los nombres de los archivos deben de contener en el nombre "results" y "counts" respectivamente.', style={"color":"#052080"}),html.Br(),
    html.Span("2. Inserta el valor de p y el umbral de log2FoldChangue (lfct).", style={"color":"#052080"}), html.Br(),
    html.Span("3. Si necesitas observar (no es un paso obligatorio) los conteos de un gene especifico en cada una de los grupos de interes, con el cuadro de entrada puedes ingresar el nombre del gene o el id.",style={"color":"#052080"}),html.Br(),
    html.Span("Se muestra un interruptor rojo en el estado activado, lo que le permite ver datos no significativos. Si desea mostrar solo los datos significativos, puede desactivarlo.", style={"color":"#052080"}),html.Br(),
    html.Br(),
    
    dbc.Row(dcc.Upload(html.Button('Upload File',style={'width':"140.5%"},className="btn btn-warning"),style={'display':'inline-block'},id='upload-data',multiple=True)),
    
    dbc.Row([
        dbc.Col([
            dcc.Input(
                id='my_pvalue',
                type="number",
                placeholder="p-value",          # A hint to the user of what can be entered in the control
                debounce=False,                       # Changes to input are sent to Dash server only on enter or losing focus
                min=0, max=1, step=0.000001,         # Ranges of numeric value. Step refers to increments
                minLength=0, maxLength=8,            # Ranges for character length inside input box
                autoComplete='on',
                required=True,                       # Require user to insert something into input box
                size="8",                            # Number of characters that will be visible inside box
                persistence=True,
                persistence_type="session",
                style={'display':'inline-block'}),

            dcc.Input(
                id='my_lfct',
                type="number",
                placeholder="lfct",  
                debounce=False,                          
                min=0, max=10, step=0.000001,         
                minLength=0, maxLength=8,          
                autoComplete='on',               
                required=True,                    
                size="20",
                persistence=True,
                persistence_type="session",
                style={'display':'inline-block','width':"10%"}),
            
            daq.BooleanSwitch(
            id='my_ns-button', color="red",style={'display':'inline-block'},
            on=True)]),
        
        dbc.Col([
            
            dcc.Input(
            id='my_GENEname',
            type="text",
            placeholder="GENEname",  
            debounce=False,                          
            min=0, max=10, step=0.000001,         
            minLength=0, maxLength=20,          
            autoComplete='on',               
            required=False,                    
            size="20",
            style={'display':'inline-block'}
            ),

            dcc.RadioItems(
            id="count_type",
            options=[{'label': 'Gene name', 'value': 'gn'},
                     {'label': 'ID', 'value': 'gid'}],
                value='gn',
                labelStyle={'display': 'inline-block'})])]),
#------------------------------------------P L O T S---------------------------------------------------------------
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="Volcano-plot",figure={}),
            dcc.Graph(id="histo",figure={})]),
    
        dbc.Col([
            dcc.Graph(id="MA-plot",figure={}),
            dcc.Graph(id="Genecount",figure={})])]),
    html.H4("Caracteristicas principales"),
    html.P("Estas son unas tablas interactivas que permiten explorar los mejores genes que tuvieron cambios de expresión (UP / DOWN) de acuerdo a los parámetros elegidos. En la parte derecha se presentan botones que permiten descargar todos los datos significativos."),
    html.Span('1. Elija cuantos cuantos genes quiere ver por tabla', style={"color":"#052080"}),html.Br(),
    html.Span('2. Elija la caracteristica que definira los mejores genes. Como default es plog que refiere al log10 del pvalue ajustado', style={"color":"#052080"}),html.Br(),
    html.Br(),
    
    dbc.Row([
        dbc.Col([
            html.Span("Observemos los mejores ",style={'display':'block'}),
            html.Br(),
            html.Span(" datos segun ",style={'display':'block'})],width={"size":3,"offset":0}),
        
        dbc.Col([
            dcc.Input(
                id='n_features',
                type="number",
                placeholder="#features",  
                debounce=False,                          
                min=0, max=999, step=1,         
                minLength=0, maxLength=3,                         
                required=False,                    
                size="20",
                style={'width':"17%",'display':'block'},
                value=10),
            dcc.Dropdown(
                id="filt-df",
                options=[{'label': 'ID', 'value': 'ID'},
                         {'label': 'Counts', 'value': 'baseMean'},
                         {'label': 'log2FoldChange', 'value': 'log2FoldChange'},
                         {'label': 'lfcSE', 'value': 'lfcSE'},
                         {'label': 'pvalue', 'value': 'pvalue'},
                         {'label': 'padj', 'value': 'padj'},
                         {'label': 'plog', 'value': 'plog'}],
                value='plog',style={'width':"70%",'display':'block'})],width={"size":4,"offset":0}),
        
        dbc.Col([
            html.Button("Download UP genes", id="btn-upcsv",className="btn btn-info",style={'width':"75%",'display':'block'}),
            dcc.Download(id="upcsv"),
    
            html.Button("Download Down genes", id="btn-downcsv",className="btn btn-primary",style={'width':"75%",'display':'block'}),
            dcc.Download(id="downcsv")],width={"size":3,"offset":2})]),
    
    html.Br(),
    dbc.Row([
            
        dbc.Col([html.B("Genes UP",style={'display':'block'}),
                html.Div(id="up-table",style={'display':'block'})],
                width={"size":5,"offset":0}),
        
        dbc.Col([
            html.B("Genes DOWN",style={'display':'block'}),
            html.Div(id="dw-table",style={'display':'block'})],
            width={"size":5,"offset":1})],justify="start"),
])


# In[8]:


sig_ea = html.Div([
    html.H4("Analisis de enriquecimiento de genes"),
    html.P([
        html.Span("Se utiliza el paquete de "),
        html.A("g_Proflier", href='https://biit.cs.ut.ee/gprofiler/gost', target="_blank"),
        html.Span(" para realizar el analisis de enriquecimiento. G:Profiler asigna genes a fuentes de información funcional conocidas y detecta términos estadísticamente significativamente enriquecidos. Ten en cuenta que este paquete te da la oportunidad de elegir entre 500 organismos")]),
    html.Br(),
    html.Span('Primero vamos a filtrar solo los datos que tienen cambios de expresion relativa significativos.'),html.Br(),
    html.Span('1. Carga los archivos y asigna un valor de p y lfct (si ya los cargaste en la pagina de plots ya no es necesario.)', style={"color":"#052080"}),html.Br(),
    html.Span('2. Para calcular el análisis de enriquecimiento, elija el organismo (el valor predeterminado es ratón)', style={"color":"#052080"}),html.Br(),
    html.Span('3. Elija una característica (para ordenar) y la cantidad de características principales que desea ver en las tablas', style={"color":"#052080"}),html.Br(),
    
    html.Br(),
    dbc.Row([dbc.Col(html.P("Datos & Parametros",style={'display':'block',"color":"#052080"})),
            dbc.Col(html.P("Filtros de EA",style={'display':'block',"color":"#052080"})),
            dbc.Col(html.P("Todos los datos EA",style={'display':'block',"color":"#052080"}))]),
    dbc.Row([
       dbc.Col([dcc.Upload(html.Button('Upload File',style={'width':"34%"},className="btn btn-warning",),style={'display':'block'},id='upload-data',multiple=True),
                dcc.Input(
                    id='my_pvalue',
                    type="number",
                    placeholder="p-value",          # A hint to the user of what can be entered in the control
                    debounce=False,                       # Changes to input are sent to Dash server only on enter or losing focus
                    min=0, max=1, step=0.000001,         # Ranges of numeric value. Step refers to increments
                    minLength=0, maxLength=8,            # Ranges for character length inside input box
                    autoComplete='on',
                    required=False,                       # Require user to insert something into input box
                    size="8",                            # Number of characters that will be visible inside box
                    persistence=True,
                    persistence_type="session",
                    style={'display':'block','width':"34%"}),
       
               dcc.Input(
                   id='my_lfct',
                   type="number",
                   placeholder="lfct",  
                   debounce=False,                          
                   min=0, max=10, step=0.000001,         
                   minLength=0, maxLength=8,          
                   autoComplete='on',               
                   required=False,                    
                   size="20",
                   persistence=True,
                   persistence_type="session",
                   style={'display':'block','width':"34%"})]),
       
       dbc.Col([
                dcc.Dropdown(id = "organism-dp",
                             options = organismos,
                             value = "mmusculus",
                             style={'width':"70%",'display':'block'}),
                
                dcc.Dropdown(id="filt1-df",
                             options=[{'label': 'Source', 'value': 'source'},
                                      {'label': 'Native', 'value': 'native'},
                                      {'label': 'Name', 'value': 'name'},
                                      {'label': 'p value', 'value': 'p_value'},
                                      {'label': 'Significant', 'value': 'significant'},
                                      {'label': 'Term size', 'value': 'term_size'},
                                      {'label': 'Query size', 'value': 'query_size'},
                                      {'label': 'Intersection size', 'value': 'intersection_size'},
                                      {'label': 'Effective Domain size', 'value': 'effective_domain_size'},
                                      {'label': 'Precision', 'value': 'precision'},
                                      {'label': 'Recall', 'value': 'recall'}],
                             value='p_value',
                             style={'width':"70%",'display':'block'}),

                dcc.Input(id='n_features_ea',
                          type="number",
                          placeholder="#features",  
                          debounce=False,                          
                          min=0, max=100, step=1,         
                          minLength=0, maxLength=3,                         
                          required=False,                    
                          size="20",
                          style={'width':"49%",'display':'block'},
                          value=10)]),

    dbc.Col([
        html.Button("Download EA UP", id="btn-ea-upcsv",className="btn btn-info",style={'width':"45%",'display':'block'}),
        dcc.Download(id="eaupcsv"),
        
        html.Button("Download EA DOWN", id="btn-ea-downcsv",className="btn btn-primary",style={'width':"45%",'display':'block'}),
        dcc.Download(id="eadowncsv"),
        
        html.Button("Download EA SIG", id="btn-ea-sigcsv",className="btn btn-secondary",style={'width':"45%",'display':'block'}),
        dcc.Download(id="easigcsv")])]),
    
    html.Br(),
    html.Br(),
    html.H4("Caracteristicas principales"),
    html.P([
        html.Span("Se trata de unas tablas interactivas que permiten explorar el análisis de enriquecimiento de los genes que tuvieron cambios de expresión (UP / DOWN) según los parámetros elegidos. Para más información puede consultar el "),
        html.A("significado de cada columna", href='https://biit.cs.ut.ee/gprofiler/page/apis', target="_blank"),]),
    

    dbc.Row([
        dbc.Col(html.Div(id="up-ea", style = {'display': 'inline-block'}),width={"size":5,"offset":0}),
        dbc.Col(html.Div(id="dw-ea", style = {'display': 'inline-block'}),width={"size":5,"offset":1}),
    ],justify="start"),
        
    html.Br(),
    
#------------------------------------P L O T S -- E N R I Q U E C I M I E N T O ---------------------------------------------------------------
    html.H4("Graficos de EA"),
    html.Span("Los gráficos muestran solo los datos significativos (p <0,05). En cada una de las barras se muestra el intersection_size, que representa cuantos genes corresponden a esa categoría"),
    html.Br(),
    dcc.Tabs(id="tabs", value='tab-up', children=[
        dcc.Tab(label='UP genes', value='tab-up'),
        dcc.Tab(label='DOWN genes', value='tab-down')]),
    html.Div(id='tabs-content'),
])


# # Iniciemos la app 

# In[9]:


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SIMPLEX],
               meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])   


# In[10]:


app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content,
    dcc.Store(id="counts_store"),
    dcc.Store(id="results_store"),
    dcc.Store(id="img-format"),
])


# # Aca definimos las funciones o callback
# El orden en la cual se definen es:
# * URL sidebar
# * Store data
# * Store img format
# * Volcano MA plot y el histograma
# * Conteos por replica experimental
# * Tablas de top features
# * Boton descarga genes UP
# * Boton desgarga genes DOWN
# * Tablas de enriquecimiento
# * Plots enriquecimiento
# * Boton descarga analisis de enriquecimiento UP
# * Boton descarga analisis de enriquecimiento DOWN
# * Boton descarga analisis de enriquecimiento TODOS significativos

# In[11]:


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return [encabezado,html.Hr(),Intro]
    elif pathname == "/plots":
        return [encabezado,p_container]
    elif pathname == "/ea":
        return [encabezado, html.Hr(), sig_ea]
    # If the user tries to reach a different page, return a 404 message
    else:
        return html.Div([
            html.H1("404: Not found", className="bg-danger text-white"),
            html.H1(f"The pathname {pathname} was not recognised...") ])


# In[12]:


@app.callback(
    Output(component_id="counts_store", component_property='data'),
    Output(component_id="results_store", component_property='data'),
    Input('upload-data', 'contents'),                                    #Archivos
    State('upload-data', 'filename'),
)
def store_data(list_of_contents, list_of_names):
    if list_of_contents is not None:
        for contents, filename, in zip(list_of_contents, list_of_names):
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            if 'tsv' in filename:
                if "results" in filename:
                    DEseq = pd.read_csv(io.StringIO(decoded.decode('utf-8')),sep="\t")
                elif "counts" in filename:
                    counts = pd.read_csv(io.StringIO(decoded.decode('utf-8')),sep="\t")
    return (counts.to_dict("dict"), DEseq.to_dict("dict"))


# In[13]:


@app.callback(
    Output(component_id="img-format", component_property='data'),
    Input(component_id="format-dw-img", component_property="value")
)
def download_img_format(f):
    svg = {'toImageButtonOptions': {'format': 'svg','filename': 'custom_image','height': 500,
                                    'width': 700,'scale': 1},
          'displaylogo': False}
    png = {'toImageButtonOptions': {'format': 'png', 'filename': 'custom_image','height': 500,
                                   'width': 700,'scale': 1 },
          'displaylogo': False}

    jpeg = {'toImageButtonOptions': {'format': 'jpeg', 'filename': 'custom_image','height': 500,
                                    'width': 700,'scale': 1},
           'displaylogo': False}

    webp = {'toImageButtonOptions': {'format': 'webp','filename': 'custom_image','height': 500,
                                    'width': 700,'scale': 1},
           'displaylogo': False}
    if  f=="svg":
        return svg
    elif f=="png":
        return png
    elif f=="jpeg":
        return jpeg
    elif f=="webp":
        return webp


# In[14]:


#********************************Volcano plot , MA plot , histograma*****************************************************   
@app.callback(
    Output(component_id="Volcano-plot", component_property='figure'),    #Volcano plot
    Output(component_id="MA-plot", component_property="figure"),         #MA plot
    Output(component_id="histo", component_property='figure'),           #Histograma genes up/down
    Output(component_id="Volcano-plot", component_property='config'),    #Volcano plot
    Output(component_id="MA-plot", component_property="config"),         #MA plot
    Output(component_id="histo", component_property='config'), 
    
    Input(component_id='my_pvalue', component_property='value'),         #P value
    Input(component_id="my_lfct", component_property='value'),
    Input(component_id="my_ns-button",component_property='on'),          #Boton de significancia
    Input(component_id="results_store", component_property="data"),       #Le pedimos que nos de los resultados
    Input(component_id="img-format", component_property='data'),
)

def update_graph(p,lfc, on, DEseq,f):           
    sig, nsig = pd.DataFrame(DEseq).reset_index().pipe(filter_data,p,lfc)
    sig = sig.rename(columns={'index': 'geneID'})
    nsig = nsig.rename(columns={'index': 'geneID'})
   
    fig_v = go.Figure()
    fig_ma = go.Figure()
    fig_v.update_layout(title="Volcano plot computed with a pvalue < "+ str(p) + " & logFC " +str(lfc) ,title_x=0.5)
    fig_ma.update_layout(title="MA plot computed with a pvalue < "+ str(p) + " & logFC " +str(lfc) ,title_x=0.5)
    
    #--------------------------------Volcano Plot----------------------------------------------
    fig_v.add_trace(go.Scatter(                     #Ploteemos primero los UP           
    x=sig[sig["Status"]=="UP"].log2FoldChange,
    y=sig[sig["Status"]=="UP"].plog,                 
    mode="markers",                                           
    marker_color="red",                       
    text= "Name: "+ sig[sig["Status"]=="UP"].external_gene_name.astype(str) + "<br>ID: " + sig[sig["Status"]=="UP"]["geneID"].astype(str),
    name="UP"))

    fig_v.add_trace(go.Scatter(                     #Ploteemos despues los DOWN            
    x=sig[sig["Status"]=="DOWN"].log2FoldChange,
    y=sig[sig["Status"]=="DOWN"].plog,                  
    mode="markers",                                           
    marker_color="blue",                       
    text= "Name: "+ sig[sig["Status"]=="DOWN"].external_gene_name.astype(str)+ "<br>ID: " + sig[sig["Status"]=="DOWN"]["geneID"].astype(str),
    name="DOWN"))


    fig_v.update_xaxes(title_text="log2 Fold Change")
    fig_v.update_yaxes(title_text="-log10(Pvalue)")

    #----------------------------------MA-plot--------------------------------------------------------------
    fig_ma.add_trace(go.Scatter(
    x=sig[sig["Status"]=="UP"].baseMean, 
    y=sig[sig["Status"]=="UP"].log2FoldChange,
    mode="markers",
    marker_color="red",
    name="UP",
    text="Name: "+ sig[sig["Status"]=="UP"].external_gene_name.astype(str)+"<br>ID: "+sig[sig["Status"]=="UP"]["geneID"].astype(str)))

    fig_ma.add_trace(go.Scatter(
    x=sig[sig["Status"]=="DOWN"].baseMean, 
    y=sig[sig["Status"]=="DOWN"].log2FoldChange,
    mode="markers",
    marker_color="blue",
    name="DOWN",
    text="Name: "+ sig[sig["Status"]=="DOWN"].external_gene_name.astype(str)+"<br>ID: "+sig[sig["Status"]=="DOWN"]["geneID"].astype(str)))
    
    if on:
        fig_v.add_trace(go.Scatter(                    #Plotemos al final los NS                            
        x=nsig[nsig["Status"].isin(["UP","DOWN","None"])].log2FoldChange,
        y=nsig[nsig["Status"].isin(["UP","DOWN","None"])].plog,                  
        mode="markers",                                           
        marker_color="gray",opacity=0.4,                       
        text= "Name: "+ nsig.external_gene_name.astype(str)+ "<br>ID: "+ nsig["geneID"].astype(str),
        name="NS"))
        
        fig_ma.add_trace(go.Scatter(
        x=nsig[nsig["Status"].isin(["UP","DOWN","None"])].baseMean, 
        y=nsig[nsig["Status"].isin(["UP","DOWN","None"])].log2FoldChange,
        mode="markers",
        marker_color="gray",opacity=0.4,
        name="NS",
        text="Name: "+ nsig.external_gene_name.astype(str)+ "<br>ID: "+ nsig["geneID"].astype(str)))

    fig_ma.update_xaxes(title_text="Mean normalized counts")
    fig_ma.update_yaxes(title_text="log2 Fold Change")
    
    
    #-------------------------------------------Histograma  genes UP/DOWN--------------------------------------------
    fig_h = px.histogram(data_frame=sig,x="Status",color="Status", color_discrete_map = {"DOWN":"#5065de", "UP": "#db3535"},
                        category_orders=dict(Status=["DOWN","UP"]))
    fig_h.update_layout(title="Gene Status computed with a pvalue < "+ str(p) + " & logFC " +str(lfc) ,title_x=0.5)

    
    
    return (fig_v, fig_ma, fig_h,f,f,f)

#****************************** Conteos por replica experimental****************************************
#*********************************************************************************************************************
@app.callback(
    Output(component_id='Genecount', component_property='figure'),   #Va a sacar un grafico
    Output(component_id='Genecount', component_property='config'),
    
    Input(component_id='my_GENEname', component_property='value'),   #Va a necesitar un numbre de gene
    Input(component_id="count_type",component_property="value"),     #Tiee que checar si metemos ID o nombre del gene
    Input(component_id="counts_store", component_property="data"),
    Input(component_id="results_store", component_property="data"),
    Input(component_id="img-format", component_property='data'),
    Input(component_id='Volcano-plot', component_property='clickData'),  #
    Input(component_id='MA-plot', component_property='clickData'),
)

def update_graph1(name,tipo,counts, DEseq,f,c_v,c_ma):
    #Generamos una copia del DF de conteos y le agregamos los nombres de los genes
    DEseq = pd.DataFrame(DEseq)
    counts = pd.DataFrame(counts)
    
    dff1 = counts.copy()
    dff1.insert(1,"Name",DEseq.external_gene_name.values)
    ctx = dash.callback_context
    
    if ctx.triggered[0]['prop_id'] == 'my_GENEname.value':
        if tipo == "gn":
            val = dff1[dff1["Name"] == name].values[0]
        elif tipo == "gid": 
            val = dff1[dff1["Unnamed: 0"] == name].values[0]
            
    elif ctx.triggered[0]['prop_id'] == 'MA-plot.clickData':
        name = c_v["points"][0]["text"].split(": ")[1].split("<")[0] 
        val = dff1[dff1["Name"] == name].values[0]
        
    elif ctx.triggered[0]['prop_id'] == 'Volcano-plot.clickData':
        name = c_ma["points"][0]["text"].split(": ")[1].split("<")[0]
        val = dff1[dff1["Name"] == name].values[0]
        
        
# =============================================================================
#     if c_v == None and c_ma == None:
# #     if type(name) is str:
#         if tipo == "gn":
#             val = dff1[dff1["Name"] == name].values[0]
#         elif tipo == "gid": 
#             val = dff1[dff1["Unnamed: 0"] == name].values[0]
#     else:
#         if c_v is not None:
#             name = c_v["points"][0]["text"].split(": ")[1].split("<")[0]    
#         elif c_ma is not None:
#             name = c_ma["points"][0]["text"].split(": ")[1].split("<")[0]
#         val = dff1[dff1["Name"] == name].values[0]
#         
# =============================================================================
    grupos = int( (dff1.shape[1] -2) / 2) 

    new = {"Log10(count+0.5)":[np.log10(i+0.5) for i in (val[2:dff1.shape[1]])],
           "Group":np.ndarray.flatten(np.ndarray.flatten(np.array([["Control"]*grupos,["Experimental"]*grupos])))}

    fig_c = px.strip(new, x="Group", y="Log10(count+0.5)",color="Group",
                   color_discrete_map = {"Control": "firebrick","Experimental":"forestgreen"})

    fig_c.update_layout(title="Count plot for gene " + name ,title_x=0.5)
    fig_c.update_xaxes(type='category')

    
    return (fig_c,f)
           
#******************************* T A B L A S   T O P   F E A T U R E S *****************************************************   
#*********************************************************************************************************************
@app.callback(
    Output(component_id="up-table",component_property="children"),       #Tabla genes regulados UP
    Output(component_id="dw-table",component_property="children"),       #Tabla genes regulados DOWN
    
    Input(component_id='my_pvalue', component_property='value'),         #P value
    Input(component_id="my_lfct", component_property='value'),
    Input(component_id="n_features", component_property='value'),        #Cuantas caracteristicas
    Input(component_id="filt-df", component_property='value'),           #Como filtramos
    Input(component_id="results_store", component_property="data")
)

def update_tables(p,lfc, n, filt, DEseq):  
    DEseq = pd.DataFrame(DEseq).reset_index()
    sig, nsig = filter_data(DEseq,p,lfc)
    sig = sig.rename(columns={'index': 'geneID'})
    
    #------------------------------------------Tablas DOWN UP--------------------------------------------------------
    up_df = sig[sig["Status"]=="UP"]            #DF UP
    dw_df = sig[sig["Status"]=="DOWN"]          #DF DOWN
    
    if filt == "pvalue" or filt == "padj":
        up_df_s = up_df.sort_values([filt],ascending=True).head(n)
        dw_df_s = dw_df.sort_values([filt],ascending=True).head(n)
    else:
        up_df_s = up_df.sort_values([filt],ascending=False).head(n)
        dw_df_s = dw_df.sort_values([filt],ascending=False).head(n)
        
    del(up_df_s['Status'])
    del(dw_df_s['Status'])
    
    up_df_s = up_df_s.round(decimals=2)
    dw_df_s = dw_df_s.round(decimals=2)

    
    return ([dash_table.DataTable(columns=[{"name": i, "id": i,"hideable": True} for i in up_df_s.columns],data=up_df_s.to_dict('records'),
                                  sort_action="native", sort_mode="single",#)]
                                  style_table={
                                      'maxHeight': '50vh',   #Largo de la tabla
                                      'overflowY': 'scroll',
                                      'margin-top': '5vh',
                                      'margin-left': '3vh',
                                      'width': '110%'})],     #Ancho de la tabla
            
            [dash_table.DataTable(columns=[{"name": i, "id": i,"hideable": True} for i in dw_df_s.columns],data=dw_df_s.to_dict('records'),
                                  sort_action="native", sort_mode="single",
                                  style_table={
                                      'maxHeight': '50vh',
                                      'overflowY': 'scroll',
                                      'margin-top': '5vh',
                                      'margin-left': '3vh',
                                      'width': '110%'})])

#**************************************** B O T O N E S - D E S C A R G A S ******************************************
######################################### Boton de genes UP-DW ######################################################
@app.callback(
    Output(component_id="upcsv", component_property="data"),
    
    Input(component_id='my_pvalue', component_property='value'),         #P value
    Input(component_id="my_lfct", component_property='value'),
    Input(component_id="btn-upcsv", component_property="n_clicks"),
    Input(component_id="results_store", component_property="data")
)
def boton_up(p,lfc,n_clicks_up, DEseq):  
    DEseq = pd.DataFrame(DEseq)
    sig, nsig = DEseq.reset_index().pipe(filter_data,p,lfc)
    
    up_df = sig[sig["Status"]=="UP"]            #DF UP
    
    if n_clicks_up >=1:
        return send_data_frame(up_df.to_csv, filename="up.csv")

@app.callback(
    Output(component_id="downcsv", component_property="data"),
    
    Input(component_id='my_pvalue', component_property='value'),         #P value
    Input(component_id="my_lfct", component_property='value'),
    Input(component_id="btn-downcsv", component_property="n_clicks"),
    Input(component_id="results_store", component_property="data")
)
def boton_dw(p,lfc,n_clicks_dw, DEseq):
    DEseq = pd.DataFrame(DEseq)
    sig, nsig = DEseq.reset_index().pipe(filter_data,p,lfc)
    
    dw_df = sig[sig["Status"]=="DOWN"]          #DF DOWN
    
    if n_clicks_dw >=1:
        return send_data_frame(dw_df.to_csv, filename="down.csv")


# In[15]:


#******************************* T A B L A S  D E  E N R I Q U E C I M I E N T O *****************************************************   
@app.callback(
    Output(component_id="up-ea",component_property="children"),          #Tabla analisis enriquecimiento UP
    Output(component_id="dw-ea",component_property="children"),          #Tabla analisis enriquecimiento DOWN
    
    Input(component_id='my_pvalue', component_property='value'),         #P value
    Input(component_id="my_lfct", component_property='value'),
    Input(component_id="organism-dp", component_property='value'),       #Organismo
    Input(component_id="n_features_ea", component_property='value'),        #Cuantas caracteristicas
    Input(component_id="filt1-df", component_property='value'),          #Como filtramos
    Input(component_id="results_store", component_property="data"),
)
def update_df_ea(p,lfc,organismo, n,filt1, DEseq):
    DEseq = pd.DataFrame(DEseq)
    sig, nsig = filter_data(DEseq,p,lfc)
    
    #------------------------------------------Enriquecimiento--------------------------------------------------------
    up_name = list(sig[sig["Status"]=="UP"]["external_gene_name"].values)
    dw_name = list(sig[sig["Status"]=="DOWN"]["external_gene_name"].values)
    
    up_gp = gp.profile(organism=organismo, query=up_name)                   #DF enriquecimiento up
    dw_gp = gp.profile(organism=organismo, query=dw_name)                   #DF enriquecimiento dw

    up_gp_s = up_gp.sort_values([filt1],ascending=False).head(n)             #Filtramos los DF
    dw_gp_s = dw_gp.sort_values([filt1],ascending=False).head(n)
    

    return ([dash_table.DataTable(columns=[{"name": i, "id": i,"hideable": True} for i in up_gp_s.columns],data=up_gp_s.to_dict('records'),
                                 sort_action="native", sort_mode="single",
                                 style_table={
                                      'maxHeight': '50vh',
                                      'overflowY': 'scroll',
                                      'margin-top': '5vh',
                                      'margin-left': '3vh',
                                      'width': '12%'})],
            [dash_table.DataTable(columns=[{"name": i, "id": i,"hideable": True} for i in dw_gp_s.columns],data=dw_gp_s.to_dict('records'),
                                  sort_action="native", sort_mode="single",
                                  style_table={
                                      'maxHeight': '50vh',
                                      'overflowY': 'scroll',
                                      'margin-top': '5vh',
                                      'margin-left': '3vh',
                                      'width': '11%'})])

#******************************* P L O T S   E N R I Q U E C I M I E N T O *****************************************************   
@app.callback(          
    Output("tabs-content", "children"),       #Plot analisis enriquecimiento UP 

    Input(component_id='my_pvalue', component_property='value'),         #P value
    Input(component_id="my_lfct", component_property='value'),
    Input(component_id="organism-dp", component_property='value'),       #Organismo
    Input(component_id="n_features_ea", component_property='value'),        #Cuantas caracteristicas
    Input(component_id="filt1-df", component_property='value'),          #Como filtramos
    Input(component_id="results_store", component_property="data"),
    Input('tabs', 'value'),
    Input(component_id="img-format", component_property='data'),
)

def graphs_ea_tab(p,lfc,organismo, n,filt1, DEseq,tab,f):
    DEseq = pd.DataFrame(DEseq)
    sig, nsig = filter_data(DEseq,p,lfc)
    
    #------------------------------------------Enriquecimiento--------------------------------------------------------
    up_name = list(sig[sig["Status"]=="UP"]["external_gene_name"].values)
    dw_name = list(sig[sig["Status"]=="DOWN"]["external_gene_name"].values)
    
    up_gp = gp.profile(organism=organismo, query=up_name)                   #DF enriquecimiento up
    dw_gp = gp.profile(organism=organismo, query=dw_name)                   #DF enriquecimiento dw

    up_gp_s = up_gp.sort_values([filt1],ascending=False).head(n)             #Filtramos los DF
    dw_gp_s = dw_gp.sort_values([filt1],ascending=False).head(n)

    up_gp_s = up_gp_s[up_gp_s["significant"]==True] 
    dw_gp_s = dw_gp_s[dw_gp_s["significant"]==True]
    
    na_up = up_gp_s["name"].values                                          #Sacamos los nombres
    na_dw = dw_gp_s["name"].values
    
    p_up  = np.log10(up_gp_s["p_value"].values)*-1                          #Sacamos los valores de p
    p_dw  = np.log10(dw_gp_s["p_value"].values)*-1

    fig_up_ea = go.Figure(
        go.Bar(y=na_up, x=p_up, orientation='h',text=up_gp_s["intersection_size"],
               hovertemplate = "p-value: %{x}"+"<br>Count: "+ up_gp_s.intersection_size.astype(str)+"<extra></extra>"))
    
    fig_up_ea.update_traces(marker_color=px.colors.qualitative.Prism, marker_line_color='rgb(0,0,0)')
    fig_up_ea.update_xaxes(title_text="- log10 (p value) ")
    fig_up_ea.update_layout(title="Enrichment analysis UP-genes" ,title_x=0.5)
    
    fig_dw_ea = go.Figure(
        go.Bar(y=na_dw, x=p_dw, orientation='h',text=dw_gp_s["intersection_size"],
               hovertemplate = "p-value: %{x}"+"<br>Count: "+ dw_gp_s.intersection_size.astype(str)+"<extra></extra>"))
    fig_dw_ea.update_traces(marker_color=px.colors.qualitative.Prism, marker_line_color='rgb(0,0,0)')
    fig_dw_ea.update_xaxes(title_text="- log10 (p value) ")
    fig_dw_ea.update_layout(title="Enrichment analysis DOWN-genes" ,title_x=0.5)
    
    if tab == "tab-up":
        return dcc.Graph(figure=fig_up_ea,config=f)
    elif tab =="tab-down":
        return dcc.Graph(figure=fig_dw_ea,config=f)
#***********************************Botones analisis de enriquecimiento ******************************************
######################################### Boton de genes UP-DW ##################################################
@app.callback(
    Output(component_id="eaupcsv", component_property="data"),
    
    Input(component_id='my_pvalue', component_property='value'),         #P value
    Input(component_id="my_lfct", component_property='value'),
    Input(component_id="btn-ea-upcsv", component_property="n_clicks"),
    Input(component_id="organism-dp", component_property='value'),       #Organismo
    Input(component_id="results_store", component_property="data")
)

def boton_eaup(p,lfc,n_clicks_eaup,organismo, DEseq):
    DEseq = pd.DataFrame(DEseq)
    sig, nsig = filter_data(DEseq,p,lfc)
    up_name = list(sig[sig["Status"]=="UP"]["external_gene_name"].values)
    up_gp = gp.profile(organism=organismo, query=up_name)                   #DF enriquecimiento up
    
    if n_clicks_eaup >=1:
        return send_data_frame(up_gp.to_csv, filename="ea-up.csv")

@app.callback(
    Output(component_id="eadowncsv", component_property="data"),
    
    Input(component_id='my_pvalue', component_property='value'),         #P value
    Input(component_id="my_lfct", component_property='value'),
    Input(component_id="btn-ea-downcsv", component_property="n_clicks"),
    Input(component_id="organism-dp", component_property='value'),       #Organismo
    Input(component_id="results_store", component_property="data")
)
def boton_eadw(p,lfc,n_clicks_eadw, organismo, DEseq):
    DEseq = pd.DataFrame(DEseq)
       
    sig, nsig = filter_data(DEseq,p,lfc)
    dw_name = list(sig[sig["Status"]=="DOWN"]["external_gene_name"].values)
    dw_gp = gp.profile(organism=organismo, query=dw_name)                   #DF enriquecimiento dw
    
    if n_clicks_eadw >=1:
        return send_data_frame(dw_gp.to_csv, filename="ea-down.csv")
    
@app.callback(
    Output(component_id="easigcsv", component_property="data"),
    
    Input(component_id='my_pvalue', component_property='value'),         #P value
    Input(component_id="my_lfct", component_property='value'),           #LFCT
    Input(component_id="btn-ea-sigcsv", component_property="n_clicks"),  
    Input(component_id="organism-dp", component_property='value'),       #Organismo
    Input(component_id="results_store", component_property="data")
)   

def boton_easig(p,lfc,n_clicks_eadw, organismo,DEseq): 
    DEseq = pd.DataFrame(DEseq)
    sig, nsig = filter_data(DEseq,p,lfc)
    names = list(sig["external_gene_name"].values)
    sig_gp = gp.profile(organism=organismo, query=names)                   #DF enriquecimiento dw
    
    if n_clicks_eadw >=1:
        return send_data_frame(sig_gp.to_csv, filename="ea-sig.csv")

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
    
# =============================================================================
# if __name__ == '__main__':               #Dash se basa un poco en flask por eso esa sintaxis
#     app.run_server(port = 1919)  
# =============================================================================
    
