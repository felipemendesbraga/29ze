'''
Created on 05/08/2014

@author: felipe
'''
from django.conf.urls import include, url, patterns
from veiculos.views_relatorio import frequencia_motoristas, relatorio_motoristas_dia, \
    relatorio_veiculos_alocados_por_perfil, relatorio_veiculos_alocados_por_orgao, \
    relatorio_veiculos_nao_alocados_orgao, relatorio_declaracao_motorista
from veiculos.views_relatorio import relatorio_veiculos, relatorio_admin_orgao_sem_veiculo, \
    relatorio_veiculos_requisitados, relatorio_veiculo_alocado, relatorio_veiculos_alocados

from views import index, veiculo_index, veiculo_cadastrar, veiculo_editar, veiculo_ajax_get_modelo, info, \
    veiculo_vistoria_listagem
from veiculos.views import veiculo_excluir, veiculo_listar, veiculo_requisitar, veiculo_liberar, veiculo_detalhar, \
    perfil_veiculo_cadastrar, perfil_veiculo_listar, perfil_veiculo_editar, perfil_veiculo_detalhar, \
    cronograma_cadastrar, cronograma_editar, cronograma_excluir, alocacao_editar, veiculo_vistoria, index_vistoria, \
    monitorar_vistoria, lancar_faltas, motorista_listar


vistoria_veiculo_patterns = [
    url(r'^$', index_vistoria, name='index'),
    url(r'^cadastrar/$', veiculo_vistoria, name='cadastrar'),
    url(r'^cadastrar/(\d+)/$', veiculo_vistoria, name='cadastrar'),
    url(r'^listar/$', veiculo_vistoria_listagem, name='listar'),
    url(r'^listar/(\d+)/$', veiculo_vistoria_listagem, name='listar'),
    url(r'^monitorar/$', monitorar_vistoria, name='monitorar'),
]

veiculo_patterns = [
    url(r'^cadastrar/$', veiculo_cadastrar, name='cadastrar'),
    url(r'^editar/(\d+)/$', veiculo_editar, name='editar'),
    url(r'^get-modelos/(\d+)/$', veiculo_ajax_get_modelo, name='ajax_get_modelo'),
    url(r'^excluir/(\d+)/$', veiculo_excluir, name='excluir'),
    url(r'^listar/$', veiculo_listar, name='listar'),
    url(r'^listar/(\d+)/$', veiculo_listar, name='listar'),
    url(r'^detalhar/(\d+)/$', veiculo_detalhar, name='detalhar'),
    url(r'^requisitar/(\d+)/$', veiculo_requisitar, name='requisitar'),
    url(r'^liberar/(\d+)/$', veiculo_liberar, name='liberar'),
    url(r'^index/$', veiculo_index, name='index'),
    url(r'^vistoria/', include(vistoria_veiculo_patterns, namespace='vistoria')),
]

motorista_patterns = [
    url(r'^listar/$', motorista_listar, name='listar'),
]

perfil_veiculo_patterns = [
    url(r'^cadastrar/$', perfil_veiculo_cadastrar, name='cadastrar'),
    url(r'^editar/(\d+)/$', perfil_veiculo_editar, name='editar'),
    url(r'^excluir/(\d+)/$', veiculo_excluir, name='excluir'),
    url(r'^listar/$', perfil_veiculo_listar, name='listar'),
    url(r'^detalhar/(\d+)/$', perfil_veiculo_detalhar, name='detalhar'),
]

cronograma_veiculo_patterns = [
    url(r'^cadastrar/(\d+)/$', cronograma_cadastrar, name='cadastrar'),
    url(r'^editar/(\d+)/$', cronograma_editar, name='editar'),
    url(r'^excluir/(\d+)/$', cronograma_excluir, name='excluir'),
]

alocacao_patterns = [
    url(r'^editar/(True|False)/(\d+)/(\d+)/$', alocacao_editar, name='editar'),
    url(r'^editar/(True|False)/(\d+)/(\d+)/(\d+)/$', alocacao_editar, name='editar'),
]

report_patterns = [
    url(r'^veiculos/$', relatorio_veiculos, name='veiculos'),
    url(r'^orgaos-sem-veiculos/$', relatorio_admin_orgao_sem_veiculo, name='orgaos-sem-veiculos'),
    url(r'^veiculos-requisitados/$', relatorio_veiculos_requisitados, name='veiculos-requisitados'),
    url(r'^veiculos-requisitados/(\d+)/$', relatorio_veiculos_requisitados, name='veiculos-requisitados'),
    url(r'^veiculo-alocado/(\d+)/$', relatorio_veiculo_alocado, name='veiculo-alocado'),
    url(r'^veiculos-alocados/$', relatorio_veiculos_alocados, name='veiculos-alocados'),
    url(r'^veiculos-alocados/(\d+)/$', relatorio_veiculos_alocados, name='veiculos-alocados'),
    url(r'^veiculos-alocados-perfil/$', relatorio_veiculos_alocados_por_perfil, name='veiculos-alocados-perfil'),
    url(r'^veiculos-alocados-perfil/(\d+)/$', relatorio_veiculos_alocados_por_perfil, name='veiculos-alocados-perfil'),
    url(r'^frequencia-motoristas/$', frequencia_motoristas, name='frequencia'),
    url(r'^motoristas-dia/$', relatorio_motoristas_dia, name='motoristas-dia'),
    url(r'^veiculos-alocados-orgao/$', relatorio_veiculos_alocados_por_orgao, name='veiculos-alocados-orgao'),
    url(r'^veiculos-alocados-orgao/(\d+)/$', relatorio_veiculos_alocados_por_orgao, name='veiculos-alocados-orgao'),
    url(r'^veiculos-nao-alocados-orgao/$', relatorio_veiculos_nao_alocados_orgao, name='veiculos-nao-alocados-orgao'),
    url(r'^veiculos-nao-alocados-orgao/(\d+)/$', relatorio_veiculos_nao_alocados_orgao, name='veiculos-nao-alocados-orgao'),
    url(r'^declaracao-motorista/(\d+)/$', relatorio_declaracao_motorista, name='declaracao-motorista'),
]

urlpatterns = patterns('',
                       url(r'^index/$', index, name='veiculos_index'),
                       url(r'^info/$', info, name='veiculos_info'),
                       url(r'^veiculo/', include(veiculo_patterns, namespace='veiculo')),
                       url(r'^motorista/', include(motorista_patterns, namespace='motorista')),
                       url(r'^perfil-veiculo/', include(perfil_veiculo_patterns, namespace='perfil-veiculo')),
                       url(r'^cronograma/', include(cronograma_veiculo_patterns, namespace='cronograma-veiculo')),
                       url(r'^alocacao/', include(alocacao_patterns, namespace='alocacao-veiculo')),
                       url(r'^lancar-faltas/$', lancar_faltas, name='lancar-faltas'),
                       url(r'^report/', include(report_patterns, namespace='report-veiculos')),
)