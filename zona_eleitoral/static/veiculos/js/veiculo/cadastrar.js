$(document).ready(function(){
	var veiculo = new Veiculo();
	
	$.mask.definitions['Z'] = "[a-zA-Z]";
	$('#id_placa').mask('ZZZ-9999');
	$('#id_motorista_titulo_eleitoral').mask('999999999999');
	
	$('#form-motorista').hide();
	if($('#id_marca').val()=='') {
		$('#id_modelo').prop('disabled', true);
	} else {
		if($('#id_modelo').val()==''){
			
			$('#id_marca').trigger('change');
		}
	}
	
	$('#id_marca').change(function() {
		$('#id_modelo option:gt(0)').remove();
		if($(this).val()=='') {
			$('#id_modelo').prop('disabled', true);
			return;
		}
		veiculo.getModelos($(this).val(), $('#id_modelo'));
		$('#id_modelo').prop('disabled', false);
	});
	
	$('#id_cadastrar_motorista').change(function(){
		$(this).prop('checked') ? $('#form-motorista').show('fast') : $('#form-motorista').hide('fast'); 
	});
	
	$('#id_cadastrar_motorista').trigger('change');
});