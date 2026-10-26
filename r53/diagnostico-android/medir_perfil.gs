/**
 * Perfil das edições pelo gatilho simples (26/10/2026). Colar só numa CÓPIA de teste, como último arquivo do
 * projeto: ao carregar, embrulha as funções globais de salário, de cartão (r53*), da paleta e o onEdit, e cada uma
 * que passar de 0,3 s escreve no registro quando termina (o tempo inclui o das que ela chama). Escreve na hora,
 * então mesmo a execução que o Google corta aos 30 s deixa o rastro até onde chegou. Não pede autorização.
 */
var MEDIR_T0_ = Date.now();
(function () {
  Object.getOwnPropertyNames(globalThis).filter(function (n) {
    return /^(onEdit$|salario|r53|continuarPaleta_|convergirPaleta_)/.test(n) && typeof globalThis[n] === 'function' && !globalThis[n].__medido;
  }).forEach(function (n) {
    var f = globalThis[n], g = function () {
      var t = Date.now();
      try { return f.apply(this, arguments); }
      finally {
        var d = Date.now() - t;
        if (d >= 300 || n === 'onEdit') console.log('PERFIL ' + n + ': ' + d + ' ms · termina em ' + (Date.now() - MEDIR_T0_) + ' ms');
      }
    };
    g.__medido = true;
    globalThis[n] = g;
  });
})();
