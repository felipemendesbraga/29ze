#-*- coding: utf-8 -*-
'''
Created on 07/08/2014

@author: felipe
'''
import datetime
from datetime import date
from django.db.models.query_utils import Q
from django.forms.models import modelform_factory
from django.contrib.auth.decorators import login_required, permission_required
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import Context
from excel_response import ExcelResponse
from core.models import Pessoa
from veiculos.forms import FrequenciaForm, RelatorioDiaForm
import webodt
from webodt.converters import converter
from eleicao.models import Equipe
from models import Veiculo, VeiculoSelecionado
from acesso.models import OrgaoPublico
from veiculos.models import VeiculoAlocado, PerfilVeiculo


@permission_required('veiculos.view_veiculo', raise_exception=True)
@login_required(login_url='acesso:login-veiculos')
def relatorio_veiculos(request):
    if isinstance(request.user, OrgaoPublico):
        veiculos = Veiculo.objects.filter(orgao= request.user, eleicao = request.eleicao_atual).order_by('marca__nome', 'modelo__nome')
    else:
        veiculos = Veiculo.objects.all().order_by('marca__nome', 'modelo__nome')
    return render(request, 'veiculos/report/veiculos.html', locals())

def relatorio_admin_orgao_sem_veiculo(request):
    orgaos = OrgaoPublico.objects.all()
    lista_orgaos = []
    for orgao in orgaos:
        if orgao.veiculo_orgao.count() == 0:
            lista_orgaos.append(orgao)
    return render(request, 'veiculos/report/orgaos-sem-veiculos.html', locals())

def relatorio_veiculos_requisitados(request, id_orgao=None):
    if id_orgao:
        orgao = OrgaoPublico.objects.get(pk=int(id_orgao))
        veiculos = VeiculoSelecionado.objects.filter(veiculo__eleicao = request.eleicao_atual, veiculo__orgao=orgao).order_by('veiculo__orgao__nome_secretaria', 'veiculo__marca__nome', 'veiculo__modelo__nome')
    
    orgaos = OrgaoPublico.objects.all().order_by('nome_secretaria')
    Form = modelform_factory(
                Veiculo,
                fields=('orgao',),
                labels={'orgao':u'Selecionar Órgão: '})
    Form.base_fields['orgao'].queryset = orgaos
    form = Form({'orgao':id_orgao})
    form.fields['orgao'].widget.attrs.update({'class':'form-control'})
    return render(request, 'veiculos/report/veiculos_requisitados.html', locals())

def relatorio_veiculo_alocado(request, id_veiculo):
    veiculo = get_object_or_404(VeiculoAlocado, pk=int(id_veiculo))
    motorista = veiculo.veiculo.motorista_veiculo.filter(segundo_turno=veiculo.segundo_turno).first()
    data = datetime.datetime.now()
    def cronograma_local(c):
        if not c.local:
            c.local = veiculo.local_votacao.local
        c.local.endereco = c.local.endereco.upper()
        c.local.bairro = c.local.bairro.upper()
        if c.dia_montagem:
            if veiculo.local_votacao.local_montagem.turno=='v':
                c.dt_apresentacao = datetime.datetime(c.dt_apresentacao.year, c.dt_apresentacao.month,c.dt_apresentacao.day, 13,0)
            else:
                c.dt_apresentacao = datetime.datetime(c.dt_apresentacao.year, c.dt_apresentacao.month,c.dt_apresentacao.day, 7,0)
        return c
    cronogramas = map(cronograma_local, veiculo.perfil.cronograma_perfil.filter(eleicao = request.eleicao_atual, segundo_turno=veiculo.segundo_turno).order_by('dt_apresentacao'))
    telefones = '/'.join(unicode(telefone) for telefone in motorista.pessoa.telefones_set.all()) if motorista else ''

    context = dict(
        veiculo='%s'%unicode(veiculo),
        motorista=motorista.pessoa.nome if motorista else 'SEM MOTORISTA',
        placa = veiculo.veiculo.placa,
        equipe = veiculo.equipe.nome,
        orgao=veiculo.veiculo.orgao.nome_secretaria,
        sigla = veiculo.equipe.sigla,
        cronogramas=cronogramas,
        perfil=veiculo.perfil.nome,
        telefones = telefones,
        endereco = motorista.pessoa.endereco if motorista else '',
        data=data
    )
    template = webodt.ODFTemplate('modelo_notificacao.odt')
    document = template.render(Context(context))
    conv = converter()
    pdf = conv.convert(document, format='pdf')
    return HttpResponse(pdf, mimetype='application/pdf')


