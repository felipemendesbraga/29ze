from django.shortcuts import render
from django.http import HttpResponse
from models import LocalVotacao, Equipe
from excel_response import ExcelResponse

def relatorio_local_geral(request):
    locais = LocalVotacao.objects.filter(eleicao=request.eleicao_atual).order_by('local__nome').select_related()
    return render(request, 'eleicao/reports/local_geral.html', locals())

def relatorio_local_equipe(request):
    equipes = Equipe.objects.filter(eleicao=request.eleicao_atual).order_by('nome').select_related()
    return render(request, 'eleicao/reports/local_equipe.html', locals())

def relatorio_local_mala_direta(request):
    locais = LocalVotacao.objects.filter(eleicao=request.eleicao_atual).order_by('local__nome').select_related()
    cabecalho = ['equipe', 'num_local', 'nome_local', 'endereco', 'bairro', 'total_eleitores', 'secoes']
    data = [cabecalho,]
    max_secoes = 0
    for local in locais:
        equipe = local.equipe and local.equipe.nome or 'Sem equipe'
        num_local = local.local.id_local
        nome_local = local.local.nome
        endereco = local.local.endereco
        bairro = local.local.bairro
        total_eleitores = local.get_total_eleitores()
        secoes = local.get_secoes(delimitador='/')
        lista = [equipe, num_local, nome_local, endereco, bairro, total_eleitores, secoes]
        total_secoes = local.secao_set.secao_pai()
        for secao in total_secoes:
            lista.append(secao.unicode_agregadas(especial=False))
        data.append(lista)
        if len(total_secoes) > max_secoes:
            for i in range(1,len(total_secoes) + 1):
                if data[0].count('secao_' + str(i)) == 0:
                    data[0].append('secao_' + str(i))
            max_secoes = len(total_secoes)
            
    return ExcelResponse(data, 'locais_mala_direta')