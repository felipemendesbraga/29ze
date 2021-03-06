#-*- coding: utf-8 -*-
from django import forms
from models import Eleicao, Equipe
from utils.forms import BootstrapModelForm, BootstrapForm
from eleicao.models import LocalVotacao
from veiculos.models import Alocacao


class EleicaoForm(BootstrapModelForm):
    
    class Meta:
        model = Eleicao
        exclude = ['eleitores','locais']


class LocalImportarForm(forms.Form):
    arquivo = forms.FileField(
                              help_text=u'Entre com o arquivo no formato CSV ou TXT. O arquivo deve conter 7 colunas, com o id do local, nome do local, endereco, bairro, numero da seção, tipo de seção (especial ou normal) e quantidade de pessoas na seção',
                              widget=forms.ClearableFileInput(attrs={'accept':'text/csv,text/plain'})
                              )
    
class LocalEquipeForm(forms.Form):
    equipe = forms.ChoiceField(required=False)
    
    def __init__(self, request, *args, **kwargs):
        super(LocalEquipeForm, self).__init__(*args, **kwargs)
        #self.fields['equipe'].widget.choices = [(u'', 'Sem equipe'),] + list(Equipe.objects.filter(eleicao=request.eleicao_atual).order_by('nome').values_list('pk', 'nome'))
        self.fields['equipe'].choices = [(u'', 'Sem equipe'),] + list(Equipe.objects.filter(eleicao=request.eleicao_atual).order_by('nome').values_list('pk', 'nome'))
        
class SecaoAgregarForm(forms.Form):
    pk_secao = forms.MultipleChoiceField(widget  = forms.CheckboxSelectMultiple)
    
class SecaoAgregarExternoForm(forms.Form):
    local = forms.ChoiceField(
                              choices = [('', 'Selecione o local'),],
                              widget = forms.Select(attrs={'class':'form-control'})
                              )
    secao = forms.ChoiceField(
                              choices = [('', u'Selecione a seção'),],
                              widget = forms.Select(attrs={'class':'form-control','disabled':'disabled'})
                              )
    
    def __init__(self, queryset = None, *args, **kwargs):
        super(SecaoAgregarExternoForm, self).__init__(*args, **kwargs)
        self.fields['local'].choices += list(queryset)
    
class EquipeForm(forms.ModelForm):
    
    class Meta:
        model = Equipe
        exclude = ['eleicao',]
        
class EquipeLocaisForm(forms.Form):
    local = forms.MultipleChoiceField()
    def __init__(self, queryset = None, *args, **kwargs):
        super(EquipeLocaisForm, self).__init__(*args, **kwargs)
        self.fields['local'].choices = list(queryset)

class EquipeAlocacaoForm(forms.ModelForm):
    class Meta:
        model = Alocacao
        widgets = {
            'perfil_veiculo' : forms.HiddenInput,
            'equipe' : forms.HiddenInput,
            'local_votacao' : forms.HiddenInput
        }

    def __init__(self, instance=None, *args, **kwargs):
        super(EquipeAlocacaoForm, self).__init__(instance=instance, *args, **kwargs)
        for key in self.fields:
            self.fields[key].widget.attrs.update({
                'class': ' '.join([i for i in ['form-control', self.fields[key].widget.attrs.get('class')] if i])
            })
        if instance:
            self.fields['quantidade'].label = instance.perfil_veiculo.nome

#EquipeAlocacaoFormSet = forms.inlineformset_factory(Equipe, Alocacao, form=EquipeAlocacaoForm, extra=0)