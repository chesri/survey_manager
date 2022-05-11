define({
  "_widgetLabel": "Editor Inteligente",
  "_featureAction_SmartEditor": "Editor Inteligente",
  "noEditPrivileges": "Sua conta não tem permissão para criar ou modificar dados.",
  "loginPopupTitle": "Entrar",
  "loginPopupMessage": "${widgetName} exige permissões e créditos para pesquisar e armazenar informações de endereço. Você gostaria de entrar e usar este recurso?",
  "noCreditsOrPrivilegeWarningMessage": "Sua conta não tem as permissões e créditos para pesquisar e armazenar informações de endereço com${widgetName}. Entre em contato com o administrador da sua organização para solicitar permissões e créditos. Clique em OK para continuar a edição.",
  "unableToUseLocator": "O localizador não está acessível. As ações do atributo de endereço não serão executadas. Clique em OK para continuar a edição.",
  "locatorDisabledWaning": "O localizador não está habilitado. Entre em contato com o administrador da sua organização para solicitar esse recurso. Clique em OK para continuar a edição.",
  "noFeatureInAIWarning": "Nenhuma feição selecionada. Selecione uma feição para realizar as edições ou clique em cancelar para retornar à tela principal.",
  "noEditableLayerWarning": "Sua conta não tem permissão para criar ou modificar dados, ou este mapa da web não contém camadas editáveis.",
  "noVisibleCreateLayerWarning": "Camadas não visíveis no nível de zoom atual. Amplie ou reduza para criar/modificar feições.",
  "noVisibleUpdateLayerWarning": "Camadas não visíveis no nível de zoom atual. Amplie ou reduza para modificar feições.",
  "checkLayerVisibilityInWebMapWarning": "Certifique-se que as camadas estejam visíveis no mapa para criar ou modificar feições.",
  "showSelectionInAITitle": "Feições Selecionadas",
  "showSelectionInAIMsg": "Você deseja carregar a seleção atual no ${widgetName}?",
  "widgetActive": "Ativo",
  "widgetNotActive": "Inativo",
  "pressStr": "Pressione ",
  "ctrlStr": " CTRL ",
  "snapStr": " para habilitar o ajuste",
  "noAvailableTempaltes": "Nenhum modelo disponível",
  "editorCache": " - Cache de Editor",
  "presetFieldAlias": "Campo",
  "presetValue": "Valor Pré-Configurado",
  "usePresetValues": " Utilizar valores pré-configurados (novas feições somente)",
  "editGeometry": " Editar Geometria",
  "savePromptTitle": "Salvar feição",
  "savePrompt": "Gostaria de salvar a feição atual?",
  "deletePromptTitle": "Excluir feição",
  "deleteAttachment": "Excluir anexo",
  "deletePrompt": "Tem certeza que deseja excluir a feição selecionada?",
  "attachmentLoadingError": "Erro ao transferir anexos",
  "attachmentSaveDeleteWarning": "Aviso: As alterações dos anexos são salvas automaticamente",
  "autoSaveEdits": "Salvar novas feições automaticamente",
  "addNewFeature": "Criar nova feição",
  "featureCreationFailedMsg": "Não é possível criar um novo registro/feição",
  "relatedItemTitle": "Camada/Tabela Relacionada",
  "relatedFeatureCount": "${layerTitle} com ${featureCount} feições",
  "createNewFeatureLabel": "Criar nova feição para ${layerTitle}",
  "invalidRelationShipMsg": "Certifique-se que o campo de chave primária: '${parentKeyField}' tenha um valor válido",
  "pendingFeatureSaveMsg": "Salve as edições da feição antes de criar uma feição relacionada.",
  "attachmentsRequiredMsg": "(*) Anexos são exigidos.",
  "coordinatePopupTitle": "Mover feição para localização XY",
  "coordinatesSelectTitle": "Sistema de Coordenadas:",
  "mapSpecialReferenceDropdownOption": "Referência Espacial do Mapa",
  "latLongDropdownOption": "Latitude/Longitude",
  "mgrsDropdownOption": "Sistema de Referência da Grade Military (MGRS)",
  "mgrsTextBoxLabel": "Coordenada:",
  "xAttributeTextBoxLabel": "Coordenada-X:",
  "yAttributeTextBoxLabel": "Coordenada-Y:",
  "latitudeTextBoxLabel": "Latitude:",
  "longitudeTextBoxLabel": "Longitude:",
  "presetGroupFieldsLabel": "'${groupName}' será aplicado aos seguintes campos da camada:",
  "presetGroupNoFieldsLabel": "'${groupName}' não tem nenhum campo associado",
  "groupInfoLabel": "Agrupar informações para '${groupName}’",
  "editGroupInfoIcon": "Editar valor de grupo para ${groupName}",
  "filterEditor": {
    "all": "Todos",
    "noAvailableTempaltes": "Nenhum modelo disponível",
    "searchTemplates": "Pesquisar Modelos",
    "filterLayerLabel": "Filtrar camadas"
  },
  "invalidConfiguration": "O Widget não está configurado ou as camadas na configuração não estão mais no mapa.  Abra o aplicativo no modo do construtor e configure novamente o widget.",
  "geometryServiceURLNotFoundMSG": "Não foi possível obter URL do Serviço de Geometria",
  "clearSelection": "Fechar",
  "refreshAttributes": "Atualizar atributos de feições dinâmicas",
  "automaticAttributeUpdatesOn": "Atualizar automaticamente atributos da feição: ATIVADO",
  "automaticAttributeUpdatesOff": "Atualizar automaticamente atributos da feição: DESATIVADO",
  "moveSelectedFeatureToGPS": "Mover feição selecionada para a localização atual do GPS",
  "moveSelectedFeatureToXY": "Mover feição selecionada para localização XY",
  "mapNavigationLocked": "Navegação do Mapa: Bloqueada",
  "mapNavigationUnLocked": "Navegação do Mapa: Desbloqueada",
  "copyFeatures": {
    "title": "Selecionar feições para copiar",
    "createFeatures": "Criar Feições",
    "createSingleFeature": "Criar 1 Feição de Múltiplas Partes",
    "createOneSingleFeature": "Criar Feição",
    "noFeaturesSelectedMessage": "Nenhuma Feição Selecionada",
    "selectFeatureToCopyMessage": "Selecione feições para copiar",
    "multipleFeatureSaveWarning": "A criação de várias feições usando esta funcionalidade salvará todas as novas feições imediatamente. A correspondência de campo não é suportada ao criar uma nova feição de múltiplas partes.",
    "copyFeatureUpdateGeometryError": "Não é possível atualizar a geometria das feições selecionadas",
    "canNotSaveMultipleFeatureWarning": "Não é possível copiar várias feições usando o mesmo valor para campos de valor único, selecione apenas uma feição",
    "createOnlyOneMultipartFeatureWarning": "Apenas uma feição de múltiplas partes pode ser criada",
    "layerLabel": "${layerName} (${selectedFeatures}/${totalFeatures})",
    "layerAriaLabel": "${layerName} ${selectedFeatures} de ${totalFeatures} feições selecionadas"
  },
  "addingFeatureError": "Erro ao adicionar feições selecionadas na camada. Tente novamente.",
  "addingFeatureErrorCount": "Falha ao copiar as feições '${copyFeatureErrorCount}'. Deseja tentar novamente para as feições ausentes?",
  "selectingFeatureError": "Erro ao selecionar feições na camada. Tente novamente.",
  "customSelectOptionLabel": "Selecionar feições para copiar",
  "copyFeaturesWithPolygon": "Copiar por polígino",
  "copyFeaturesWithRect": "Copiar por retângulo",
  "copyFeaturesWithLasso": "Copiar por laço",
  "noFeatureSelectedMessage": "Nenhuma feição selecionada",
  "multipleFeatureSaveMessage": "Todas as feições serão salvas imediatamente. Você deseja prosseguir?",
  "relativeDates": {
    "dateTypeLabel": "Tipo de Data",
    "valueLabel": "Valor",
    "fixed": "Fixo",
    "current": "Atual",
    "past": "Passado",
    "future": "Futuro",
    "popupTitle": "Selecionar Valor",
    "hintForFixedDateType": "Dica: A data e hora especificadas serão utilizadas como valor padrão pré-definido.",
    "hintForCurrentDateType": "Dica: A data e hora atuais serão utilizadas como valor padrão pré-definido.",
    "hintForPastDateType": "Dica: O valor especificado será subtraído da data e hora atuais para o valor padrão da pré-definição.",
    "hintForFutureDateType": "Dica: O valor especificado será adicionado à data e hora atuais para o valor padrão da pré-definição.",
    "noDateDefinedTooltip": "Nenhuma data definida",
    "relativeDateWarning": "Um valor para data ou hora deve ser especificado para poder salvar o valor pré-definido padrão.",
    "customLabel": "Personalizada",
    "layerLabel": "Camada",
    "domainFieldHintLabel": "O valor selecionado é um domínio de valor codificado. O valor: \"${domainValue}\" será usado"
  },
  "valuePicker": {
    "popupTitle": "Selecionar Valor",
    "popupHint": "A feição atual está interseccionando com múltiplas feições. Escolha o valor para o respectivo campo",
    "buttonTooltip": "Selecione o valor de múltiplas feições de intersecção"
  },
  "uniqueValueErrorMessage": "O valor \"${fieldName}\" em \"\" já existe, forneça um novo valor.",
  "requiredFields": {
    "displayMsg": "Os campos obrigatórios não podem ficar em branco. Forneça valores para os campos comuns abaixo.",
    "popupTittle": "Campos obrigatórios",
    "foundNullRecordCount": "${fieldName} (Localizado em ${count} registros)"
  },
  "fieldsMapping": {
    "popupTittle": "Aplicar Correspondência de Campo",
    "fieldsMatchingCheckboxLabel": "Os valores das feições copiadas substituem os valores padrão no campo de destino",
    "resetLabel": "Redefinir",
    "clearLabel": "Limpar",
    "fieldsInTargetLayerLabel": "Destino",
    "fieldsInSourceLayerLabel": "Fonte",
    "targetFieldsMatchedLabel": "${layerName} (${matchedFields}/${totalFields} campos correspondidos)",
    "selectSourceFieldLabel": "- Selecionar -",
    "selectFieldAriaLabel": "Selecione campo de origem para campo de destino ${targetField}",
    "informativeText": "Revise os campos correspondentes da origem ao destino e personalize-os, se necessário.",
    "dynamicValueText": "Um valor dinâmico é configurado",
    "noFieldsToMatchLabel": "Nenhum campo para corresponder"
  },
  "cantLocateUserLocation": "Não foi possível determinar seu local",
  "tryAgainButtonLabel": "Tentar novamente",
  "copyFeatureFailedPopupTitle": "Oops!"
});