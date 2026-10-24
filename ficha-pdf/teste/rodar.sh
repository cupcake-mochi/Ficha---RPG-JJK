#!/usr/bin/env bash
# Abre as quatro fichas no pdf.js (o leitor do Firefox) com JavaScript ligado,
# preenche a Kaori do livro e confere 43 valores calculados.
# Precisa de node, playwright e acesso ao npm na primeira vez.
set -euo pipefail
cd "$(dirname "$0")"
[ -d node_modules/pdfjs-dist ] || npm install --no-save pdfjs-dist@4.10.38 >/dev/null
cp ../saidas/*.pdf .
python3 -m http.server 8765 >/dev/null 2>&1 & srv=$!
trap 'kill $srv; rm -f ./*.pdf' EXIT
sleep 1
for f in mizuki-claro mizuki-escuro eclipse-claro eclipse-escuro; do
  node teste.js "ficha-ciclo-maldito-$f.pdf"
done
