### LISTE DES ATTRIBUTS POTENTIELS 



NO\_CLIENT

NO\_COMMANDE 

NO\_DOSSIER

------------------------------------------------------

NOM\_CONTACT\_CLIENT

PRENOM\_CLIENT

NOM\_COMPAGNIE\_CLIENT

ADRESSE\_COMPAGNIE\_CLIENT

VILLE\_COMPAGNIE\_CLIENT

CODE\_POSTAL\_COMPAGNIE\_CLIENT

NUMERO\_TELEPHONE\_COMPAGNIE\_CLIENT

------------------------------------------------------

DATE\_COMMANDE

DATE\_LIMITE\_COMMANDE

PO\_CLIENT\_COMMANDE 

------------------------------------------------------

TYPE\_TRAVAIL

------------------------------------------------------

QUANTITE\_COMMANDE

TYPE\_IMPRESSION 

------------------------------------------------------

FORMAT\_FINAL\_IMPRESSION 

FORMAT\_OUVERT\_IMPRESSION 

RECTO\_VERSO\_IMPRESSION 

TYPE\_ENCRE\_RECTO

TYPE\_ENCRE\_VERSO

TYPE\_PAPIER

------------------------------------------------------

TYPE\_FINITION

NUMEROTAGE\_FINITION 

NOTES\_FINITION  

------------------------------------------------------

NOTES\_COMMANDE

------------------------------------------------------

NO\_SOUS-TRAITANT 

NOM\_SOUS-TRAITANT

PO\_SOUS-TRAITANT

COUT\_SOUS-TRAITANT

------------------------------------------------------

NOTES\_LIVRAISON

QUANTITE\_LIVRAISON

DATE\_LIVRAISON

ADRESSE\_LIVRAISON  

VILLE\_LIVRAISON 

CODE\_POSTAL\_LIVRAISON 

NO\_BON\_LIVRAISON (B/L)

------------------------------------------------------

COUT\_COMMANDE

COUT\_INFOGRAPHIE

COUT\_LIVRAISON







### DÉPENDANCES FONCTIONNELLES ENTRE LES ATTRIBUTS 



*Il peut y avoir plus d'une livraison par commande; un NO\_LIVRAISON unique est généré pour chaque livraison.*

DF1: NO\_LIVRAISON -> NO\_CLIENT, NO\_COMMANDE, NO\_BON\_LIVRAISON, NOTES\_LIVRAISON, QUANTITE\_LIVRAISON, DATE\_LIVRAISON, ADRESSE\_LIVRAISON, VILLE\_LIVRAISON, CODE\_POSTAL\_LIVRAISON, COUT\_LIVRAISON



*Nous partons du principe que chaque client à ses numéro de commandes. Par exemple client 10000 à 25 commandes, donc 1 à 25 NO\_COMMANDE*

DF2: NO\_CLIENT, NO\_COMMANDE -> DATE\_COMMANDE, DATE\_LIMITE\_COMMANDE, PO\_CLIENT\_COMMANDE, QUANTITE\_COMMANDE, TYPE\_IMPRESSION, FORMAT\_FINAL\_IMPRESSION, FORMAT\_OUVERT\_IMPRESSION, RECTO\_VERSO\_IMPRESSION

&nbsp;			TYPE\_ENCRE\_RECTO, TYPE\_ENCRE\_VERSO, TYPE\_PAPIER, TYPE\_FINITION, NUMEROTAGE\_FINITION, NOTES\_FINITION, NOTES\_COMMANDE, NO\_SOUS-TRAITANT, PO\_SOUS-TRAITANT, COUT\_SOUS\_TRAITANT,

&nbsp;			COUT\_COMMANDE, COUT\_INFOGRAPHIE



DF3: NO\_CLIENT -> NOM\_CONTACT\_CLIENT, PRENOM\_CONTACT\_CLIENT, NOM\_COMPAGNIE\_CLIENT, ADRESSE\_COMPAGNIE\_CLIENT, VILLE\_COMPAGNIE\_CLIENT, CODE\_POSTAL\_COMPAGNIE\_CLIENT, NUMERO\_TELEPHONE\_COMPAGNIE\_CLIENT

 

