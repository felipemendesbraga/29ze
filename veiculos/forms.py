# -*- coding: utf-8 -*-
'''
Created on 05/08/2014

@author: felipe
'''
import datetime
from acesso.models import OrgaoPublico
from django import forms
from django.utils import timezone
from eleicao.models import Equipe
from models import Veiculo
from core.models import Marca, Local, Pessoa
from selectable_select2.forms import Select2DependencyModelForm, Select2DependencyForm
from selectable_select2.widgets import AutoCompleteSelect2Widget
from veiculos.autocomplete import MotoristaLookup, EquipeLookup, PerfilChainedEquipeLookup, MarcaLookup, \
    ModeloChainedMarcaLookup, EquipeManualLookup, OrgaoLookup, LocalManualChainedEquipeManualLookup, \
    PerfilManualChainedLocalManualLookup
from veiculos.models import PerfilVeiculo, CronogramaVeiculo, Alocacao, Motorista, VeiculoAlocado


class VeiculoForm(forms.ModelForm):
    marca = forms.ModelChoiceField(queryset=Marca.objects.all().order_by('nome'))
    placa = forms.RegexField(r'[A-Za-z]{3}-\d{4}', max_length=8, help_text='Ex.:ABC-1234',
                             error_messages={'invalid': u'Insira uma placa válida.'})
    cadastrar_motorista = forms.BooleanField(initial=False, label='Cadastrar Motorista para o Veículo', required=False)
    
    class Meta:
        model = Veiculo
        fields = ['placa', 'marca', 'modelo', 'ano', 'tipo', 'lotacao', 'estado', 'observacao']
        widgets = {
            'observacao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(VeiculoForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['placa'].widget = forms.HiddenInput()
        for key in self.fields:
            if not isinstance(self.fields[key].widget, forms.CheckboxInput):
                self.fields[key].widget.attrs.update({'class': 'form-control'})
    
    def clean_placa(self):
        if not self.instance.pk and Veiculo.objects.filter(placa=self.cleaned_data.get('placa'), eleicao=self.instance.eleicao).exists():
            raise forms.ValidationError(u'O veículo com esta placa já está cadastrado')
        return self.cleaned_data.get('placa')


class SelecaoVeiculoForm(forms.Form):
    id_veiculo = forms.IntegerField(widget=forms.HiddenInput)
    primeiro_turno = forms.BooleanField(required=False)
    segundo_turno = forms.BooleanField(required=False)


class VeiculoVistoriaForm(Select2DependencyModelForm):
    # orgao = forms.ModelChoiceField(queryset=OrgaoPublico.objects.all().order_by('nome_secretaria'))
    placa = forms.RegexField(r'[A-Za-z]{3}-\d{4}', max_length=8, help_text='Ex.:ABC-1234',
                             error_messages={'invalid': u'Insira uma placa válida.'},
                             widget=forms.TextInput(attrs={'readonly': ''}))
    orgao = forms.ModelChoiceField(queryset=OrgaoLookup().get_queryset(),
                                   widget=AutoCompleteSelect2Widget(OrgaoLookup, placeholder=u"Selecione um órgão"),
                                   label=u'Órgão')
    marca = forms.ModelChoiceField(queryset=MarcaLookup().get_queryset(),
                                   widget=AutoCompleteSelect2Widget(MarcaLookup, placeholder="Selecione uma marca"),
                                   label='Marca')
    modelo = forms.ModelChoiceField(queryset=ModeloChainedMarcaLookup().get_queryset(),
                                    widget=AutoCompleteSelect2Widget(ModeloChainedMarcaLookup,
                                                                     placeholder="Selecione um modelo"),
                                    label='Modelo')

    select2_deps = (
        (
            'modelo', {'parents': ['marca']},
        ),
    )

    def __init__(self, *args, **kwargs):
        super(VeiculoVistoriaForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            if not isinstance(self.fields[key].widget, forms.CheckboxInput):
                self.fields[key].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Veiculo
        fields = ['placa', 'marca', 'modelo', 'ano', 'tipo', 'lotacao', 'estado', 'orgao', 'observacao']
        widgets = {
            'observacao': forms.Textarea(attrs={'rows': 3}),
        }


class MotoristaForm(forms.ModelForm):
    motorista_titulo_eleitoral = forms.RegexField(
        r'\d{12}',
        label=u'Título Eleitoral do Motorista',
        max_length=12,
        help_text=u'Entre 11 e 12 dígitos.'
    )
    
    class Meta:
        model = Veiculo
        fields = ['motorista_titulo_eleitoral', 'motorista_nome', 'endereco', 'tel_residencial', 'tel_celular']
        widgets = {
            'tel_residencial': forms.TextInput(attrs={'class': 'telefone'}),
            'tel_celular': forms.TextInput(attrs={'class': 'telefone'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(MotoristaForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            if not isinstance(self.fields[key].widget, forms.CheckboxInput):
                self.fields[key].widget.attrs.update({
                    'class': self.fields[key].widget.attrs.get('class') and
                             self.fields[key].widget.attrs.get('class') + ' form-control' or
                             'form-control'
                })
    

class PerfilVeiculoForm(forms.ModelForm):
    equipes = forms.ModelMultipleChoiceField(queryset=Equipe.objects.order_by('nome'))

    class Meta:
        model = PerfilVeiculo

    def __init__(self, *args, **kwargs):
        super(PerfilVeiculoForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            if not isinstance(self.fields[key].widget, forms.CheckboxInput):
                self.fields[key].widget.attrs.update({'class': 'form-control'})


# class CronogramaForm(forms.ModelForm):
#     local = forms.ModelChoiceField(
#         queryset=Local.objects.filter(localvotacao=None).order_by('id_local'),
#         empty_label=u'NO LOCAL DE TRABALHO',
#         required=False,
#         label=u'Local de apresentação'
#     )
#     data = forms.DateField(label='Data da apresentação')
#     hora = forms.TimeField(label='Horário de apresentação')
#     dia_montagem = forms.BooleanField(initial=False,required=False,label='Dia de montagem')
#
#     class Meta:
#         model = CronogramaVeiculo
#         fields= ('local', 'data', 'hora', 'dia_montagem', 'segundo_turno')
#
#     def __init__(self, data=None, instance=None, *args, **kwargs):
#         if instance:
#             if instance.pk and not data:
#                 data = {}
#                 default_timezone = timezone.get_default_timezone()
#                 value = timezone.make_aware(instance.dt_apresentacao, default_timezone)
#                 raise Exception(value)
#                 data.update({
#                     'data': '{:%d/%m/%Y}'.format(instance.dt_apresentacao),
#                     'hora': '{:%H:%M:%S}'.format(instance.dt_apresentacao),
#                     'local': instance.local,
#                     'dia_montagem': instance.dia_montagem,
#                     'segundo_turno': instance.segundo_turno
#                 })
#         super(CronogramaForm, self).__init__(data=data, instance=instance, *args, **kwargs)
#
#         for key in self.fields:
#             if (not isinstance(self.fields[key].widget, forms.CheckboxInput)) and (not isinstance(self.fields[key].widget, forms.SplitDateTimeWidget)):
#                 self.fields[key].widget.attrs.update({
#                     'class': ' '.join([i for i in ['form-control', self.fields[key].widget.attrs.get('class')] if i])
#                 })
#             if isinstance(self.fields[key].widget, forms.DateInput):
#
#                 self.fields[key].widget.attrs.update({
#                     'class': ' '.join([i for i in ['date', self.fields[key].widget.attrs.get('class')] if i])
#                 })
#
#             if isinstance(self.fields[key].widget, forms.TimeInput):
#                 self.fields[key].widget.attrs.update({
#                     'class': ' '.join([i for i in ['time', self.fields[key].widget.attrs.get('class')] if i])
#                 })
#
#     def clean_local(self):
#         if not self.cleaned_data.get('local'):
#             if self.instance.perfil.perfil_equipe:
#                 raise forms.ValidationError(u'O perfil está ligada à equipe, não possui local.')
#         return self.cleaned_data.get('local')

class CronogramaForm(forms.ModelForm):
    local = forms.ModelChoiceField(
        queryset=Local.objects.filter(localvotacao=None).order_by('id_local'),
        empty_label=u'NO LOCAL DE TRABALHO',
        required=False,
        label=u'Local de apresentação'
    )
    dt_apresentacao = forms.SplitDateTimeField(label=u'Data e Hora da Apresentação',widget=forms.SplitDateTimeWidget(attrs={'class': 'form-control'}))
    dia_montagem = forms.BooleanField(initial=False,required=False,label='Dia de montagem')

    class Meta:
        model = CronogramaVeiculo
        fields= ('local', 'dt_apresentacao', 'dia_montagem', 'segundo_turno')

    def __init__(self, data=None, instance=None, *args, **kwargs):

        super(CronogramaForm, self).__init__(data=data, instance=instance, *args, **kwargs)

        for key in self.fields:
            if (not isinstance(self.fields[key].widget, forms.CheckboxInput)) and (not isinstance(self.fields[key].widget, forms.SplitDateTimeWidget)):
                self.fields[key].widget.attrs.update({
                    'class': ' '.join([i for i in ['form-control', self.fields[key].widget.attrs.get('class')] if i])
                })
            if isinstance(self.fields[key].widget, forms.DateInput):

                self.fields[key].widget.attrs.update({
                    'class': ' '.join([i for i in ['date', self.fields[key].widget.attrs.get('class')] if i])
                })

            if isinstance(self.fields[key].widget, forms.TimeInput):
                self.fields[key].widget.attrs.update({
                    'class': ' '.join([i for i in ['time', self.fields[key].widget.attrs.get('class')] if i])
                })

    def clean_local(self):
        if not self.cleaned_data.get('local'):
            if self.instance.perfil.perfil_equipe:
                raise forms.ValidationError(u'O perfil está ligada à equipe, não possui local.')
        return self.cleaned_data.get('local')


class AlocacaoForm(forms.ModelForm):
    class Meta:
        model = Alocacao
        widgets = {
            'equipe': forms.HiddenInput,
            'local_votacao': forms.HiddenInput,
            'perfil_veiculo': forms.HiddenInput,
            'segundo_turno': forms.HiddenInput,
        }

    def __init__(self,  data=None, eleicao=None, *args, **kwargs):
        super(AlocacaoForm, self).__init__(data, *args, **kwargs)
        self.eleicao = eleicao
        for key in self.fields:
            if not isinstance(self.fields[key].widget, forms.CheckboxInput):
                self.fields[key].widget.attrs.update({'class': 'form-control'})

    def clean_quantidade(self):
        total_veiculos = Veiculo.objects.filter(eleicao=self.eleicao, veiculo_selecionado__segundo_turno=self.instance.segundo_turno).count()
        equipes = Equipe.objects.filter(eleicao=self.eleicao)
        veiculos_alocados = 0
        for equipe in equipes:
            veiculos_alocados += self.instance.segundo_turno and equipe.total_veiculos_estimados_turno2() or equipe.total_veiculos_estimados_turno1()
        if (veiculos_alocados + self.cleaned_data['quantidade']) - self.instance.quantidade > total_veiculos:
            raise forms.ValidationError(u'Quantidade de veiculos supera o número total de veículos requisitados')
        return self.cleaned_data['quantidade']


class VistoriaForm(Select2DependencyForm):
    alocacao = forms.ChoiceField(choices=[(0, u'Alocar por local'), (1, u'Alocar por equipe')], label=u'Alocação')
    equipe = forms.ModelChoiceField(queryset=EquipeLookup().get_queryset(),
                                    widget=AutoCompleteSelect2Widget(EquipeLookup,
                                                                     placeholder="Selecione uma equipe"),
                                    label='Equipe', required=False)
    perfil = forms.ModelChoiceField(queryset=PerfilChainedEquipeLookup().get_queryset(),
                                    widget=AutoCompleteSelect2Widget(PerfilChainedEquipeLookup,
                                                                     placeholder=u"Selecione uma função"),
                                    label=u'Função do Veículo', required=False)
    alocacao_manual = forms.BooleanField(label=u'Escolher equipe manualmente', required=False)
    alocacao_2_turno = forms.BooleanField(label=u'Alterar dados da alocação', required=False)
    equipe_manual = forms.ModelChoiceField(queryset=EquipeManualLookup().get_queryset(),
                                           widget=AutoCompleteSelect2Widget(EquipeManualLookup,
                                                                            placeholder="Selecione uma equipe"),
                                           label='Equipe', required=False)
    local_manual = forms.ModelChoiceField(queryset=LocalManualChainedEquipeManualLookup().get_queryset(),
                                          widget=AutoCompleteSelect2Widget(LocalManualChainedEquipeManualLookup,
                                                                           placeholder="Selecione um local"),
                                          label=u'Local de Votação', required=False)
    perfil_manual = forms.ModelChoiceField(queryset=PerfilManualChainedLocalManualLookup().get_queryset(),
                                           widget=AutoCompleteSelect2Widget(PerfilManualChainedLocalManualLookup,
                                                                            placeholder=u"Selecione uma função"),
                                           label=u'Função do Veículo', required=False)

    select2_deps = (
        (
            'perfil', {'parents': ['equipe']},
        ),
        (
            'local_manual', {'parents': ['equipe_manual']},
        ),
        (
            'perfil_manual', {'parents': ['local_manual']},
        ),
    )

    def __init__(self, *args, **kwargs):
        super(VistoriaForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            if not isinstance(self.fields[key].widget, forms.CheckboxInput):
                self.fields[key].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super(VistoriaForm, self).clean()
        alocacao = cleaned_data.get("alocacao")
        alocacao_manual = cleaned_data.get("alocacao_manual")
        equipe_manual = cleaned_data.get("equipe_manual")
        equipe = cleaned_data.get("equipe")
        perfil = cleaned_data.get("perfil")
        msg = u"Este campo é obrigatório para esse tipo de alocação"

        if alocacao == '1':
            if equipe is None:
                self._errors["equipe"] = self.error_class([msg])
                del cleaned_data["equipe"]
            if perfil is None:
                self._errors["perfil"] = self.error_class([msg])
                del cleaned_data["perfil"]
        else:
            if alocacao_manual and equipe_manual is None:
                self._errors["equipe_manual"] = self.error_class([msg])
                del cleaned_data["equipe_manual"]

        return cleaned_data


class MotoristaVistoriaForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    nome = forms.CharField(label=u'Nome do Motorista', max_length=100)
    titulo_eleitoral = forms.RegexField(r'^[0-9]{12}$', label=u'Título Eleitoral do Motorista',
                                        max_length=12, help_text=u'Entre 11 e 12 dígitos.')
    motorista = forms.ModelChoiceField(queryset=MotoristaLookup().get_queryset(),
                                       widget=AutoCompleteSelect2Widget(MotoristaLookup,
                                                                        placeholder="Selecione um motorista"),
                                       label='Motorista', required=False)

    class Meta:
        model = Pessoa

    def __init__(self, *args, **kwargs):
        super(MotoristaVistoriaForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            if not isinstance(self.fields[key].widget, forms.CheckboxInput):
                self.fields[key].widget.attrs.update({
                    'class': self.fields[key].widget.attrs.get('class') and
                             self.fields[key].widget.attrs.get('class') + ' form-control' or 'form-control'
                })


class FrequenciaForm(forms.ModelForm):
    data_frequencia = forms.DateField(label=u'Data da Frequência')

    class Meta:
        model = VeiculoAlocado
        fields = ['equipe', ]

    def __init__(self, *args, **kwargs):
        super(FrequenciaForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            if not isinstance(self.fields[key].widget, forms.CheckboxInput):
                self.fields[key].widget.attrs.update({
                    'class': self.fields[key].widget.attrs.get('class') and
                             self.fields[key].widget.attrs.get('class') + ' form-control' or 'form-control'
                })


class RelatorioDiaForm(forms.Form):
    data_frequencia = forms.DateField(label=u'Data')

    def __init__(self, *args, **kwargs):
        super(RelatorioDiaForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            if not isinstance(self.fields[key].widget, forms.CheckboxInput):
                self.fields[key].widget.attrs.update({
                    'class': self.fields[key].widget.attrs.get('class') and
                             self.fields[key].widget.attrs.get('class') + ' form-control' or 'form-control'
                })


class FaltasForm(forms.Form):
    motorista = forms.IntegerField(label=u'Motorista', widget=forms.HiddenInput())
    pessoa = forms.IntegerField(label=u'Pessoa', widget=forms.HiddenInput())
    cronograma = forms.IntegerField(label=u'Cronograma', widget=forms.HiddenInput())
    falta = forms.BooleanField(label=u'Falta', initial=False, required=False)

