# -*- coding: utf-8 -*-
import re

from conn import MongoDBconn
import pdb

class Congress(object):
    _conn = None
    def __init__(self):
        self._conn = MongoDBconn()

    def _getCollection(self,collection):
        return self._conn.getDB()[collection]

    def searchAll(self,collection=None):
        """
        :param collection:
        :return: List
        """
        return [ element for element in self._getCollection(collection).find()]

    def searchByparam(self, collection=None, param={}):
        return self._getCollection(collection).find(param)

    def getNotAnnotatedInitiatives(self, dictname):
        return self._getCollection('iniciativas').find({'$or': [{'annotate.%s'%dictname : {'$exists': False}}, {'annotate.%s'%dictname : False}]}, no_cursor_timeout=True)

    def getDictsByGroup(self, group):
        return self._getCollection('dicts').find({'group': group})


    def addDictToInitiative(self, initiative_id, dictgroup, dicts, terms):
        coll = self._getCollection(collection='iniciativas')
        coll.update_one({
            '_id': initiative_id,
        },{
            '$set': {
            'annotate.%s'%dictgroup: True,
            'is.%s'%dictgroup: True if len(dicts) > 0 else False,
            'dicts.%s'%dictgroup: dicts,
            'terms.%s'%dictgroup: terms,
            }
        ,}
        )


    def getDictGroups(self):
        coll = self._getCollection(collection='dicts')
        return coll.find({}, {'group': 1}).distinct('group')
    

    def getInitiative(self, collection="iniciativas", ref = None, tipotexto= None, titulo = None):
        search = self._getCollection(collection).find_one(
            {
                'ref': ref,
                'tipotexto': tipotexto,
                'titulo': titulo
            }
        )
        return search


    def updateorinsertInitiative(self, collection="iniciativas", type = "insert", item = None):
        #metodo para el pipeline
        if type is 'insert':
            self._insertInitiative(collection,item)
            #update
        elif type is 'update':
            self._updateInitiative(collection,item)
            #inserta
        else:
            print "Not type accepted"
            raise

    def _insertInitiative(self,collection,item):
        self._getCollection(collection=collection).insert(dict(item))

    def _updateInitiative(self,collection,item):
        coll = self._getCollection(collection=collection)
        coll.update_one({
                 'ref': item['ref'],
                'tipotexto': item['tipotexto'],


        },{
            '$set': {
            'titulo': item['titulo'],
            'autor_diputado': item['autor_diputado'],
            'autor_grupo': item['autor_grupo'],
            'autor_otro': item['autor_otro'],
            'url': item['url'],
            'tipo': item['tipo'],
            'tramitacion': item['tramitacion'],
            'fecha': item['fecha'],
            'lugar': item['lugar'],
            'fechafin': item['fechafin'],

                    }
            ,}
        )



    def updateorinsertInitiativecontent(self, collection="iniciativas", type = "insert", item = None):
        #metodo para el pipeline
        if type is 'insert':
            self._insertInitiative(collection,item)
            #update
        elif type is 'update':
            self._updateInitiativecontent(collection,item)
            #inserta
        else:
            print "Not type accepted"
            raise



    def _updateInitiativecontent(self,collection,item):
        coll = self._getCollection(collection=collection)
        coll.update_one({
                 'ref': item['ref'],
                'tipotexto': item['tipotexto'],


        },{
            '$set': {
            'titulo': item['titulo'],
            'autor_diputado': item['autor_diputado'],
            'autor_grupo': item['autor_grupo'],
            'autor_otro': item['autor_otro'],
            'url': item['url'],
            'tipo': item['tipo'],
            'tramitacion': item['tramitacion'],
            'fecha': item['fecha'],
            'lugar': item['lugar'],
            'fechafin': item['fechafin'],
            'contenido': item['contenido'],

                    }
            ,}
        )




    def isDiffinitiative(self, collection="iniciativas", item = None, search = None):


        if search:#existe
            return not self.sameInitiative(item,search)
        else:
            return False

    def sameInitiative(self,item,search):

        for key, value in search.iteritems():
            for ikey,ivalue in item.iteritems():
                if key == ikey:
                    if value !=  ivalue and  (key is not 'contenido' and  key is not 'dicts' and
                                              key is not 'terms' and key is not 'annotate' and key is not 'is'):
                        return False
        return True


    def updateorinsertAdmenment(self, collection="iniciativas",  item = None ,search = None):
        #metodo para el pipeline

        self._insertAdmendment(collection,item,search)
            #update


    def _insertAdmendment(self,collection,item,search):

        if not search:
            insert ={
                'ref': item['ref'],
                'tipotexto':item['tipotexto'],
                'titulo': item['titulo'],
                'tipo':item['tipo'],
                'autor_grupo': item["autor_grupo"],
                'autor_diputado':item["autor_diputado"],
                'autor_otro' : item["autor_otro"],
                'fecha': item["fecha"],
                'fechafin': item["fechafin"],
                'url': item['url'],
                'lugar': item['lugar'],
                'tramitacion': item['tramitacion'],
                'contenido':[item["contenido"]]


            }
            self._getCollection(collection=collection).insert(insert)
        else:
            self._updateAdmendment(collection,item,search)

    def _updateAdmendment(self,collection,item,search):

        autor = item["autor_grupo"]

        coll = self._getCollection(collection=collection)
        append = item["contenido"]
        before = search["contenido"]
        beforeautor = search["autor_diputado"]
        beforeotro = search["autor_otro"]
        if item["autor_diputado"]:
            beforeautor = beforeautor + item["autor_diputado"]
        if item["autor_otro"]:
            beforeotro=beforeotro+item["autor_otro"]
        if append not in before:
            before.append(append)
            coll.update_one({
                        'ref': item['ref'],
                        'tipotexto': item['tipotexto'],
                        'autor_grupo' : autor


                },{
                    '$set': {
                    'autor_diputado': list(set(beforeautor)),
                    'autor_otro': list(set(beforeotro)),
                    'contenido':before,
                            }
                    ,}
                )

    def getAdmendment(self, collection="iniciativas", ref = None, tipotexto= None, autor = None):
        search = self._getCollection(collection).find_one(
        {
                'ref': ref,
                'tipotexto': tipotexto,
                'autor_grupo': autor
        }
        )

        return search


    def updateorinsertFinishtextorResponse(self, collection="iniciativas", type="insert", item=None):
            # metodo para el pipeline
        if type is 'insert':
            self._insertFinishsTextorResponse(collection, item)
                # update
        elif type is 'update':
            self._updateFinishTextorResponse(collection, item)
                # inserta
        else:
            print "Not type accepted"
            raise

    def _insertFinishsTextorResponse(self, collection, item):
        self._getCollection(collection=collection).insert(dict(item))

    def _updateFinishTextorResponse(self, collection, item):
        coll = self._getCollection(collection=collection)
        coll.update_one({
                'ref': item['ref'],
                'tipotexto': item['tipotexto'],

            }, {
                '$set': {
                    'titulo': item['titulo'],
                    'autor_diputado': item['autor_diputado'],
                    'autor_grupo': item['autor_grupo'],
                    'autor_otro': item['autor_otro'],
                    'url': item['url'],
                    'tipo': item['tipo'],
                    'tramitacion': item['tramitacion'],
                    'fecha': item['fecha'],
                    'lugar': item['lugar'],
                    'fechafin': item['fechafin'],
                    'contenido': item['contenido']

                }
                ,}
            )

    def getMember(self, collection="diputados", name = None):
        search = self._getCollection(collection).find_one(
            {
                'nombre': name,
            }
        )
        return search


    def updateorinsertMember(self, collection="diputados", type = "insert", item = None):
        #metodo para el pipeline
        if type is 'insert':
            self._insertMember(collection,item)
            #update
        elif type is 'update':
            self._updateMember(collection,item)
            #inserta
        else:
            print "Not type accepted"
            raise

    def _insertMember(self, collection, item):
        self._getCollection(collection=collection).insert(dict(item))

    def _updateMember(self, collection, item):
        coll = self._getCollection(collection=collection)
        coll.update_one({
            'nombre': item['nombre'],


        }, {
            '$set': {
                'url': item['url'],
                'grupo': item['grupo'],
                'correo': item['correo'],
                'web': item['web'],
                'twitter': item['twitter'],
                'fecha_alta': item['fecha_alta'],
                'fecha_baja': item['fecha_baja'],
                'imagen': item['imagen']

            }
        })



    def addAlert(self, dictname, init_id, init_title, init_date):
        coll = self._getCollection(collection='tipialerts')
        coll.update_one({
            'dict': dictname,
            }, {
                '$addToSet': {
                    'items': {
                        'id': str(init_id),
                        'titulo': init_title,
                        'fecha': init_date,
                        }
                }
            }, upsert=True)

    def getTipisAllAlerts(self):
        #return cursor
        return self._getCollection('tipialerts').find({'items':{'$exists':True,'$not':{'$size':0}}}) #Contain alert

    def getUserswithAlert(self):
        #return cursor
        return self._getCollection('users').find({"profile.dicts":{'$exists': True}})

    def getAgregatefrompipeline(self,collection,pipeline):
        """
        :param collection: For match
        :param pipeline: any pipeline
        :return: List
        """
        return list(self._getCollection(collection).aggregate(pipeline=pipeline))

    def deletecollection(self,collection):
        #Warning
        self._getCollection(collection).drop()

    def insertstat(self,collection="tipistats",dict={}):
        self._getCollection(collection).insert(dict)



        