DF4: NO\_SOUS-TRAITANT -> NOM\_SOUS-TRAITANT



DF5: NO\_DOSSIER -> TYPE\_TRAVAIL

 
DF6: TYPE\_TRAVAIL -> NO\_DOSSIER





### QUESTIONS ET RÉPONSES POSÉES AUX CLIENTS 





* Est-ce que le NO\_DOSSIER est équivalent à un numéro de commande ? 

Non, ici NO\_DOSSIER réfère à un numéro unique attribué au type de travail, donc NO\_DOSSIER <=> TYPE\_TRAVAIL, ainsi pas besoin d'un NO du dossier unique pour chaque client. 



* Est-ce que le PO dans la section Sous-traitant est le même que celui du client ? 

Non le sous-traitant peu avoir son propre PO 



* Voulez-vous conserver d'autre informations sur le sous-traitant et est-ce qu'il s'agit seulement du nom ou d'un numéro unique ?  

Seulement besoin du nom du sous-traitant, car le reste est fournis sur la facture, donc pas besoin de créer une table avec les infos.



* Pourquoi y a-t-il note sur la commande et note sur le dossier ? 

Notes sur dossier peu être effacé; redondant. 



* Est-ce que à droite de finition, il s'agit des types de finitions ? : 

À droite de finition, c'est tous des types de finitions, sauf "Num" qui est un booléen désignant si c'est numéroté ou non;

ce dernier peut-être retiré de la liste et il faudrait ajouté "livret" dans la liste.  



* Peut-on sélectionner plusieurs types de finitions ? 

Non, seulement une sélection parmi la liste. 



* Que signifie "Numéro" dans la section finition ?  

Numéro dans la section finition signifie si c'est numéroté (par exemple: pages 1-321). 



* Qu'est-ce que "autre" signifie dans la section finition ?  

Autre dans la section finition signifie seulement des notes sur le type de finition 



* Pour encre il y a seulement NB (noir et blanc) pour le recto et le verso, manque-t-il la catégorie couleur ? 

Oui, il y 2 types de couleurs : N (noir) et CMYK









*Légende de normalisation : primary key (PK) en **gras** et foreing key (FK) avec un #*





### NORMALISATION 1NF



**NO\_LIVRAISON, NO\_CLIENT,** **NO\_COMMANDE,**   *Pour satisfaire la 1NF, NO\_LIVRAISON prendrait toujours une valeur par défaut, même s'il n'y a pas de livraison.*

NO\_BON\_LIVRAISON,

NO\_DOSSIER

NOM\_CONTACT\_CLIENT

PRENOM\_CONTACT\_CLIENT

NOM\_COMPAGNIE\_CLIENT

ADRESSE\_COMPAGNIE\_CLIENT

VILLE\_COMPAGNIE\_CLIENT

CODE\_POSTAL\_COMPAGNIE\_CLIENT

NUMERO\_TELEPHONE\_COMPAGNIE\_CLIENT

DATE\_COMMANDE

DATE\_LIMITE\_COMMANDE

PO\_CLIENT\_COMMANDE

TYPE\_TRAVAIL

QUANTITE\_COMMANDE

TYPE\_IMPRESSION

FORMAT\_FINAL\_IMPRESSION

FORMAT\_OUVERT\_IMPRESSION

RECTO\_VERSO\_IMPRESSION

TYPE\_ENCRE\_RECTO

TYPE\_ENCRE\_VERSO

TYPE\_PAPIER

TYPE\_FINITION

NUMEROTAGE\_FINITION

NOTES\_FINITION

NOTES\_COMMANDE

NO\_SOUS-TRAITANT

NOM\_SOUS-TRAITANT

PO\_SOUS-TRAITANT

COUT\_SOUS-TRAITANT

NOTES\_LIVRAISON

QUANTITE\_LIVRAISON

DATE\_LIVRAISON

ADRESSE\_LIVRAISON 

VILLE\_LIVRAISON 

CODE\_POSTAL\_LIVRAISON  

COUT\_COMMANDE

COUT\_INFOGRAPHIE

COUT\_LIVRAISON







### NORMALISATION 2NF  

