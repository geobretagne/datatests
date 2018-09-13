#!/usr/bin/python
# -*- coding: utf-8 -*-
# coding: utf8

from datetime import datetime
from time import localtime, strftime, time
import json, glob, sys, os


try:
    from osgeo import ogr
except:
    sys.exit('ERROR: Impossible de trouver les modules GDAL/OGR')

if (len(sys.argv) > 2):
    workspace = sys.argv[1]
    configuration = sys.argv[2]
else:
    print u"Ce script utilise 2 paramètres : \n- 1 pour le dossier à analyser. \n- 2 pour le fichier json de test à utiliser.".encode('utf-8') 
    exit()
    
def txt(t):
    return "\'%s\'" % t

def write(logfile, message, tag, color="black"):
    print message.encode('utf-8')
    if tag:
        message = ' '.join(['<' + tag + ' style="color:'+color+';" >', message, '</' + tag + '>'])
    logfile.write(message.encode('utf-8') + "</br>")

start = time()
config = {}

try:
    with open(configuration) as json_data:
        config = json.load(json_data)
except:
    sys.exit('ERREUR: impossible de trouver %s' % configuration)

log_file = workspace + "/../rapport.html"
log = open(log_file,"w")
fichiers = glob.glob(workspace + "/" + "*.shp")

for fichier in fichiers :
    results = {"global": True}
    dataSource = ogr.Open(fichier)
    dataLayer = dataSource.GetLayer(0)
    layerDefinition = dataLayer.GetLayerDefn()
    layername = dataLayer.GetName()
    featureCount = dataLayer.GetFeatureCount()
    spatialRef = dataLayer.GetSpatialRef()
    write(log, "RAPPORT DU " + strftime("%d-%m-%Y %H:%M:%S", localtime()), "h4")
    write(log, "ANALYSE DE " + os.path.basename(fichier), "h1") 
    write(log, "Projection de la couche : " + str(spatialRef.GetAttrValue("PROJCS", 0)), "p")
    write(log, str(featureCount) + u" entités trouvées dans la couche", "p") 

    fields_shape =[]
    fields_types = {}
    
    
    for i in range(layerDefinition.GetFieldCount()):
        nom_champs = layerDefinition.GetFieldDefn(i).GetName()
        type = layerDefinition.GetFieldDefn(i).GetType()
        type_name = layerDefinition.GetFieldDefn(i).GetFieldTypeName(type)
        fields_shape.append(nom_champs)
        fields_types[nom_champs] = type_name        
    

        
    #Boucle sur les tests listes dans le fichier json
    for test in config["tests"]:
        if test["type"] == "requery_field":
            write(log, test["id"]+ " - " + test["nom"] , "h4")
            nofields = []
            for field in test["fields"]:
                if field not in fields_shape:
                    nofields.append(field)                    
            if len(nofields)>0:
                results["global"] = False
                write(log, "ERREUR, champs obligatoires manquants :" + ", ".join(nofields),"p", "#F44336")
            else:
                write(log, u"champs obligatoires : test réussi. ", "p")


  ###################################################################

        elif test["type"] == "datatype":
            write(log, test["id"] + " - " + test["nom"] , "h4")
            if test["field"] in fields_types:
                if fields_types[test["field"]] == test["datatype"]:
                    write(log, u"Test réussi.", "p")
                else:
                    write(log, "ERREUR.", "p", "#F44336")
                    results["global"] = False

            else:
                write(log, "Test non disponible.", "p")

          
            
        elif test["type"] == "notnull":
            write(log, test["id"]+ " - " + test["nom"], "h4")
            #Creation variable propre au test en reprenant l'id du tes. ex results.Test2
            results[test["id"]] = {}
            critere = str(test["critere"]).replace("'", "\'")  
            if len(critere) > 1:
                critere = "AND " + critere     
            #boucle sur les champs listes dans le test
            for field in test["fields"]:
                # pour chaque champ analyse, creation d'une variable initialisee a True. Ex results.Test2.ID_AJOUR = True
                if not field in results[test["id"]]:
                    results[test["id"]][field] = True
                #si le champ a tester est disponible
                if field in fields_shape:                    
                    sql = 'SELECT * FROM "%s" WHERE %s IS NULL %s' % (layername, field, critere)                               
                    nodata = dataSource.ExecuteSQL(str(sql))                    
                    if nodata.GetFeatureCount() > 0:
                        results[test["id"]][field] = False
                        results["global"] = False
                        write(log, u"ERREUR. Au moins une valeur nulle pour le champ "  + field, "p", "#F44336")
                    else:                   
                        write(log, field + " : " + u"Test réussi", "p")
                else:
                    write(log, field + " : champ non disponible", "p")
                    
                    

                    
        elif test ["type"] ==  "uniquevalue":
            write(log, test["id"]+ " - " + test["nom"], "h4")
            field = test["field"]
            if field in fields_shape:                
                sql = 'SELECT COUNT(DISTINCT ID_AJOUR) AS COUNT FROM "%s"' % layername
                doublons = dataSource.ExecuteSQL(sql)
                doublonsCount = featureCount - doublons[0].GetField("COUNT")
                if doublonsCount > 0:
                    write(log, "ERREUR. " +  str (doublonsCount) + " doublon(s)", "p", "#F44336")
                    results["global"] = False
                else:
                    write (log, u"Test réussi.", "p")
            else:
                write(log, field + " champ non disponible", "p")        
                    
        elif test ["type"] ==  "featurecount":
            write(log, test["id"]+ " - " + test["nom"], "h4")
            nombre = test["nombre"]
            if featureCount > nombre:                
               write(log, u"Test réussi.", "p")              
                    
            else:
                write (log, "ERREUR", "p", "#F44336")
                results["global"] = False    
