#-*- coding: utf-8 -*-
from django.db import models
import datetime

# Create your models here.

class Pessoa(models.Model):
    u'''
    Classe referente aos dados gerais de Pessoa física
    '''
    titulo_eleitoral = models.CharField(u'Título Eleitoral', max_length=12)
    nome = models.CharField('Nome do eleitor', max_length=100)
    data_nascimento = models.DateField('Data de Nascimento')
    endereco = models.CharField(u'Endereço Residencial', max_length=150)
    cep = models.CharField('CEP', max_length=9)
    telefone = models.CharField('Telefone', max_length=11, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    data_cadastro = models.DateTimeField(default=datetime.datetime.now())
    class Meta:
        unique_together = ('titulo_eleitoral',)
    
class Local(models.Model):
    u'''
    Classe referente ao local registrado 
    '''
    id_local = models.IntegerField(primary_key = True)
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=150)
    bairro = models.CharField(max_length = 30)


#classes referente a veículos
class Marca(models.Model):
    nome = models.CharField(max_length=30)
        
class Modelo(models.Model):
    nome = models.CharField(u'Modelo do veículo', max_length = 30)
    marca = models.ForeignKey(Marca, verbose_name='Marca do veículo')
    
