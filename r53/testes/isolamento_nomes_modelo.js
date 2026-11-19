'use strict';
const {comparar}=require('./contagem_especiais_modelo');
if(!process.argv[2])throw Error('Informe fontes privadas da primeira PR88');
console.log(JSON.stringify(comparar(process.argv[2],require('../diagnostico-android/isolamento_nomes_plano.json'))));
