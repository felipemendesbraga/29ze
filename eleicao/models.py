#-*- coding: utf-8 -*-
from django.db import models
from core.models import Pessoa, Local
from django.db.models.signals import post_save
from django.dispatch import receiver


class Eleicao(models.Model):
    
    nome = models.CharField(u'Nome da eleição', max_length=30)
    data_turno_1 = models.DateField('Data do primeiro turno')
    data_turno_2 = models.DateField('Data do segundo turno', null=True, blank=True)
    atual = models.BooleanField(default=True)
    eleitores = models.ManyToManyField(Pessoa, through='Eleitor', related_name='eleicao_eleitores')
    locais = models.ManyToManyField(Local, through='LocalVotacao', related_name='eleicao_locais')
    
    class Meta:
        permissions = [('view_eleicao', u'Visualizar Eleições'),
                       ('view_old_eleicao', u'Visualizar Eleição Anterior'), ]
    
    @models.permalink
    def get_absolute_url(self):
        return 'eleicao:editar', [str(self.id)]
    
    def __unicode__(self):
        return self.nome
    
    def get_total_local(self):
        locais = self.locais.all()
        count = 0
        for local in locais:
            if local.localvotacao_set.all()[0].get_total_eleitores() == 0:
                continue
            count += 1
        return count

    def get_total_eleitores(self):
        return self.secao_set.aggregate(models.Sum('num_eleitores')).get('num_eleitores__sum')

    def save(self, *args, **kwargs):
        if self.nome:
            self.nome=self.nome.upper()
        super(Eleicao, self).save(*args, **kwargs)

        

@receiver(post_save, sender=Eleicao)
def eleicao_post_save(signal, instance, sender, **kwargs):
    
    if instance.atual:
        sender.objects.exclude(pk=instance.pk).update(atual=False)


class LocalVotacao(models.Model):
    eleicao = models.ForeignKey(Eleicao)
    local = models.ForeignKey(Local)
    equipe = models.ForeignKey('Equipe', related_name='local_equipe', blank=True, null=True)
    
    class Meta:
        permissions = [
                       ('view_local_votacao', u'Visualizar Locais de Votação'),
                       ('import_local_votacao', u'Importar Locais de Votação'),
                       ]
    
    def __unicode__(self):
        return unicode(self.local.nome)
    
    def get_secoes(self, delimitador=u', '):
        return delimitador.join([s.unicode_agregadas() for s in list(self.secao_set.secao_pai())])
    
    def get_count_secao_agregadas(self):
        return self.secao_set.secao_pai().count()
    
    def get_total_eleitores(self):
        secoes = self.secao_set.secao_pai()
        total = 0
        for secao in secoes:
            total += secao.get_total_eleitores()
        return total

    @models.permalink
    def get_absolute_url(self):
        return 'local:detalhar', [str(self.id)]

    def get_perfis_local(self):
        return self.equipe.perfilveiculo_set.filter(perfil_equipe=False)

    def get_veiculos_alocados(self):
        return self.veiculoalocado_set.all()

    def get_veiculos_alocados_turno2(self):
        return self.veiculoalocado_set.filter(segundo_turno=True)

class SecaoManager(models.Manager):
    
    def secao_pai(self):
        return self.filter(secoes_agregadas=None).order_by('num_secao')
    
    def all_ordenado(self):
        return self.all().order_by('num_secao')
    
    def get_by_natural_key(self, num_secao):
        return self.get(num_secao=num_secao)
    
    