######################################################################
          
        elif test["type"] == "allowedvalues":
            write(log, test["id"]+ " - "+test["nom"], "h4")
            # Creation variable propre au test en reprenant l'id du test. ex results.Test2
            results[test["id"]] = {}
            critere = test["critere"]
            if len(critere) > 1:
                critere = "AND " + critere            
            # boucle sur les rules listes dans le test. Attention champs de la forme {nom , values}
            for rule in test["rules"]:
                #Recuperation valeurs requises
                field = rule["field"]
                allowedvalues = rule["values"]
                expression = ", ".join(map(txt, allowedvalues))                
                # pour chaque champ analyse, creation d'une variable initialisee a True. Ex results.Test2.ID_AJOUR = True
                if not field in results[test["id"]]:
                    results[test["id"]][field] = True
                # si le champ a tester est disponible
                if field in fields_shape:
                    # Boucle sur les lignes de la table attributaire
                    # On parcourt toutes les lignes du champ jusqu'a rencontrer une erreur  
                    critere = critere + " AND %s IS NOT NULL" % field                            
                    #test
                    sql = 'SELECT DISTINCT %s as baddata FROM "%s" WHERE %s NOT IN (%s) %s' % (field, layername, field, expression, critere)
                    baddata = dataSource.ExecuteSQL(str(sql))
                    if baddata.GetFeatureCount() > 0:
                        results[test["id"]][field] = False
                        results["global"] = False
                        write(log, "ERREUR : " + field + " : " + str(baddata[0].GetField("baddata")) + " : valeur interdite", "p", "#F44336")
                    else:
                        write(log, field + u" : test réussi.", "p")            
                    

                else:
                    write(log, "Champ, " + field + " : non disponible", "p")
                  
        else: 
            write(log, test["id"]+ " - " + test["nom"] + " TYPE INCONNU", "h4")
        
        
    
    write(log, " --- %s secondes ---" % str(time() - start), "h4")
    #Affichage resultat global pour la couche ananlysee
    if results["global"] == True:
        message = os.path.basename(fichier) + "--> Bravo. Tout est ok !"
        write(log, message, "h2")        
        exit(0)
    else:
        message = os.path.basename(fichier) + " --> Couche en erreur !"
        write(log, message, "h2", "#F44336!important")
        exit(1)
    
    

        
    
    