def relatorio_veiculos_alocados(request, id_equipe=None):

    if id_equipe:
        equipe = get_object_or_404(Equipe, pk=int(id_equipe))
    equipes = Equipe.objects.filter(eleicao=request.eleicao_atual).order_by('nome')
    Form = modelform_factory(
                VeiculoAlocado,
                fields=('equipe',),
                labels={'equipe':u'Selecionar Equipe: '})
    Form.base_fields['equipe'].queryset = equipes
    form = Form({'equipe':id_equipe})
    form.fields['equipe'].widget.attrs.update({'class':'form-control'})
    return render(request, 'veiculos/report/veiculos_alocados.html', locals())

def relatorio_veiculos_alocados_por_perfil(request, id_perfil=None):

    if id_perfil:
        perfil = get_object_or_404(PerfilVeiculo, pk=int(id_perfil))
        equipes = perfil.equipes.filter(eleicao = request.eleicao_atual).exclude(veiculoalocado=None).order_by('nome')
        veiculos = perfil.veiculoalocado_set.filter(veiculo__eleicao = request.eleicao_atual).order_by('veiculo__motorista_veiculo__pessoa__nome')
    perfis = PerfilVeiculo.objects.all().order_by('nome')
    Form = modelform_factory(
                VeiculoAlocado,
                fields=('perfil',),
                labels={u'perfil':u'Selecionar Função: '})
    Form.base_fields['perfil'].queryset = perfis
    form = Form({'perfil':id_perfil})
    form.fields['perfil'].widget.attrs.update({'class':'form-control'})
    return render(request, 'veiculos/report/veiculos_alocados_perfil.html', locals())

@login_required
@permission_required('veiculos.monitor_vistoria', raise_exception=True)
def frequencia_motoristas(request):
    if request.POST:
        formulario = FrequenciaForm(request.POST)
        dict_equipe = None
        data = None
        if formulario.is_valid():
            data = formulario.cleaned_data['data_frequencia']
            equipe = formulario.cleaned_data['equipe']
            equipe = Equipe.objects.filter(veiculoalocado__perfil__cronograma_perfil__dt_apresentacao__range=(data, data.replace(day=data.day+1)), id=equipe.id).select_related()

            if equipe:
                equipe = equipe.first()
                veiculos_alocados = equipe.veiculoalocado_set.filter(segundo_turno=True,perfil__cronograma_perfil__dt_apresentacao__range=(data, data.replace(day=data.day+1))).distinct()
                dict_equipe = {
                    'equipe': equipe,
                    'veiculos_equipe': veiculos_alocados.get_perfis_equipe(),
                    'locais': []
                }

                for local in equipe.local_equipe.all().order_by('local__nome'):
                    veiculos_alocados_local = veiculos_alocados.get_perfis_local().filter(segundo_turno=True, local_votacao=local)

                    if veiculos_alocados_local:
                        dict_equipe['locais'].append({'local': local,
                                                      'veiculos_local': veiculos_alocados_local})
        return render(request, 'veiculos/report/frequencia_motoristas.html', {'dict_equipe': dict_equipe, 'form': formulario, 'data': data})

    formulario = FrequenciaForm()
    return render(request, 'veiculos/report/frequencia_motoristas.html', {'form': formulario})