*(retrait des dépendances partielles sur la PK de ma 1NF)*



*COMMANDE* (**NO\_COMMANDE**,**NO\_CLIENT#**,

NO\_DOSSIER#

TYPE\_TRAVAIL

DATE\_COMMANDE

DATE\_LIMITE\_COMMANDE

PO\_CLIENT\_COMMANDE

QUANTITE\_COMMANDE

TYPE\_IMPRESSION

FORMAT\_FINAL\_IMPRESSION

FORMAT\_OUVERT\_IMPRESSION

RECTO\_VERSO\_IMPRESSION

TYPE\_ENCRE\_RECTO

TYPE\_ENCRE\_VERSO

TYPE\_PAPIER

TYPE\_FINITION

NUMEROTAGE\_FINITION

NOTES\_FINITION

NOTES\_COMMANDE

NO\_SOUS-TRAITANT

NOM\_SOUS-TRAITANT

PO\_SOUS-TRAITANT

COUT\_COMMANDE,

COUT\_INFOGRAPHIE,

COUT\_SOUS-TRAITANT,

)



*CLIENT* (**NO\_CLIENT,**

NOM\_CONTACT\_CLIENT

PRENOM\_CONTACT\_CLIENT

NOM\_COMPAGNIE\_CLIENT

ADRESSE\_COMPAGNIE\_CLIENT

VILLE\_COMPAGNIE\_CLIENT

CODE\_POSTAL\_COMPAGNIE\_CLIENT

NUMERO\_TELEPHONE\_COMPAGNIE\_CLIENT

)



*LIVRAISON* (**NO\_LIVRAISON**,

NO\_CLIENT#, NO\_COMMANDE#,

NO\_BON\_LIVRAISON,

NOTES\_LIVRAISON

QUANTITE\_LIVRAISON

DATE\_LIVRAISON

ADRESSE\_LIVRAISON

VILLE\_LIVRAISON

CODE\_POSTAL\_LIVRAISON

COUT\_LIVRAISON)







### NORMALISATION 3NF 

*(retrait des dépendances transitives)*





*COMMANDE* (**NO\_COMMANDE**,**NO\_CLIENT#**,

NO\_DOSSIER#

DATE\_COMMANDE

DATE\_LIMITE\_COMMANDE

PO\_CLIENT\_COMMANDE

QUANTITE\_COMMANDE

TYPE\_IMPRESSION

FORMAT\_FINAL\_IMPRESSION

FORMAT\_OUVERT\_IMPRESSION

RECTO\_VERSO\_IMPRESSION

TYPE\_ENCRE\_RECTO

TYPE\_ENCRE\_VERSO

TYPE\_PAPIER

TYPE\_FINITION

NUMEROTAGE\_FINITION

NOTES\_FINITION

NOTES\_COMMANDE

NO\_SOUS-TRAITANT#

PO\_SOUS-TRAITANT

COUT\_COMMANDE,

COUT\_INFOGRAPHIE,

COUT\_SOUS-TRAITANT,

)



*CLIENT* (**NO\_CLIENT,**

NOM\_CONTACT\_CLIENT

PRENOM\_CONTACT\_CLIENT

NOM\_COMPAGNIE\_CLIENT

ADRESSE\_COMPAGNIE\_CLIENT

VILLE\_COMPAGNIE\_CLIENT

CODE\_POSTAL\_COMPAGNIE\_CLIENT

NUMERO\_TELEPHONE\_COMPAGNIE\_CLIENT

)



*LIVRAISON* (**NO\_LIVRAISON**,

NO\_CLIENT#, NO\_COMMANDE#,

NO\_BON\_LIVRAISON,

NOTES\_LIVRAISON

QUANTITE\_LIVRAISON

DATE\_LIVRAISON

ADRESSE\_LIVRAISON

VILLE\_LIVRAISON

CODE\_POSTAL\_LIVRAISON

COUT\_LIVRAISON)



*TYPE\_TRAVAIL* (**NO\_DOSSIER**, 

TYPE\_TRAVAIL)



*SOUS-TRAITANT* (**NO\_SOUS-TRAITAN**T,

NOM\_SOUS-TRAITANT)