class Secao(models.Model):
    objects = SecaoManager()
    num_secao = models.IntegerField()
    eleicao = models.ForeignKey(Eleicao)
    local_votacao = models.ForeignKey(LocalVotacao)
    num_eleitores = models.IntegerField()
    principal = models.BooleanField(default=False)
    especial = models.BooleanField(default=False)
    secoes_agregadas = models.ForeignKey('Secao', related_name='secao_secoes_agregadas', null=True, blank=True)
    
    class Meta:
        unique_together = ('num_secao', 'eleicao')
        permissions = [
                       ('agregar_secao', u'Agregar/desagregar Seção'),
                       ]
    
    def __unicode__(self):
        return unicode(self.num_secao) + (self.especial and u'*' or u'')
    
    def __str__(self):
        return str(self.num_secao) + (self.especial and '*' or '')
    
    def unicode_agregadas(self, especial=True):
        agregadas = list(self.secao_secoes_agregadas.all_ordenado())
        if especial:
            return u'+'.join([unicode(s) for s in ([self, ] + agregadas)])
        return u'+'.join([unicode(s.num_secao) for s in ([self, ] + agregadas)])
    
    def get_local(self):
        if not self.secoes_agregadas:
            return self.local_votacao.local.nome
        return self.secoes_agregadas.local_votacao.local.nome
    
    def get_endereco(self):
        if not self.secoes_agregadas:
            return self.local_votacao.local.endereco
        return self.secoes_agregadas.local_votacao.local.endereco
    
    def get_bairro(self):
        if not self.secoes_agregadas:
            return self.local_votacao.local.bairro
        return self.secoes_agregadas.local_votacao.local.bairro
        
    def desagregarSecoes(self):
        secoes = self.secao_secoes_agregadas.all()
        for secao in secoes:
            secao.secoes_agregadas = None
            secao.save()
        self.principal = False
        self.save()

    def secao_with_popover(self, principal=False):
        html = u'''<span  class="tooltip-iniciar"
            href="#" data-toggle="tooltip" title="<label>Quantidade de eleitores:&nbsp;</label>%(num_eleitores)d %(especial)s %(local)s">
            %(num_secao)s
            </span>'''
        
        especial = self.especial and '<br /><label>especial</label>' or ''
        local = ''

        if self.secoes_agregadas:
            if self.local_votacao.pk != self.secoes_agregadas.local_votacao.pk:
                local = '<br /><label>Local de origem:&nbsp;</label>' + self.local_votacao.local.nome

        if self.principal or principal:
            return html % {'num_secao': '<strong>' + str(self) + '</strong>', 'num_eleitores': self.num_eleitores, 'especial': especial, 'local': local}
        return html % {'num_secao': str(self), 'num_eleitores': self.num_eleitores, 'especial': especial, 'local': local}
    
    def get_total_eleitores(self):
        total_agregado = self.secao_secoes_agregadas.aggregate(soma_agregados=models.Sum('num_eleitores'))
        return total_agregado.get('soma_agregados') and self.num_eleitores + total_agregado['soma_agregados'] or self.num_eleitores
        
    def get_num_secao(self):
        agregadas = list(self.secao_secoes_agregadas.all_ordenado())
        if len(agregadas) == 0:
            return [self.secao_with_popover(True),]
        return [s.secao_with_popover() for s in ([self, ] + agregadas)]

    
class Eleitor(models.Model):
    eleicao = models.ForeignKey(Eleicao, related_name='eleitor_eleicao')
    eleitor = models.ForeignKey(Pessoa, related_name='eleitor_eleitor')
    secao = models.ForeignKey(Secao, related_name='eleitor_secao')


class Coligacao(models.Model):
    nome = models.CharField(max_length=100)
    eleicao = models.ForeignKey(Eleicao, related_name='coligacao_eleicao')


class Partido(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=20)
    prefixo = models.IntegerField()
    coligacao = models.ForeignKey(Coligacao)
    eleicao = models.ForeignKey(Eleicao, related_name='partido_eleicao')


class EquipeManager(models.Manager):
    def all(self):
        qs = super(EquipeManager, self).all()
        return qs.order_by('nome')