@login_required
@permission_required('eleicao.view_local_votacao', raise_exception=True)
def relatorio_motoristas_dia(request):
    formulario = RelatorioDiaForm()

    if request.POST:
        formulario = RelatorioDiaForm(request.POST)

        if formulario.is_valid():
            data = formulario.cleaned_data['data_frequencia']
            veiculos = VeiculoAlocado.objects.filter(segundo_turno=True).filter(perfil__cronograma_perfil__dt_apresentacao__range=(data, data.replace(day=data.day+1))).distinct().order_by('equipe__nome', 'veiculo__motorista_veiculo__pessoa__nome', 'local_votacao__local__nome').select_related()
            cabecalho = ['nome_motorista', 'titulo_eleitor', 'placa_veiculo', 'equipe', 'local', 'perfil', 'telefone_celular', 'telefone_residencial', ]
            dados = [cabecalho, ]

            for veiculoalocado in veiculos:
                motorista = veiculoalocado.get_motorista()
                dados_veiculo = [unicode(motorista.pessoa.nome.upper() if motorista else ''),
                                 unicode(motorista.pessoa.titulo_eleitoral if motorista else ''),
                                 unicode(veiculoalocado.veiculo.placa.upper()),
                                 unicode(veiculoalocado.equipe),
                                 unicode(veiculoalocado.local_votacao) if veiculoalocado.local_votacao else '',
                                 unicode(veiculoalocado.perfil),
                                 unicode(motorista.pessoa.tel_celular() if motorista else ''),
                                 unicode(motorista.pessoa.tel_residencial() if motorista else ''), ]
                if dados_veiculo not in dados:
                    dados.append(dados_veiculo)

            return ExcelResponse(dados, 'motoristas_do_dia')

    return render(request, 'veiculos/report/motoristas_por_dia.html', {'form': formulario})

def relatorio_veiculos_alocados_por_orgao(request, id_orgao=None):
    titulo_relatorio = u'Veiculos Alocados por Órgão'
    lista_orgaos = OrgaoPublico.objects.exclude(nome_secretaria__icontains='teste').order_by('nome_secretaria')
    if id_orgao:
        orgao = get_object_or_404(OrgaoPublico, pk=int(id_orgao))
        orgaos = [orgao,]
    else:
        orgaos = lista_orgaos
    count_veiculos = 0
    for o in orgaos:
        o.eleicao = request.eleicao_atual
        count_veiculos += o.get_veiculos_alocados().count()
    Form = modelform_factory(
                Veiculo,
                fields=('orgao',),
                labels={u'orgao':u'Selecionar Órgão: '})
    Form.base_fields['orgao'].queryset = lista_orgaos
    form = Form({'orgao':id_orgao})
    form.fields['orgao'].widget.attrs.update({'class':'form-control'})
    return render(request, 'veiculos/report/veiculos_alocados_orgao.html', locals())

def relatorio_veiculos_nao_alocados_orgao(request, id_orgao=None):
    titulo_relatorio = u'Veiculos requisitados não vistoriados'
    lista_orgaos = OrgaoPublico.objects.exclude(nome_secretaria__icontains='teste').order_by('nome_secretaria')
    if id_orgao:
        orgao = get_object_or_404(OrgaoPublico, pk=int(id_orgao))
        orgaos = [orgao,]
    else:
        orgaos = lista_orgaos
    count_veiculos = 0
    for o in orgaos:
        o.eleicao = request.eleicao_atual
        count_veiculos += o.get_veiculos_nao_alocados().count()
    Form = modelform_factory(
                Veiculo,
                fields=('orgao',),
                labels={u'orgao':u'Selecionar Órgão: '})
    Form.base_fields['orgao'].queryset = lista_orgaos
    form = Form({'orgao':id_orgao})
    form.fields['orgao'].widget.attrs.update({'class':'form-control'})
    return render(request, 'veiculos/report/veiculos_nao_alocados_orgao.html', locals())


def relatorio_declaracao_motorista(request, id_pessoa):
    pessoa = get_object_or_404(Pessoa, pk=int(id_pessoa))
    motoristas = pessoa.motorista_set.all().order_by('segundo_turno')
    lista_datas = []
    for motorista in motoristas:
        veiculo = motorista.get_veiculo_alocado()
        lista_datas += list(motorista.datas_trabalhadas())
    datas = len(lista_datas)<=2 and ' e '.join(map(lambda x:x.strftime('%d/%m/%Y'), lista_datas)) or len(lista_datas) > 0 and ' e '.join([', '.join(map(lambda x:x.strftime('%d/%m/%Y'), lista_datas[:-1])), lista_datas[-1].strftime('%d/%m/%Y')]) or ''
    context = dict(
        datas=datas,
        pessoa=pessoa,
        qtde_convocacao=len(lista_datas),
        hoje = datetime.date.today()
    )
    template = webodt.ODFTemplate('modelo_declaracao_motorista.odt')
    document = template.render(Context(context))
    conv = converter()
    pdf = conv.convert(document, format='pdf')
    return HttpResponse(pdf, mimetype='application/pdf')