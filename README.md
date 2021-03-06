# datatests
Script python permettant de tester des données au format shape sur la base de tests décris dans un fichier de configuration.

## Principe :
le script est lancé avec 2 arguments en entré qui correspondent respectivement au dossier où sont stockés les fichiers à analyser et au fichier de configuration (tests) à utiliser.

Tous les tests à effectuer sont décrits dans un fichier json qui doit avoir la forme suivante 
> Exemple : configuration.json




    {
    	"tests": [
    			{
    				"id": "Test1",
    				"nom": "Présence des champs obligatoires",
    				"type": "requery_field",
    				"fields": ["champ1", "champ2"]
    			},
    			{
    				"id": "Test2",
    				"nom": "Nombre d'enregistrements supérieur à 100",			
    				"type": "featurecount",
    				"nombre": 100
    			}
    		]
    }




exemple `script.py dossier_a_tester fichier_de_tests.json`

L'exécution du script retourne un fichier rapport au format html.

## Paramétrage :

Il existe 6 types de tests. Les tests sont décrits dans fichier json appelé par le script

 - **requery_field** : test sur la présence de champs obligatoires,
 - **featurecount** : test sur le nombre d'enregistrements,
 - **datatype** : test sur le type de données d'un champ,
 - **notnull** : test sur l'absence de valeurs nulles,
 - **allowedvalues** : test sur les valeurs autorisées d'un champ,
 - **uniquevalue** : test sur l'unicité des valeurs d'un champ,
 
 
Chaque test doit comporter les propriétés obligatoires suivantes

 - **id** : Identifiant unique du test - Chaine de charactères
 - **nom** : Nom ou description du test. Cette valeur est reprise dans le rapport d'analyse
 - **type** : Type de test. 

En fonction de chaque test, des paramètres supplémentaires sont disponibles

## 1 - Test sur la présence champs obligatoires :

Le paramètre **fields** est une liste de champs
 
     {
       	"type": "requery_field",
       	"fields": ["champ1", champ2"]
     }

## 2 - Test sur le nombre d'enregistrements
    
    {
       	"type": "featurecount",
       	"nombre": 100
     }

## 3 - Test sur le type de données. 

Le paramètre **datatype** est un type OGRFieldType. Les valeurs possibles sont : String, Integer, Integer64, Real, Date, Time.
Le paramètre **field** précise le champ concerné.
    
    {
       	"type": "datatype",
	"field": "champ1",
       	"datatype": "String"
     }

## 4 - Test sur l'absence de valeurs nulles. 

Le paramètre **critere** est une expression de type SQL WHERE. Il s'agit d'un paramètre obligatoire. Si on ne souhaite pas de filtre, il faut mettre `critere : ""`
Le paramètre **fields** est une liste de champs.
    
    {
       	"type": "notnull",
       	"fields": ["champ1", champ2"],
       	"critere" : "champ3 = 'BB1'"
     }

## 5 - Test sur les valeurs autorisées d'un champ

Le paramètre **critere** est une expression de type SQL WHERE. Il s'agit d'un paramètre obligatoire. Si on ne souhaite pas de filtre, il faut mettre `critere : ""`
Le paramètre **rules** est une liste de champs / valeurs
    
    {
       	"type": "allowedvalues",       	
       	"critere" : "champ3 = 'BB1'",
       	"rules" : [{
	       	"field": "champ4",
	       	"values": ["1", "2", "3"]
	       	}]
     }

## 6 - Test sur les valeurs uniques. 

Le paramètre **field** indique le nom du champ à tester.
    
    {
       	"type": "uniquevalues",
       	"field": "champ0"
     }
     
     
## Prérequis

le script python utilise la librairie gdal/ogr qui doit être installée.