class Equipe(models.Model):
    nome = models.CharField(max_length=100)
    eleicao = models.ForeignKey(Eleicao, related_name='equipe_eleicao')
    manual = models.BooleanField(u'Inserção manual de veículos', default=False)
    sigla = models.CharField(max_length=4)
    objects = EquipeManager()

    class Meta:
        permissions = [('view_equipe', 'Visualizar Equipes'),
                       ('alocar_veiculos', 'Estimar veículos da equipe'), ]
    
    def __unicode__(self):
        return unicode(self.nome)
    
    @models.permalink
    def get_absolute_url(self):
        return 'equipe:detalhar', [str(self.id)]
    
    def get_total_secoes(self):
        soma = 0
        for local in self.local_equipe.all():
            soma += local.secao_set.secao_pai().count()
        return soma
    
    def get_locais_ordenado(self):
        return self.local_equipe.filter(local_montagem=None).order_by('local__nome')
    
    def get_locais_matutinos(self):
        return self.local_equipe.filter(local_montagem__turno='m').order_by('local_montagem__ordem')
    
    def get_total_secoes_matutino(self):
        total = 0
        for local in self.local_equipe.filter(local_montagem__turno='m'):
            total += local.get_count_secao_agregadas()
        return total
    
    def get_locais_vespertinos(self):
        return self.local_equipe.filter(local_montagem__turno='v').order_by('local_montagem__ordem')
    
    def get_total_secoes_vespertino(self):
        total = 0
        for local in self.local_equipe.filter(local_montagem__turno='v'):
            total += local.get_count_secao_agregadas()
        return total
    
    def get_total_eleitores(self):
        soma = 0
        for local in self.local_equipe.all():
            somatorio = local.secao_set.secao_pai().aggregate(soma_agregados=models.Sum('num_eleitores')).get('soma_agregados')
            if isinstance(somatorio, int):
                soma += somatorio
        return soma

    def get_perfis_equipe(self):
        return self.perfilveiculo_set.filter(perfil_equipe=True)

    def get_perfis_local(self):
        return self.perfilveiculo_set.filter(perfil_equipe=False)

    def total_veiculos_estimados_turno1(self):
        total_agregado = self.alocacao_set.filter(segundo_turno=False).aggregate(soma_agregados=models.Sum('quantidade'))
        return total_agregado.get('soma_agregados') and total_agregado.get('soma_agregados') or 0

    def total_veiculos_estimados_turno2(self):
        total_agregado = self.alocacao_set.filter(segundo_turno=True).aggregate(soma_agregados=models.Sum('quantidade'))
        return total_agregado.get('soma_agregados') and total_agregado.get('soma_agregados') or 0

    def get_alocacoes_turno2(self):
        return self.alocacao_set.get_perfis_equipe().filter(segundo_turno=True)

    def veiculos_alocados_local(self):
        return self.veiculoalocado_set.exclude(local_votacao=None)
    def veiculos_alocados_local_turno2(self):
        return self.veiculoalocado_set.filter(segundo_turno=True).exclude(local_votacao=None)


    def veiculos_por_data(self, data):
        return self.veiculoalocado_set.filter(perfil__cronograma_perfil__dt_apresentacao__range=(data, data.replace(day=data.day+1)))

    def save(self, *args, **kwargs):
        if self.nome:
            self.nome = self.nome.upper()
        super(Equipe, self).save(*args, **kwargs)


class EquipesAlocacao(models.Model):
    equipe = models.ForeignKey(Equipe, primary_key=True)
    eleicao = models.ForeignKey(Eleicao)
    segundo_turno = models.BooleanField()
    total_estimativa = models.IntegerField()
    estimativa_equipe = models.IntegerField()
    estimativa_local = models.IntegerField()
    veiculos_alocados = models.IntegerField()
    veiculos_alocados_equipe = models.IntegerField()
    veiculos_alocados_local = models.IntegerField()

    class Meta:
        managed = False
        db_table = u'vw_equipes_alocacao'


class Montagem(models.Model):
    local = models.OneToOneField(LocalVotacao, related_name='local_montagem')
    turno = models.CharField(max_length=1, choices=(('m', 'matutino'), ('v', 'vespertino')))
    ordem = models.IntegerField()


class Cargo(models.Model):
    nome = models.CharField(max_length=50)
    eleicao = models.ForeignKey(Eleicao, related_name='cargo_eleicao')


class Funcionario(Pessoa):
    equipe = models.ForeignKey(Equipe, related_name='funcionario_equipe')
    cargo = models.ForeignKey(Cargo, related_name='funcionario_cargo')
    eleicao = models.ForeignKey('Eleicao', related_name='funcionario_eleicao')
